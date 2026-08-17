from __future__ import annotations

import base64
import bisect
import math
import re
from dataclasses import dataclass

from pyproj import CRS, Transformer
from shapely.geometry import Point, Polygon

from app.catalog_models import FixtureModelCatalog, IesFileRecord, IesLibrary
from app.models import (
    CalculationArea,
    LightingCalculationPoint,
    LightingCalculationResult,
    LightingFixtureProvenance,
    LightingStatistics,
    Project,
    utc_now,
)

MODEL_VERSION = "direct-horizontal-type-c-1.0.0"
BOUNDARY_TOLERANCE_M = 1e-7
MAX_CALCULATION_POINTS = 25_000
MAX_CONTRIBUTION_VALUES = 100_000
ASSUMPTIONS = [
    "Direct maintained horizontal illuminance only, calculated in the project-selected projected CRS in metres.",
    "IES Type C C0 is aligned with fixture azimuth; 0 degrees is project/grid north and positive rotation is clockwise.",
    "The photometric origin is the unchanged source-pole X/Y coordinate at configured mounting height; azimuth rotates distribution only.",
    "No physical luminaire tilt is applied. TILT=NONE is file metadata, while zero installed tilt is the approved Phase 4 assumption.",
    "No terrain, slope, buildings, occlusion, obstruction, shadowing, interreflection, reflected light, or atmospheric effects.",
    "Luminous-opening geometry is excluded from this far-field point-source model, including preserved negative source dimensions.",
    "No depreciation is applied beyond the calculation area's explicit maintenance factor.",
    "Results are not a standards-compliance determination.",
]


@dataclass(frozen=True)
class TypeCPhotometry:
    vertical_angles_deg: tuple[float, ...]
    horizontal_angles_deg: tuple[float, ...]
    candela_rows: tuple[tuple[float, ...], ...]
    candela_multiplier: float
    input_watts: float
    luminaire_identifier: str | None
    dimensions_raw: tuple[float, float, float]


@dataclass(frozen=True)
class EligibleFixture:
    pole_id: str
    origin_x_m: float
    origin_y_m: float
    origin_z_m: float
    azimuth_deg: float
    photometry: TypeCPhotometry
    provenance: LightingFixtureProvenance


def parse_type_c_photometry(record: IesFileRecord) -> TypeCPhotometry:
    if not record.active or record.validation_status != "valid":
        raise ValueError("IES record is not active and calculation-eligible")
    lines = base64.b64decode(record.original_content_base64, validate=True).decode("utf-8-sig").splitlines()
    tilt_index = next((index for index, line in enumerate(lines) if line.strip().upper().startswith("TILT=")), None)
    if tilt_index is None or lines[tilt_index].split("=", 1)[1].strip().upper() != "NONE":
        raise ValueError("Only TILT=NONE photometry is calculation-eligible")
    keywords: dict[str, str] = {}
    for line in lines[1:tilt_index]:
        match = re.match(r"\[([^]]+)]\s*(.*)", line.strip())
        if match:
            keywords[match.group(1).upper()] = match.group(2).strip()
    numbers = [float(token) for line in lines[tilt_index + 1 :] for token in line.split()]
    if len(numbers) < 13 or any(not math.isfinite(value) for value in numbers):
        raise ValueError("IES numeric payload is incomplete or non-finite")
    multiplier = numbers[2]
    vertical_count, horizontal_count = int(numbers[3]), int(numbers[4])
    if numbers[5] != 1 or multiplier <= 0:
        raise ValueError("Only valid Type C photometry with a positive candela multiplier is supported")
    dimensions = (numbers[7], numbers[8], numbers[9])
    input_watts = numbers[12]
    start = 13
    vertical = tuple(numbers[start : start + vertical_count])
    horizontal = tuple(numbers[start + vertical_count : start + vertical_count + horizontal_count])
    values = numbers[start + vertical_count + horizontal_count :]
    if len(vertical) != vertical_count or len(horizontal) != horizontal_count or len(values) != vertical_count * horizontal_count:
        raise ValueError("IES angle or candela array length mismatch")
    rows = tuple(tuple(values[row * vertical_count : (row + 1) * vertical_count]) for row in range(horizontal_count))
    return TypeCPhotometry(vertical, horizontal, rows, multiplier, input_watts, keywords.get("LUMINAIRE"), dimensions)


