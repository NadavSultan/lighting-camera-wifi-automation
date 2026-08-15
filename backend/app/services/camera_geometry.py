from __future__ import annotations

import math
from itertools import combinations

from pyproj import CRS, Transformer
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.ops import unary_union

from app.catalog_models import CameraEquipmentCatalog, CameraMountingSlot, FixtureModelCatalog, camera_absolute_azimuth
from app.models import (
    CameraFootprintResult,
    CameraGeometryLayer,
    CameraOverlapResult,
    PriorityAreaCoverageSummary,
    Project,
    utc_now,
)

GEOMETRY_MODEL_VERSION = "flat-ground-pinhole-1.0.0"
FIXED_MOUNT_CONTRACT = "fixed-zero-origin-1.0.0"
RAY_Z_TOLERANCE = 1e-10
AREA_TOLERANCE_M2 = 1e-8
ASSUMPTIONS = [
    "Project-selected local projected CRS in metres; WGS84 is display/interchange only.",
    "Flat horizontal local ground plane at Z=0; fixture height is optical-center height above ground.",
    "Symmetric rectilinear pinhole camera using catalog horizontal/vertical FOV; no lens distortion.",
    "No terrain, slope, buildings, trees, poles, occlusion, refraction, or site obstacles.",
    "Geometric footprint only; no facial recognition, LPR, people-counting, analytics, or compliance claim.",
]


def _signed_area(vertices: list[tuple[float, float]]) -> float:
    return 0.5 * sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(vertices, vertices[1:] + vertices[:1], strict=True))


def canonical_ring(vertices: list[tuple[float, float]], digits: int = 9) -> list[tuple[float, float]]:
    """Return a closed, CCW ring starting at its lexicographically smallest rounded vertex."""
    rounded = [(round(x, digits), round(y, digits)) for x, y in vertices]
    if _signed_area(rounded) < 0:
        rounded.reverse()
    start = min(range(len(rounded)), key=lambda index: rounded[index])
    ordered = rounded[start:] + rounded[:start]
    return [*ordered, ordered[0]]


def project_ground_footprint(
    origin_x_m: float,
    origin_y_m: float,
    height_m: float,
    absolute_azimuth_deg: float,
    downward_tilt_deg: float,
    horizontal_fov_deg: float,
    vertical_fov_deg: float,
) -> list[tuple[float, float]]:
    values = (origin_x_m, origin_y_m, height_m, absolute_azimuth_deg, downward_tilt_deg, horizontal_fov_deg, vertical_fov_deg)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("non-finite camera geometry input")
    if height_m <= 0 or not (0 < horizontal_fov_deg < 180) or not (0 < vertical_fov_deg < 180):
        raise ValueError("invalid height or camera field of view")
    azimuth = math.radians(absolute_azimuth_deg % 360.0)
    tilt = math.radians(downward_tilt_deg)
    half_h = math.tan(math.radians(horizontal_fov_deg) / 2)
    half_v = math.tan(math.radians(vertical_fov_deg) / 2)
    forward = (math.sin(azimuth) * math.cos(tilt), math.cos(azimuth) * math.cos(tilt), -math.sin(tilt))
    right = (math.cos(azimuth), -math.sin(azimuth), 0.0)
    image_up = (-math.sin(azimuth) * math.sin(tilt), -math.cos(azimuth) * math.sin(tilt), math.cos(tilt))
    vertices: list[tuple[float, float]] = []
    for horizontal_sign, vertical_sign in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        ray = tuple(forward[index] + horizontal_sign * half_h * right[index] + vertical_sign * half_v * image_up[index] for index in range(3))
        if not all(math.isfinite(value) for value in ray) or ray[2] >= -RAY_Z_TOLERANCE:
            raise ValueError("frustum boundary ray is horizontal, upward, or numerically unstable")
        distance = height_m / -ray[2]
        if not math.isfinite(distance) or distance <= 0:
            raise ValueError("frustum boundary ray does not intersect ground in front of camera")
        vertices.append((origin_x_m + distance * ray[0], origin_y_m + distance * ray[1]))
    ring = canonical_ring(vertices)
    polygon = Polygon(ring)
    if not polygon.is_valid or polygon.area <= AREA_TOLERANCE_M2:
        raise ValueError("camera footprint is invalid or degenerate")
    return ring


