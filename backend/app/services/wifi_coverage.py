from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from typing import Any

from pyproj.exceptions import ProjError
from shapely.geometry import GeometryCollection, Point, Polygon
from shapely.strtree import STRtree
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from app.catalog_models import FixtureModelCatalog
from app.crs import project_transformers, validate_projected_metre_crs
from app.models import (
    FixtureType,
    MAX_WIFI_ANALYSIS_AREAS,
    MAX_WIFI_CANDIDATE_OPERATIONS,
    MAX_WIFI_CIRCLE_VERTICES,
    MAX_WIFI_CIRCLES,
    MAX_WIFI_TOTAL_GEOMETRY_VERTICES,
    WIFI_INTERSECTION_TOLERANCE_M2,
    WIFI_MODEL_VERSION,
    WifiAnalysisAreaStatistics,
    WifiCircle,
    WifiCoverageResult,
    WifiGlobalStatistics,
    Project,
    utc_now,
)

ASSUMPTIONS = [
    "Each enabled Wi-Fi circle is a Euclidean projected-plane buffer around an existing pole.",
    "The 30 m project default and per-pole radii are engineering assumptions, not coverage guarantees.",
    "Circle geometry is independent of height, terrain, obstacles, antennas, bands, EIRP, sensitivity, capacity, and propagation effects.",
]
DISCLAIMER = "Conceptual geometric visualization only; not verified RF coverage, performance, capacity, service quality, or standards compliance."


def _round(value: float, places: int) -> float:
    if not math.isfinite(value):
        raise ValueError("Wi-Fi geometry contains a non-finite value")
    return round(float(value), places)


def _canonical_ring(geometry: Polygon, places: int) -> list[tuple[float, float]]:
    if geometry.is_empty or not geometry.is_valid or geometry.area <= 1e-8:
        raise ValueError("Wi-Fi circle geometry is empty, invalid, or degenerate")
    ring = list(orient(geometry, sign=1.0).exterior.coords)[:-1]
    rounded = [(_round(x, places), _round(y, places)) for x, y in ring]
    start = min(range(len(rounded)), key=lambda i: rounded[i])
    rotated = rounded[start:] + rounded[:start]
    return rotated + [rotated[0]]