def _linear(values: tuple[float, ...], samples: tuple[float, ...], value: float) -> float:
    if value < samples[0] or value > samples[-1]:
        return 0.0
    right = bisect.bisect_right(samples, value)
    if right == 0:
        return values[0]
    if right >= len(samples):
        return values[-1]
    left = right - 1
    span = samples[right] - samples[left]
    fraction = 0.0 if span == 0 else (value - samples[left]) / span
    return values[left] + fraction * (values[right] - values[left])


def _canonical_c_angle(angle_deg: float, planes: tuple[float, ...]) -> float:
    angle = angle_deg % 360.0
    if len(planes) == 1:
        return planes[0]
    extent = planes[-1] - planes[0]
    if planes[0] == 0 and extent <= 90.0 + 1e-12:
        quadrant = angle % 180.0
        return min(quadrant, 180.0 - quadrant)
    if planes[0] == 0 and extent <= 180.0 + 1e-12:
        return angle if angle <= 180.0 else 360.0 - angle
    return angle


def interpolate_candela(photometry: TypeCPhotometry, vertical_deg: float, c_plane_deg: float) -> float:
    planes = photometry.horizontal_angles_deg
    c_angle = _canonical_c_angle(c_plane_deg, planes)
    vertical_values = tuple(_linear(row, photometry.vertical_angles_deg, vertical_deg) for row in photometry.candela_rows)
    if len(planes) == 1:
        return vertical_values[0] * photometry.candela_multiplier
    if planes[0] == 0 and planes[-1] == 360:
        c_angle %= 360.0
    intensity = _linear(vertical_values, planes, c_angle)
    return max(0.0, intensity * photometry.candela_multiplier)


def horizontal_illuminance_lux(fixture: EligibleFixture, point_x_m: float, point_y_m: float, plane_z_m: float) -> float:
    vertical_separation = fixture.origin_z_m - plane_z_m
    if vertical_separation <= 0:
        return 0.0
    dx, dy = point_x_m - fixture.origin_x_m, point_y_m - fixture.origin_y_m
    horizontal_distance = math.hypot(dx, dy)
    slant_distance = math.hypot(horizontal_distance, vertical_separation)
    vertical_angle = math.degrees(math.atan2(horizontal_distance, vertical_separation))
    world_azimuth = math.degrees(math.atan2(dx, dy)) % 360.0 if horizontal_distance else 0.0
    local_c_plane = (world_azimuth - fixture.azimuth_deg) % 360.0
    intensity_cd = interpolate_candela(fixture.photometry, vertical_angle, local_c_plane)
    incidence_cosine = vertical_separation / slant_distance
    return max(0.0, intensity_cd * incidence_cosine / (slant_distance * slant_distance))


def deterministic_grid(polygon: Polygon, spacing_m: float) -> list[tuple[float, float]]:
    min_x, min_y, max_x, max_y = polygon.bounds
    first_x, last_x = math.ceil(min_x / spacing_m), math.floor(max_x / spacing_m)
    first_y, last_y = math.ceil(min_y / spacing_m), math.floor(max_y / spacing_m)
    candidate_count = max(0, last_x - first_x + 1) * max(0, last_y - first_y + 1)
    if candidate_count > MAX_CALCULATION_POINTS * 20:
        raise ValueError(f"Requested grid has too many candidate points ({candidate_count:,}); maximum accepted result count is {MAX_CALCULATION_POINTS:,}. Increase spacing explicitly or reduce the area.")
    accepted: list[tuple[float, float]] = []
    accepted_region = polygon.buffer(BOUNDARY_TOLERANCE_M)
    for y_index in range(first_y, last_y + 1):
        y = y_index * spacing_m
        for x_index in range(first_x, last_x + 1):
            x = x_index * spacing_m
            if accepted_region.covers(Point(x, y)):
                accepted.append((x, y))
                if len(accepted) > MAX_CALCULATION_POINTS:
                    raise ValueError(f"Requested grid exceeds the {MAX_CALCULATION_POINTS:,}-point limit. Spacing was not changed and points were not dropped.")
    return accepted