def _polygon_rings_wgs84(geometry, to_wgs84: Transformer) -> list[list[tuple[float, float]]]:
    polygons = list(geometry.geoms) if isinstance(geometry, MultiPolygon) else [geometry]
    result: list[list[tuple[float, float]]] = []
    for polygon in polygons:
        if not isinstance(polygon, Polygon) or polygon.is_empty:
            continue
        result.append([(round(lon, 10), round(lat, 10)) for lon, lat in (to_wgs84.transform(x, y) for x, y in polygon.exterior.coords)])
    return result


def calculate_camera_geometry(project: Project, fixtures: FixtureModelCatalog, cameras: CameraEquipmentCatalog) -> CameraGeometryLayer:
    layer = CameraGeometryLayer(calculated_at=utc_now(), projected_crs=project.projected_crs)
    fixture_revisions = {(item.id, item.revision): item for item in [*fixtures.fixture_models, *fixtures.fixture_model_history]}
    fixture_current = {item.id: item for item in fixtures.fixture_models}
    camera_revisions = {(item.id, item.revision): item for item in [*cameras.camera_models, *cameras.camera_model_history]}
    lens_revisions = {(item.id, item.revision): item for item in [*cameras.lenses, *cameras.lens_history]}
    if not project.projected_crs:
        return layer
    crs = CRS.from_user_input(project.projected_crs)
    if not crs.is_projected or any(axis.unit_name.lower() not in {"metre", "meter"} for axis in crs.axis_info[:2]):
        return layer
    to_projected = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    to_wgs84 = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    source_by_id = {pole.id: pole for pole in project.source.poles}
    polygon_by_id: dict[str, Polygon] = {}

    for pole_id, edit in project.pole_edits.items():
        config = edit.fixture_configuration
        if config is None or edit.fixture_type is None or edit.fixture_type.value != "SMART":
            continue
        model = fixture_revisions.get((config.fixture_model_id, config.fixture_model_revision))
        reference_model = model or fixture_current.get(config.fixture_model_id)
        template = next((item for item in model.mounting_template_revisions if item.revision == config.mounting_template_revision), None) if model else None
        reference_template = template or (reference_model.current_template() if reference_model else None)
        if reference_model is None or not reference_model.capabilities.cameras or reference_template is None:
            continue
        source = source_by_id[pole_id]
        origin_x, origin_y = to_projected.transform(source.longitude, source.latitude)
        for slot in reference_template.slots:
            override = config.camera_overrides.get(slot.id)
            camera_id = override.camera_model_id if override and override.camera_model_id is not None else slot.camera_model_id
            camera_revision = override.camera_model_revision if override and override.camera_model_id is not None else slot.camera_model_revision
            lens_id = override.lens_id if override and override.lens_id is not None else slot.lens_id
            lens_revision = override.lens_revision if override and override.lens_id is not None else slot.lens_revision
            enabled = override.enabled if override and override.enabled is not None else slot.enabled
            absolute = camera_absolute_azimuth(config.fixture_azimuth_deg, slot.relative_azimuth_deg)
            result = CameraFootprintResult(
                pole_id=pole_id, fixture_model_id=config.fixture_model_id, fixture_model_revision=config.fixture_model_revision,
                mounting_template_revision=config.mounting_template_revision or reference_template.revision, camera_slot_id=slot.id,
                camera_model_id=camera_id, camera_model_revision=camera_revision, lens_id=lens_id, lens_revision=lens_revision,
                fixture_height_m=edit.height_m if edit.height_m is not None else project.defaults.pole_height_m,
                fixture_azimuth_deg=config.fixture_azimuth_deg, template_relative_azimuth_deg=slot.relative_azimuth_deg,
                fixed_downward_tilt_deg=slot.downward_tilt_deg, camera_absolute_azimuth_deg=absolute,
                enabled=enabled, valid=False, projected_crs=project.projected_crs, assumptions=ASSUMPTIONS,
            )
            if not enabled:
                layer.footprints.append(result)
                continue
            camera = camera_revisions.get((camera_id, camera_revision)) if camera_id and camera_revision else None
            lens = lens_revisions.get((lens_id, lens_revision)) if lens_id and lens_revision else None
            if model is None:
                result.warnings.append("Pinned fixture model revision does not exist.")
            if template is None:
                result.warnings.append("Pinned mounting template revision does not exist.")
            if reference_template.geometry_contract_version != FIXED_MOUNT_CONTRACT:
                result.warnings.append("Pinned mounting template predates the approved fixed-mount contract; explicitly adopt/reset to the current template.")
            if override and (override.relative_azimuth_deg is not None or override.downward_tilt_deg is not None):
                result.warnings.append("Legacy per-pole camera orientation override is preserved but unsupported; explicitly reset this slot to the immutable template.")
            if result.fixture_height_m is None:
                result.warnings.append("Fixture/pole height is required.")
            if camera is None:
                result.warnings.append("A pinned camera model and revision are required.")
            if lens is None:
                result.warnings.append("An explicit compatible pinned lens and revision are required; no default lens is assigned.")
            if camera and lens and camera.id not in lens.compatible_camera_model_ids:
                result.warnings.append("Selected camera and lens revisions are incompatible.")
            if lens and (lens.horizontal_fov_deg is None or lens.vertical_fov_deg is None):
                result.warnings.append("Pinned lens revision lacks catalog horizontal/vertical FOV.")
            if (slot.origin_offset_x_m, slot.origin_offset_y_m, slot.origin_offset_z_m) != (0, 0, 0):
                result.warnings.append("Mounting template does not use the approved zero XYZ optical-center offsets.")
            if result.warnings:
                layer.footprints.append(result)
                continue
            try:
                ring = project_ground_footprint(origin_x, origin_y, result.fixture_height_m, absolute, slot.downward_tilt_deg, lens.horizontal_fov_deg, lens.vertical_fov_deg)  # type: ignore[arg-type]
            except ValueError as exc:
                result.warnings.append(str(exc))
                layer.footprints.append(result)
                continue
            polygon = Polygon(ring)
            result.projected_coordinates_m = ring
            result.wgs84_coordinates = [(round(lon, 10), round(lat, 10)) for lon, lat in (to_wgs84.transform(x, y) for x, y in ring)]
            result.footprint_area_m2 = round(polygon.area, 6)
            result.valid = True
            footprint_id = f"{pole_id}/{slot.id}"
            polygon_by_id[footprint_id] = polygon
            layer.footprints.append(result)

    for (id_a, polygon_a), (id_b, polygon_b) in combinations(polygon_by_id.items(), 2):
        intersection = polygon_a.intersection(polygon_b)
        if intersection.area > AREA_TOLERANCE_M2:
            layer.overlaps.append(CameraOverlapResult(footprint_a=id_a, footprint_b=id_b, intersection_area_m2=round(intersection.area, 6), wgs84_coordinates=_polygon_rings_wgs84(intersection, to_wgs84)))

    all_footprints = list(polygon_by_id.items())
    for area in project.priority_areas:
        projected_ring = [to_projected.transform(lon, lat) for lon, lat in area.wgs84_coordinates]
        priority_polygon = Polygon(projected_ring)
        if not priority_polygon.is_valid or priority_polygon.area <= AREA_TOLERANCE_M2:
            layer.priority_area_summaries.append(PriorityAreaCoverageSummary(
                priority_area_id=area.id, priority_area_name=area.name, area_m2=0, covered_area_m2=0,
                covered_percentage=0, intersecting_footprint_ids=[], warnings=["Priority-area polygon is invalid or degenerate in the projected CRS; no intersection was calculated."],
            ))
            continue
        intersecting = [(footprint_id, polygon.intersection(priority_polygon)) for footprint_id, polygon in all_footprints if polygon.intersects(priority_polygon)]
        parts = [geometry for _, geometry in intersecting if not geometry.is_empty]
        covered = unary_union(parts).area if parts else 0.0
        layer.priority_area_summaries.append(PriorityAreaCoverageSummary(
            priority_area_id=area.id, priority_area_name=area.name, area_m2=round(priority_polygon.area, 6),
            covered_area_m2=round(covered, 6), covered_percentage=round(100 * covered / priority_polygon.area, 6),
            intersecting_footprint_ids=[footprint_id for footprint_id, geometry in intersecting if not geometry.is_empty],
        ))
    return layer