def wifi_calculation_input_sha256(project: Project) -> str:
    poles: list[dict[str, Any]] = []
    for source in sorted(project.source.poles, key=lambda item: (item.sequence_index, item.id)):
        edit = project.pole_edits.get(source.id)
        config = edit.fixture_configuration if edit else None
        wifi = config.wifi_configuration if config else None
        effective_type = (edit.fixture_type if edit and edit.fixture_type else project.defaults.fixture_type).value
        effective_coordinate = [edit.longitude, edit.latitude] if edit and edit.longitude is not None else [source.longitude, source.latitude]
        poles.append({
            "id": source.id, "sequence_index": source.sequence_index,
            "source_coordinate": [source.longitude, source.latitude],
            "effective_coordinate": effective_coordinate,
            "fixture_type": effective_type,
            "active": edit.active if edit and edit.active is not None else True,
            "fixture_model_id": config.fixture_model_id if config else None,
            "fixture_model_revision": config.fixture_model_revision if config else None,
            "radius": wifi.radius_override_m if wifi and wifi.radius_override_m is not None else project.defaults.wifi_radius_m,
            "enabled": wifi.enabled if wifi and wifi.enabled is not None else True,
        })
    payload = {
        "model_version": WIFI_MODEL_VERSION, "resolution": 32,
        "projected_crs": project.projected_crs, "source_crs": project.source_crs,
        "default_radius": project.defaults.wifi_radius_m, "poles": poles,
        "analysis_areas": [area.model_dump(mode="json") for area in project.wifi_analysis_areas],
        "candidate_operation_cap": MAX_WIFI_CANDIDATE_OPERATIONS,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(canonical).hexdigest()


def invalidate_stale_wifi_results(project: Project) -> bool:
    layer = project.wifi_coverage
    if layer.result is None:
        return False
    fingerprint = wifi_calculation_input_sha256(project)
    if layer.result.calculation_input_sha256 == fingerprint:
        return False
    layer.result = None
    layer.state.status = "not-calculated"
    layer.state.last_calculated_at = None
    layer.state.calculation_input_sha256 = None
    layer.state.provenance = {}
    layer.state.warnings = []
    return True


def _effective_pole(project: Project, pole_id: str):
    source = next(pole for pole in project.source.poles if pole.id == pole_id)
    edit = project.pole_edits.get(pole_id)
    config = edit.fixture_configuration if edit else None
    fixture_type = edit.fixture_type if edit and edit.fixture_type else project.defaults.fixture_type
    active = edit.active if edit and edit.active is not None else True
    coordinate = (edit.longitude, edit.latitude) if edit and edit.longitude is not None and edit.latitude is not None else (source.longitude, source.latitude)
    wifi = config.wifi_configuration if config else None
    radius = wifi.radius_override_m if wifi and wifi.radius_override_m is not None else project.defaults.wifi_radius_m
    enabled = wifi.enabled if wifi and wifi.enabled is not None else True
    return source, edit, config, fixture_type, active, coordinate, radius, enabled


def _projected_area(project: Project, area):
    if not project.projected_crs:
        raise ValueError("A project-selected projected CRS is required for Wi-Fi geometry")
    crs = validate_projected_metre_crs(project.projected_crs)
    to_projected, _ = project_transformers(crs)
    try:
        ring = [to_projected.transform(lon, lat) for lon, lat in area.wgs84_coordinates]
    except ProjError as exc:
        raise ValueError(f"Wi-Fi analysis area {area.id} could not be transformed to the projected CRS") from exc
    if not all(math.isfinite(v) for xy in ring for v in xy):
        raise ValueError(f"Wi-Fi analysis area {area.id} transformed to non-finite coordinates")
    polygon = Polygon(ring)
    if not polygon.is_valid or polygon.area <= 1e-8:
        raise ValueError(f"Wi-Fi analysis area {area.id} is invalid or degenerate in the selected projected CRS")
    return polygon, to_projected


def calculate_wifi_coverage(project: Project, fixtures: FixtureModelCatalog) -> WifiCoverageResult:
    if not project.projected_crs:
        raise ValueError("A project-selected projected CRS is required for Wi-Fi geometry")
    if len(project.wifi_analysis_areas) > MAX_WIFI_ANALYSIS_AREAS:
        raise ValueError(f"Wi-Fi analysis areas exceed the {MAX_WIFI_ANALYSIS_AREAS:,}-area limit")
    if sum(len(area.wgs84_coordinates) for area in project.wifi_analysis_areas) + MAX_WIFI_CIRCLE_VERTICES > MAX_WIFI_TOTAL_GEOMETRY_VERTICES:
        raise ValueError(f"Wi-Fi persisted geometry exceeds the {MAX_WIFI_TOTAL_GEOMETRY_VERTICES:,}-vertex limit")
    crs = validate_projected_metre_crs(project.projected_crs)
    to_projected, to_wgs84 = project_transformers(crs)
    models = {(model.id, model.revision): model for model in [*fixtures.fixture_models, *fixtures.fixture_model_history]}
    current_models = {model.id: model for model in fixtures.fixture_models}
    circles: list[WifiCircle] = []
    exact_geometries: list[Polygon] = []
    warnings: list[str] = []
    for pole in sorted(project.source.poles, key=lambda item: (item.sequence_index, item.id)):
        source, edit, config, fixture_type, active, coordinate, radius, enabled = _effective_pole(project, pole.id)
        if not math.isfinite(radius) or radius <= 0 or radius > 1000:
            raise ValueError(f"{pole.id}: Wi-Fi radius must be finite and greater than 0 and at most 1000 m")
        if fixture_type is FixtureType.LITE:
            continue
        capability = True
        model_warning = None
        if config:
            model = models.get((config.fixture_model_id, config.fixture_model_revision))
            current = current_models.get(config.fixture_model_id)
            capability = bool(model and current and current.active and model.capabilities.wifi)
            if model and model.capability_variant is not fixture_type:
                capability = False
                model_warning = "fixture type/model capability conflict"
            elif not capability:
                model_warning = "assigned fixture model is missing, inactive, or not Wi-Fi-capable"
        if not capability:
            warnings.append(f"{pole.id}: excluded - {model_warning}.")
            continue
        if not active:
            warnings.append(f"{pole.id}: excluded - pole is inactive.")
            continue
        if not enabled:
            continue
        try:
            x, y = to_projected.transform(*coordinate)
        except ProjError as exc:
            raise ValueError(f"{pole.id}: Wi-Fi coordinate transformation failed") from exc
        if not all(math.isfinite(v) for v in (x, y)):
            raise ValueError(f"{pole.id}: Wi-Fi projected center is non-finite")
        circle_geometry = Point(x, y).buffer(radius, quad_segs=32)
        exact_geometries.append(circle_geometry)
        projected_ring = _canonical_ring(circle_geometry, 9)
        display_ring = []
        for px, py in projected_ring[:-1]:
            lon, lat = to_wgs84.transform(px, py)
            display_ring.append((_round(lon, 10), _round(lat, 10)))
        display_ring.append(display_ring[0])
        circles.append(WifiCircle(
            id=f"wifi-circle/{pole.id}", pole_id=pole.id, effective_fixture_type=fixture_type,
            center_projected_m=(_round(x, 9), _round(y, 9)),
            source_wgs84_coordinate=(source.longitude, source.latitude),
            effective_wgs84_coordinate=(coordinate[0], coordinate[1]),
            projected_ring=projected_ring, wgs84_ring=display_ring,
            effective_radius_m=radius, enabled=True, eligible=True,
            area_m2=_round(circle_geometry.area, 6), approximation_resolution=32,
            source_provenance={"source_coordinate": [source.longitude, source.latitude], "effective_coordinate": list(coordinate), "source_sequence_index": source.sequence_index},
        ))
        if len(circles) > MAX_WIFI_CIRCLES:
            raise ValueError(f"Wi-Fi eligible circles exceed the {MAX_WIFI_CIRCLES:,}-circle limit")
    if len(circles) * 129 > MAX_WIFI_CIRCLE_VERTICES:
        raise ValueError(f"Wi-Fi circle vertices exceed the {MAX_WIFI_CIRCLE_VERTICES:,}-vertex limit")
    geometries = exact_geometries
    union = unary_union(geometries) if geometries else GeometryCollection()
    tree = STRtree(geometries) if geometries else None
    candidates: set[tuple[int, int]] = set()
    if tree:
        for index, geometry in enumerate(geometries):
            for match in tree.query(geometry):
                other = int(match) if hasattr(match, "__index__") else geometries.index(match)
                if index < other:
                    candidates.add((index, other))
    if len(candidates) > MAX_WIFI_CANDIDATE_OPERATIONS:
        raise ValueError(f"Wi-Fi candidate pair/intersection operations exceed the {MAX_WIFI_CANDIDATE_OPERATIONS:,} limit")
    pairwise = 0.0
    overlap_geometries = []
    overlap_count = 0
    for first, second in sorted(candidates, key=lambda pair: (circles[pair[0]].id, circles[pair[1]].id)):
        intersection = geometries[first].intersection(geometries[second])
        area = intersection.area
        if area > WIFI_INTERSECTION_TOLERANCE_M2:
            pairwise += area
            overlap_geometries.append(intersection)
            overlap_count += 1
    multiply_union = unary_union(overlap_geometries) if overlap_geometries else GeometryCollection()
    individual = math.fsum(circle.area_m2 for circle in circles)
    union_area = union.area if not union.is_empty else 0.0
    global_stats = WifiGlobalStatistics(
        circle_count=len(circles), individual_area_m2=_round(individual, 6),
        union_covered_area_m2=_round(union_area, 6), overlap_area_m2=_round(max(0.0, individual - union_area), 6),
        pairwise_overlap_area_m2=_round(pairwise, 6), multiply_covered_union_area_m2=_round(multiply_union.area if not multiply_union.is_empty else 0.0, 6),
        overlap_pair_count=overlap_count,
        union_over_individual_percentage=_round(100 * union_area / individual, 6) if individual > 0 else None,
    )
    area_stats: list[WifiAnalysisAreaStatistics] = []
    for area in project.wifi_analysis_areas:
        polygon, _ = _projected_area(project, area)
        covered = polygon.intersection(union).area if not union.is_empty else 0.0
        uncovered = polygon.difference(union).area if not union.is_empty else polygon.area
        boundary_length = polygon.boundary.length
        boundary_covered = polygon.boundary.intersection(union).length if not union.is_empty else 0.0
        area_stats.append(WifiAnalysisAreaStatistics(
            analysis_area_id=area.id, analysis_area_name=area.name, area_m2=_round(polygon.area, 6),
            covered_area_m2=_round(covered, 6), uncovered_area_m2=_round(uncovered, 6),
            covered_percentage=_round(100 * covered / polygon.area, 6), uncovered_percentage=_round(100 * uncovered / polygon.area, 6),
            boundary_covered_length_m=_round(boundary_covered, 6), boundary_covered_percentage=_round(100 * boundary_covered / boundary_length, 6) if boundary_length > 0 else 0.0,
        ))
    fingerprint = wifi_calculation_input_sha256(project)
    return WifiCoverageResult(
        projected_crs=project.projected_crs, circles=circles, global_statistics=global_stats,
        analysis_area_statistics=area_stats, calculation_input_sha256=fingerprint,
        calculated_at=utc_now(), warnings=warnings, assumptions=ASSUMPTIONS,
    )


def apply_wifi_result(project: Project, result: WifiCoverageResult) -> Project:
    updated = deepcopy(project)
    updated.wifi_coverage.result = result
    updated.wifi_coverage.state.status = "warning" if result.warnings else "calculated"
    updated.wifi_coverage.state.last_calculated_at = result.calculated_at
    updated.wifi_coverage.state.warnings = result.warnings
    updated.wifi_coverage.state.assumptions = result.assumptions
    updated.wifi_coverage.state.calculation_input_sha256 = result.calculation_input_sha256
    updated.wifi_coverage.state.provenance = {"projected_crs": result.projected_crs, "approximation_resolution": 32, "disclaimer": DISCLAIMER}
    return updated