def _eligible_fixtures(project: Project, area: CalculationArea, fixtures: FixtureModelCatalog, ies: IesLibrary, transformer: Transformer) -> tuple[list[EligibleFixture], list[str]]:
    warnings: list[str] = []
    eligible: list[EligibleFixture] = []
    source_by_id = {pole.id: pole for pole in project.source.poles}
    fixture_revisions = {(item.id, item.revision): item for item in [*fixtures.fixture_models, *fixtures.fixture_model_history]}
    fixture_current = {item.id: item for item in fixtures.fixture_models}
    ies_current = {item.id: item for item in ies.files}
    associations = {(item.ies_file_id, item.fixture_model_id) for item in ies.fixture_associations if item.active}
    for pole in project.source.poles:
        edit = project.pole_edits.get(pole.id)
        if edit is None or edit.active is False:
            continue
        config = edit.fixture_configuration
        if config is None:
            continue
        model = fixture_revisions.get((config.fixture_model_id, config.fixture_model_revision))
        current_model = fixture_current.get(config.fixture_model_id)
        prefix = f"{pole.id}:"
        reasons: list[str] = []
        if model is None or current_model is None or not current_model.active or not model.capabilities.lighting:
            reasons.append("fixture model/revision is missing, inactive, or not lighting-capable")
        if not config.ies_file_id:
            reasons.append("explicit compatible IES selection is required")
        record = ies_current.get(config.ies_file_id or "")
        if record is None or not record.active or record.validation_status != "valid":
            reasons.append("selected IES record is missing, inactive, invalid, or unsupported")
        if config.ies_file_id and (config.ies_file_id, config.fixture_model_id) not in associations:
            reasons.append("selected IES is not explicitly associated with the fixture model")
        if record is not None and config.ies_file_revision != record.revision:
            reasons.append("selected IES revision is not explicitly pinned to the active record revision")
        height = edit.height_m if edit.height_m is not None else project.defaults.pole_height_m
        if height is None or not math.isfinite(height) or height <= area.calculation_plane_elevation_m:
            reasons.append("valid mounting height above the calculation plane is required")
        if reasons:
            warnings.append(f"{prefix} excluded - {'; '.join(reasons)}.")
            continue
        photometry = parse_type_c_photometry(record)  # type: ignore[arg-type]
        origin_x, origin_y = transformer.transform(pole.longitude, pole.latitude)
        fixture_warnings = list(record.validation_warnings)  # type: ignore[union-attr]
        if photometry.input_watts == 50 and photometry.luminaire_identifier and "60W" in photometry.luminaire_identifier.upper():
            fixture_warnings.append("Controlling nominal input is 50 W; the preserved internal [LUMINAIRE] identifier says 60W.")
        if any(value < 0 for value in photometry.dimensions_raw):
            fixture_warnings.append("Negative luminous-opening dimensions are preserved raw and excluded from the Phase 4 far-field model.")
        provenance = LightingFixtureProvenance(
            pole_id=pole.id, fixture_model_id=config.fixture_model_id, fixture_model_revision=config.fixture_model_revision,
            ies_file_id=record.id, ies_file_revision=record.revision, ies_sha256=record.sha256,
            ies_original_filename=record.original_filename, mounting_height_m=height, fixture_azimuth_deg=config.fixture_azimuth_deg,
            origin_projected_m=(origin_x, origin_y, height), warnings=fixture_warnings,
        )
        eligible.append(EligibleFixture(pole.id, origin_x, origin_y, height, config.fixture_azimuth_deg, photometry, provenance))
    return eligible, warnings


def calculate_lighting_area(project: Project, area_id: str, fixtures: FixtureModelCatalog, ies: IesLibrary) -> LightingCalculationResult:
    area = next((item for item in project.calculation_areas if item.id == area_id), None)
    if area is None:
        raise ValueError("Calculation area was not found")
    if not project.projected_crs:
        raise ValueError("A project-selected projected CRS is required")
    crs = CRS.from_user_input(project.projected_crs)
    if not crs.is_projected or any(axis.unit_name.lower() not in {"metre", "meter"} for axis in crs.axis_info[:2]):
        raise ValueError("Lighting calculation requires a projected CRS with metre axes")
    to_projected = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    to_wgs84 = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    ring = [to_projected.transform(longitude, latitude) for longitude, latitude in area.wgs84_coordinates]
    polygon = Polygon(ring)
    if not polygon.is_valid or polygon.area <= 1e-8:
        raise ValueError("Calculation area is invalid or degenerate in the selected projected CRS")
    grid = deterministic_grid(polygon, area.grid_spacing_m)
    eligible, warnings = _eligible_fixtures(project, area, fixtures, ies, to_projected)
    fixture_warning_counts: dict[str, int] = {}
    for fixture in eligible:
        for warning in fixture.provenance.warnings:
            fixture_warning_counts[warning] = fixture_warning_counts.get(warning, 0) + 1
    warnings.extend(f"{count} contributing fixture(s): {warning}" for warning, count in sorted(fixture_warning_counts.items()))
    if not grid:
        warnings.append("The valid polygon produced zero calculation points on the requested anchored grid; no statistics were calculated.")
    if not eligible:
        warnings.append("No fixtures were calculation-eligible; point values, if present, are explicitly zero.")
    retain_contributions = len(grid) * len(eligible) <= MAX_CONTRIBUTION_VALUES
    if not retain_contributions and eligible:
        warnings.append("Per-fixture point contributions were omitted to keep the persisted payload safe; fixture provenance remains complete.")
    points: list[LightingCalculationPoint] = []
    for index, (x, y) in enumerate(grid):
        contributions = {fixture.pole_id: horizontal_illuminance_lux(fixture, x, y, area.calculation_plane_elevation_m) for fixture in eligible}
        maintained = math.fsum(contributions.values()) * area.maintenance_factor
        longitude, latitude = to_wgs84.transform(x, y)
        points.append(LightingCalculationPoint(
            id=f"{area.id}:r{area.calculation_state.polygon_revision}:{index:06d}", sequence_index=index,
            projected_coordinate_m=(x, y), wgs84_coordinate=(longitude, latitude),
            calculation_plane_elevation_m=area.calculation_plane_elevation_m,
            maintained_horizontal_illuminance_lux=maintained,
            per_fixture_contributions_lux=({key: value * area.maintenance_factor for key, value in contributions.items()} if retain_contributions else None),
        ))
    values = [point.maintained_horizontal_illuminance_lux for point in points]
    average = math.fsum(values) / len(values) if values else None
    minimum, maximum = (min(values), max(values)) if values else (None, None)
    statistics = LightingStatistics(
        point_count=len(points), grid_spacing_m=area.grid_spacing_m,
        average_illuminance_lux=average, minimum_illuminance_lux=minimum, maximum_illuminance_lux=maximum,
        emin_over_eavg=(minimum / average if minimum is not None and average is not None and average > 0 else None),
        emin_over_emax=(minimum / maximum if minimum is not None and maximum is not None and maximum > 0 else None),
    )
    result = LightingCalculationResult(
        calculation_area_id=area.id, calculation_area_name=area.name,
        calculated_at=utc_now(), polygon_revision=area.calculation_state.polygon_revision, projected_crs=project.projected_crs,
        points=points, statistics=statistics, contributing_fixture_count=len(eligible),
        fixture_provenance=[fixture.provenance for fixture in eligible], assumptions=ASSUMPTIONS,
        warnings=warnings,
    )
    area.calculation_state.status = "warning" if warnings else "calculated"
    area.calculation_state.last_calculated_at = result.calculated_at
    area.calculation_state.warnings = warnings
    area.calculation_state.assumptions = ASSUMPTIONS
    area.calculation_state.provenance = {
        "calculation_model_version": MODEL_VERSION, "projected_crs": project.projected_crs,
        "grid_origin_m": [0.0, 0.0], "grid_anchor_policy": result.grid_anchor_policy,
        "spacing_m": area.grid_spacing_m, "polygon_revision": area.calculation_state.polygon_revision,
        "boundary_policy": result.boundary_policy, "maintenance_factor": area.maintenance_factor,
    }
    return result
