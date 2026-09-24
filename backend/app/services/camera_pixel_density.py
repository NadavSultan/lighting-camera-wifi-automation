from __future__ import annotations

import math
import hashlib
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Sequence

from pyproj import Transformer
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import polygonize, unary_union
from shapely.strtree import STRtree

from app.catalog_models import (
    CameraEquipmentCatalog,
    CameraModel,
    CameraMountingSlot,
    CameraMountingTemplateRevision,
    FixtureModel,
    FixtureModelCatalog,
    LensConfiguration,
    camera_absolute_azimuth,
)
from app.crs import project_transformers, validate_projected_metre_crs
from app.models import (
    CameraPixelDensityBand,
    CameraPixelDensityCameraResult,
    CameraPixelDensityProfile,
    CameraPixelDensityProfileSnapshot,
    CameraPixelDensityProjectionEnvelope,
    CameraPixelDensityResult,
    CameraPixelDensityState,
    CameraPixelDensityOverlapRegion,
    PixelDensityLegendDefinition,
    PixelDensityLegendThreshold,
    PoleCameraOverride,
    Project,
    utc_now,
)


PIXEL_DENSITY_MODEL_VERSION = "camera-face-density-vector-1.0.0"
FACE_WIDTH_M = 0.16
FORWARD_DEPTH_TOLERANCE_M = 1e-9
THRESHOLD_SNAP_TOLERANCE = 1e-9
DISTANCE_CAP_SIDES = 128
PROJECTED_DIGITS = 9
WGS84_DIGITS = 10
AREA_DIGITS = 6
GEOMETRY_AREA_TOLERANCE_M2 = 1e-8
MAX_ENABLED_CAMERAS = 200
MAX_OVERLAP_REGIONS = 20_000
MAX_PERSISTED_VERTICES = 250_000
MAX_RESULT_BYTES = 26_214_400
FIXED_MOUNT_CONTRACT = "fixed-zero-origin-1.0.0"
PIXEL_DENSITY_ASSUMPTIONS = [
    "Project-selected local projected CRS in metres; WGS84 is display/interchange only.",
    "Flat horizontal projection planes and an ideal rectilinear pinhole camera; no lens distortion.",
    "Density is horizontal pixels across a front-facing 0.16 m reference face at the AUTO midpoint height.",
    "No terrain, occlusion, recognition, identification, analytics, or compliance claim.",
]

Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class BandGeometry:
    rank: int
    threshold: PixelDensityLegendThreshold
    geometry: Polygon | MultiPolygon


@dataclass(frozen=True)
class ResolvedCameraDensityInput:
    footprint_id: str
    pole_id: str
    camera_slot_id: str
    sequence_index: int
    pole_active: bool
    longitude: float
    latitude: float
    enabled: bool
    fixture_model_id: str
    fixture_model_revision: int
    mounting_template_revision: int | None
    fixture_height_m: float | None
    fixture_azimuth_deg: float
    absolute_azimuth_deg: float
    slot: CameraMountingSlot
    template: CameraMountingTemplateRevision | None
    fixture_model: FixtureModel | None
    camera_model_id: str | None
    camera_model_revision: int | None
    camera: CameraModel | None
    lens_id: str | None
    lens_revision: int | None
    lens: LensConfiguration | None
    override: PoleCameraOverride | None
    resolution_warnings: tuple[str, ...]


def _finite_vector(values: Sequence[float], name: str) -> tuple[float, ...]:
    result = tuple(values)
    if len(result) != 3 or not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must contain three finite values.")
    return result


def camera_basis(absolute_azimuth_deg: float, downward_tilt_deg: float) -> tuple[Vector3, Vector3, Vector3]:
    if not all(math.isfinite(value) for value in (absolute_azimuth_deg, downward_tilt_deg)):
        raise ValueError("Camera azimuth and downward tilt must be finite.")
    azimuth = math.radians(absolute_azimuth_deg % 360.0)
    tilt = math.radians(downward_tilt_deg)
    forward = (math.sin(azimuth) * math.cos(tilt), math.cos(azimuth) * math.cos(tilt), -math.sin(tilt))
    right = (math.cos(azimuth), -math.sin(azimuth), 0.0)
    image_up = (-math.sin(azimuth) * math.sin(tilt), -math.cos(azimuth) * math.sin(tilt), math.cos(tilt))
    return forward, right, image_up


def camera_coordinates(
    point_xyz_m: Sequence[float],
    origin_xyz_m: Sequence[float],
    forward: Sequence[float],
    right: Sequence[float],
    image_up: Sequence[float],
) -> Vector3:
    point = _finite_vector(point_xyz_m, "World point")
    origin = _finite_vector(origin_xyz_m, "Camera origin")
    forward_vector = _finite_vector(forward, "Camera forward vector")
    right_vector = _finite_vector(right, "Camera right vector")
    up_vector = _finite_vector(image_up, "Camera image-up vector")
    delta = tuple(point[index] - origin[index] for index in range(3))
    dot = lambda vector: sum(delta[index] * vector[index] for index in range(3))
    return dot(right_vector), dot(up_vector), dot(forward_vector)


def horizontal_density_px_per_face(width_px: int, horizontal_fov_deg: float, forward_depth_m: float) -> float:
    if width_px <= 0 or not math.isfinite(horizontal_fov_deg) or not 0 < horizontal_fov_deg < 180:
        raise ValueError("Camera resolution and horizontal FOV must be finite and positive.")
    if not math.isfinite(forward_depth_m) or forward_depth_m <= FORWARD_DEPTH_TOLERANCE_M:
        raise ValueError("Camera-space forward depth must be greater than 1e-9 m.")
    focal_length_px = width_px / (2 * math.tan(math.radians(horizontal_fov_deg) / 2))
    return focal_length_px * FACE_WIDTH_M / forward_depth_m


def density_band_index(value: float, thresholds: Sequence[float]) -> int | None:
    if not math.isfinite(value):
        raise ValueError("Pixel density must be finite.")
    if not thresholds or not all(math.isfinite(threshold) for threshold in thresholds):
        raise ValueError("Pixel-density thresholds must be finite and non-empty.")
    snapped = next((threshold for threshold in thresholds if abs(value - threshold) <= THRESHOLD_SNAP_TOLERANCE), value)
    eligible = [index for index, threshold in enumerate(thresholds) if snapped >= threshold]
    return eligible[-1] if eligible else None


def _signed_area(vertices: Sequence[tuple[float, float]]) -> float:
    pairs = list(vertices)
    return 0.5 * sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(pairs, pairs[1:] + pairs[:1], strict=True)
    )


def canonical_ring(
    vertices: Sequence[tuple[float, float]],
    *,
    digits: int = PROJECTED_DIGITS,
    clockwise: bool = False,
) -> list[tuple[float, float]]:
    rounded = [(round(float(x), digits), round(float(y), digits)) for x, y in vertices]
    if rounded and rounded[0] == rounded[-1]:
        rounded.pop()
    if len(rounded) < 3 or not all(math.isfinite(value) for vertex in rounded for value in vertex):
        raise ValueError("Polygon ring must contain at least three finite vertices.")
    if (_signed_area(rounded) < 0) != clockwise:
        rounded.reverse()
    start = min(range(len(rounded)), key=lambda index: rounded[index])
    ordered = rounded[start:] + rounded[:start]
    return [*ordered, ordered[0]]


def canonical_polygonal(geometry: Polygon | MultiPolygon) -> Polygon | MultiPolygon:
    if geometry.is_empty:
        return Polygon()
    polygons = list(geometry.geoms) if isinstance(geometry, MultiPolygon) else [geometry]
    normalized: list[Polygon] = []
    for polygon in polygons:
        if not isinstance(polygon, Polygon):
            raise ValueError("Only polygonal camera-density geometry is supported.")
        ring = canonical_ring(list(polygon.exterior.coords))
        holes = sorted(
            (canonical_ring(list(interior.coords), clockwise=True) for interior in polygon.interiors),
            key=lambda item: tuple(item),
        )
        candidate = Polygon(ring, holes)
        if not candidate.is_valid or candidate.area <= GEOMETRY_AREA_TOLERANCE_M2:
            raise ValueError("Camera-density geometry is invalid or degenerate.")
        normalized.append(candidate)
    normalized.sort(key=_canonical_polygon_sort_key)
    return normalized[0] if len(normalized) == 1 else MultiPolygon(normalized)


def project_frustum_plane(
    origin_xyz_m: Sequence[float],
    forward: Sequence[float],
    right: Sequence[float],
    image_up: Sequence[float],
    horizontal_fov_deg: float,
    vertical_fov_deg: float,
    plane_height_m: float,
) -> Polygon:
    origin = _finite_vector(origin_xyz_m, "Camera origin")
    vectors = tuple(_finite_vector(vector, name) for vector, name in (
        (forward, "Camera forward vector"), (right, "Camera right vector"), (image_up, "Camera image-up vector")
    ))
    if not all(math.isfinite(value) and 0 < value < 180 for value in (horizontal_fov_deg, vertical_fov_deg)):
        raise ValueError("Camera field of view must be finite and between zero and 180 degrees.")
    if not math.isfinite(plane_height_m):
        raise ValueError("Projection-plane height must be finite.")
    forward_vector, right_vector, up_vector = vectors
    half_h = math.tan(math.radians(horizontal_fov_deg) / 2)
    half_v = math.tan(math.radians(vertical_fov_deg) / 2)
    vertices: list[tuple[float, float]] = []
    for horizontal_sign, vertical_sign in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        ray = tuple(
            forward_vector[index]
            + horizontal_sign * half_h * right_vector[index]
            + vertical_sign * half_v * up_vector[index]
            for index in range(3)
        )
        if abs(ray[2]) <= FORWARD_DEPTH_TOLERANCE_M:
            raise ValueError("Frustum boundary ray is horizontal or numerically unstable.")
        distance = (plane_height_m - origin[2]) / ray[2]
        if not math.isfinite(distance) or distance <= FORWARD_DEPTH_TOLERANCE_M:
            raise ValueError("Frustum boundary ray does not intersect the plane in front of the camera.")
        vertices.append((origin[0] + distance * ray[0], origin[1] + distance * ray[1]))
    polygon = Polygon(canonical_ring(vertices))
    if not polygon.is_valid or polygon.area <= GEOMETRY_AREA_TOLERANCE_M2:
        raise ValueError("Projected frustum plane is invalid or degenerate.")
    return polygon


def distance_cap_polygon(origin_x_m: float, origin_y_m: float, radius_m: float) -> Polygon:
    if not all(math.isfinite(value) for value in (origin_x_m, origin_y_m, radius_m)) or radius_m <= 0:
        raise ValueError("Maximum visible distance must be finite and positive.")
    vertices = [
        (
            origin_x_m - radius_m * math.sin(2 * math.pi * index / DISTANCE_CAP_SIDES),
            origin_y_m + radius_m * math.cos(2 * math.pi * index / DISTANCE_CAP_SIDES),
        )
        for index in range(DISTANCE_CAP_SIDES)
    ]
    ring = [(round(x, PROJECTED_DIGITS), round(y, PROJECTED_DIGITS)) for x, y in vertices]
    polygon = Polygon([*ring, ring[0]])
    if not polygon.is_valid or not polygon.exterior.is_ccw:
        raise ValueError("Maximum-distance cap is invalid.")
    return polygon


def _clip_vertices(
    vertices: list[tuple[float, float]],
    evaluate,
    *,
    keep_greater: bool,
    boundary: float,
) -> list[tuple[float, float]]:
    if not vertices:
        return []
    result: list[tuple[float, float]] = []
    previous = vertices[-1]
    previous_value = evaluate(previous)
    previous_inside = previous_value >= boundary if keep_greater else previous_value <= boundary
    for current in vertices:
        current_value = evaluate(current)
        current_inside = current_value >= boundary if keep_greater else current_value <= boundary
        if current_inside != previous_inside:
            denominator = current_value - previous_value
            if abs(denominator) > 1e-15:
                ratio = (boundary - previous_value) / denominator
                result.append((previous[0] + ratio * (current[0] - previous[0]), previous[1] + ratio * (current[1] - previous[1])))
        if current_inside:
            result.append(current)
        previous, previous_value, previous_inside = current, current_value, current_inside
    return result


def clip_polygon_to_depth_interval(
    domain: Polygon,
    *,
    origin_xyz_m: Sequence[float],
    forward: Sequence[float],
    plane_height_m: float,
    minimum_depth_m: float,
    maximum_depth_m: float,
) -> Polygon:
    origin = _finite_vector(origin_xyz_m, "Camera origin")
    forward_vector = _finite_vector(forward, "Camera forward vector")
    values = (plane_height_m, minimum_depth_m, maximum_depth_m)
    if not all(math.isfinite(value) for value in values) or minimum_depth_m < 0 or maximum_depth_m <= minimum_depth_m:
        raise ValueError("Depth interval and plane height must be finite and ordered.")
    if not isinstance(domain, Polygon) or not domain.is_valid or domain.is_empty or domain.interiors:
        raise ValueError("Midpoint density domain must be one valid simple polygon.")
    def depth(point: tuple[float, float]) -> float:
        return (
            (point[0] - origin[0]) * forward_vector[0]
            + (point[1] - origin[1]) * forward_vector[1]
            + (plane_height_m - origin[2]) * forward_vector[2]
        )
    vertices = list(domain.exterior.coords)[:-1]
    vertices = _clip_vertices(vertices, depth, keep_greater=True, boundary=minimum_depth_m)
    vertices = _clip_vertices(vertices, depth, keep_greater=False, boundary=maximum_depth_m)
    if len(vertices) < 3:
        return Polygon()
    candidate = Polygon(canonical_ring(vertices))
    if candidate.area <= GEOMETRY_AREA_TOLERANCE_M2:
        return Polygon()
    if not candidate.is_valid:
        raise ValueError("Depth-clipped density geometry is invalid.")
    return candidate


def clip_midpoint_density_bands(
    domain: Polygon,
    *,
    origin_xyz_m: tuple[float, float, float],
    forward: tuple[float, float, float],
    measurement_height_m: float,
    focal_length_px: float,
    legend: PixelDensityLegendDefinition,
) -> list[BandGeometry]:
    if not math.isfinite(focal_length_px) or focal_length_px <= 0:
        raise ValueError("Camera focal length must be finite and positive.")
    result: list[BandGeometry] = []
    density_scale = focal_length_px * FACE_WIDTH_M
    for rank, threshold in enumerate(legend.thresholds, start=1):
        minimum_depth = 0.0 if threshold.maximum is None else density_scale / threshold.maximum
        maximum_depth = density_scale / threshold.minimum
        geometry = clip_polygon_to_depth_interval(
            domain,
            origin_xyz_m=origin_xyz_m,
            forward=forward,
            plane_height_m=measurement_height_m,
            minimum_depth_m=minimum_depth,
            maximum_depth_m=maximum_depth,
        )
        if not geometry.is_empty:
            result.append(BandGeometry(rank=rank, threshold=threshold, geometry=canonical_polygonal(geometry)))
    return result


def profile_snapshot(profile: CameraPixelDensityProfile, legend: PixelDensityLegendDefinition) -> CameraPixelDensityProfileSnapshot:
    return CameraPixelDensityProfileSnapshot(
        lower_projection_height_m=profile.lower_projection_height_m,
        upper_projection_height_m=profile.upper_projection_height_m,
        measurement_height_m=profile.measurement_height_m,
        maximum_visible_distance_m=profile.maximum_visible_distance_m,
        legend_id=legend.id,
        face_width_m=legend.object_width_m,
    )


def resolve_camera_pixel_density_inputs(
    project: Project,
    fixtures: FixtureModelCatalog,
    cameras: CameraEquipmentCatalog,
) -> list[ResolvedCameraDensityInput]:
    fixture_revisions = {(item.id, item.revision): item for item in [*fixtures.fixture_models, *fixtures.fixture_model_history]}
    fixture_current = {item.id: item for item in fixtures.fixture_models}
    camera_revisions = {(item.id, item.revision): item for item in [*cameras.camera_models, *cameras.camera_model_history]}
    lens_revisions = {(item.id, item.revision): item for item in [*cameras.lenses, *cameras.lens_history]}
    result: list[ResolvedCameraDensityInput] = []
    for source in sorted(project.source.poles, key=lambda item: (item.sequence_index, item.id)):
        edit = project.pole_edits.get(source.id)
        config = edit.fixture_configuration if edit else None
        if config is None or edit is None or edit.fixture_type is None or edit.fixture_type.value != "SMART":
            continue
        pinned_model = fixture_revisions.get((config.fixture_model_id, config.fixture_model_revision))
        reference_model = pinned_model or fixture_current.get(config.fixture_model_id)
        if reference_model is None or not reference_model.capabilities.cameras:
            continue
        template = next(
            (item for item in (pinned_model.mounting_template_revisions if pinned_model else []) if item.revision == config.mounting_template_revision),
            None,
        )
        reference_template = template or reference_model.current_template()
        if reference_template is None:
            continue
        longitude = edit.longitude if edit.longitude is not None else source.longitude
        latitude = edit.latitude if edit.latitude is not None else source.latitude
        pole_active = edit.active if edit.active is not None else True
        for slot in sorted(reference_template.slots, key=lambda item: item.id):
            override = config.camera_overrides.get(slot.id)
            camera_id = override.camera_model_id if override and override.camera_model_id is not None else slot.camera_model_id
            camera_revision = override.camera_model_revision if override and override.camera_model_id is not None else slot.camera_model_revision
            lens_id = override.lens_id if override and override.lens_id is not None else slot.lens_id
            lens_revision = override.lens_revision if override and override.lens_id is not None else slot.lens_revision
            enabled = override.enabled if override and override.enabled is not None else slot.enabled
            warnings: list[str] = []
            if pinned_model is None:
                warnings.append("Pinned fixture model revision does not exist.")
            if template is None:
                warnings.append("Pinned mounting template revision does not exist.")
            result.append(ResolvedCameraDensityInput(
                footprint_id=f"{source.id}/{slot.id}", pole_id=source.id, camera_slot_id=slot.id,
                sequence_index=source.sequence_index, pole_active=pole_active,
                longitude=longitude, latitude=latitude, enabled=enabled,
                fixture_model_id=config.fixture_model_id, fixture_model_revision=config.fixture_model_revision,
                mounting_template_revision=config.mounting_template_revision,
                fixture_height_m=edit.height_m if edit.height_m is not None else project.defaults.pole_height_m,
                fixture_azimuth_deg=config.fixture_azimuth_deg,
                absolute_azimuth_deg=camera_absolute_azimuth(config.fixture_azimuth_deg, slot.relative_azimuth_deg),
                slot=slot, template=template, fixture_model=pinned_model,
                camera_model_id=camera_id, camera_model_revision=camera_revision,
                camera=camera_revisions.get((camera_id, camera_revision)) if camera_id is not None and camera_revision is not None else None,
                lens_id=lens_id, lens_revision=lens_revision,
                lens=lens_revisions.get((lens_id, lens_revision)) if lens_id is not None and lens_revision is not None else None,
                override=override, resolution_warnings=tuple(warnings),
            ))
    return result


def _resolved_payload(item: ResolvedCameraDensityInput) -> dict[str, object]:
    return {
        "footprint_id": item.footprint_id,
        "sequence_index": item.sequence_index,
        "pole_active": item.pole_active,
        "longitude": item.longitude,
        "latitude": item.latitude,
        "enabled": item.enabled,
        "fixture_model_id": item.fixture_model_id,
        "fixture_model_revision": item.fixture_model_revision,
        "mounting_template_revision": item.mounting_template_revision,
        "geometry_contract_version": item.template.geometry_contract_version if item.template else None,
        "fixture_height_m": item.fixture_height_m,
        "fixture_azimuth_deg": item.fixture_azimuth_deg,
        "slot": item.slot.model_dump(mode="json"),
        "override": item.override.model_dump(mode="json") if item.override else None,
        "camera": item.camera.model_dump(mode="json") if item.camera else {
            "id": item.camera_model_id, "revision": item.camera_model_revision,
        },
        "lens": item.lens.model_dump(mode="json") if item.lens else {
            "id": item.lens_id, "revision": item.lens_revision,
        },
    }


def camera_pixel_density_input_sha256(
    project: Project,
    fixtures: FixtureModelCatalog,
    cameras: CameraEquipmentCatalog,
    legend: PixelDensityLegendDefinition,
) -> str:
    profile = project.camera_pixel_density_profile
    if not all(math.isfinite(value) for value in (
        profile.lower_projection_height_m,
        profile.upper_projection_height_m,
        profile.maximum_visible_distance_m,
        profile.measurement_height_m,
    )):
        raise ValueError("Camera pixel-density calculation inputs are not finite JSON-compatible values.")
    payload = {
        "model_version": PIXEL_DENSITY_MODEL_VERSION,
        "fixed_mount_contract": FIXED_MOUNT_CONTRACT,
        "distance_cap_sides": DISTANCE_CAP_SIDES,
        "projected_digits": PROJECTED_DIGITS,
        "projected_crs": project.projected_crs,
        "profile": profile_snapshot(profile, legend).model_dump(mode="json"),
        "legend": legend.model_dump(mode="json"),
        "cameras": [_resolved_payload(item) for item in resolve_camera_pixel_density_inputs(project, fixtures, cameras)],
    }
    try:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("Camera pixel-density calculation inputs are not finite JSON-compatible values.") from exc
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _polygonal_parts(geometry: Polygon | MultiPolygon) -> list[Polygon]:
    if geometry.is_empty:
        return []
    if isinstance(geometry, Polygon):
        return [geometry]
    if isinstance(geometry, MultiPolygon):
        return sorted(geometry.geoms, key=_canonical_polygon_sort_key)
    raise ValueError("Camera-density overlay produced non-polygonal geometry.")


def _canonical_polygon_coordinate_sequence(polygon: Polygon) -> tuple[object, ...]:
    exterior = tuple(canonical_ring(list(polygon.exterior.coords), digits=PROJECTED_DIGITS))
    interiors = tuple(sorted(
        tuple(canonical_ring(list(interior.coords), digits=PROJECTED_DIGITS, clockwise=True))
        for interior in polygon.interiors
    ))
    return (exterior, interiors)


def _canonical_polygon_sort_key(polygon: Polygon) -> tuple[float, tuple[object, ...]]:
    return (-round(polygon.area, AREA_DIGITS), _canonical_polygon_coordinate_sequence(polygon))


def _rings(
    geometry: Polygon | MultiPolygon, *, digits: int, sort_parts: bool = True,
) -> list[list[list[tuple[float, float]]]]:
    result: list[list[list[tuple[float, float]]]] = []
    polygons = _polygonal_parts(geometry) if sort_parts else (
        [geometry] if isinstance(geometry, Polygon) else list(geometry.geoms)
    )
    for polygon in polygons:
        rings = [canonical_ring(list(polygon.exterior.coords), digits=digits)]
        rings.extend(canonical_ring(list(interior.coords), digits=digits, clockwise=True) for interior in polygon.interiors)
        result.append(rings)
    return result


def _transform_polygonal(geometry: Polygon | MultiPolygon, transformer: Transformer) -> Polygon | MultiPolygon:
    polygons: list[Polygon] = []
    for polygon in _polygonal_parts(geometry):
        exterior = [transformer.transform(x, y) for x, y in polygon.exterior.coords]
        interiors = [[transformer.transform(x, y) for x, y in ring.coords] for ring in polygon.interiors]
        polygons.append(Polygon(exterior, interiors))
    return polygons[0] if len(polygons) == 1 else MultiPolygon(polygons)


def calculate_one_camera_density(
    project: Project,
    item: ResolvedCameraDensityInput,
    legend: PixelDensityLegendDefinition,
    *,
    to_projected: Transformer,
    to_wgs84: Transformer,
) -> CameraPixelDensityCameraResult:
    camera = item.camera
    lens = item.lens
    result = CameraPixelDensityCameraResult(
        footprint_id=item.footprint_id, pole_id=item.pole_id, camera_slot_id=item.camera_slot_id,
        enabled=item.enabled, fixture_model_id=item.fixture_model_id, fixture_model_revision=item.fixture_model_revision,
        mounting_template_revision=item.mounting_template_revision,
        geometry_contract_version=item.template.geometry_contract_version if item.template else None,
        camera_model_id=item.camera_model_id, camera_model_revision=item.camera_model_revision,
        lens_id=item.lens_id, lens_revision=item.lens_revision,
        resolution_width_px=camera.resolution_width_px if camera else None,
        resolution_height_px=camera.resolution_height_px if camera else None,
        horizontal_fov_deg=lens.horizontal_fov_deg if lens else None,
        vertical_fov_deg=lens.vertical_fov_deg if lens else None,
        fixture_height_m=item.fixture_height_m, camera_absolute_azimuth_deg=item.absolute_azimuth_deg,
        fixed_downward_tilt_deg=item.slot.downward_tilt_deg, assumptions=PIXEL_DENSITY_ASSUMPTIONS,
    )
    if not item.pole_active:
        result.warnings = ["Pole is inactive; camera does not contribute."]
        return result
    if not item.enabled:
        return result
    warnings = list(item.resolution_warnings)
    if item.fixture_height_m is None:
        warnings.append("Fixture/pole height is required.")
    if item.camera_model_id is None:
        warnings.append("A pinned camera model is required.")
    elif item.camera_model_revision is None:
        warnings.append("A pinned camera model revision is required.")
    elif camera is None:
        warnings.append("Pinned camera model revision does not exist.")
    elif camera.resolution_width_px is None or camera.resolution_height_px is None:
        warnings.append("Pinned camera revision requires positive horizontal and vertical resolution.")
    if item.lens_id is None:
        warnings.append("An explicit pinned lens is required; no default lens is assigned.")
    elif item.lens_revision is None:
        warnings.append("A pinned lens revision is required.")
    elif lens is None:
        warnings.append("Pinned lens revision does not exist.")
    elif lens.horizontal_fov_deg is None or lens.vertical_fov_deg is None:
        warnings.append("Pinned lens revision lacks catalog horizontal/vertical FOV.")
    if camera and lens and camera.id not in lens.compatible_camera_model_ids:
        warnings.append("Selected camera and lens revisions are incompatible.")
    if item.template is None or item.template.geometry_contract_version != FIXED_MOUNT_CONTRACT:
        warnings.append("Pinned mounting template does not use the approved fixed-mount contract.")
    if item.override and (item.override.relative_azimuth_deg is not None or item.override.downward_tilt_deg is not None):
        warnings.append("Legacy per-pole camera orientation override is preserved but unsupported; explicitly reset this slot to the immutable template.")
    if (item.slot.origin_offset_x_m, item.slot.origin_offset_y_m, item.slot.origin_offset_z_m) != (0, 0, 0):
        warnings.append("Mounting template does not use the approved zero XYZ optical-center offsets.")
    if warnings:
        result.warnings = list(dict.fromkeys(warnings))
        return result
    assert camera and lens and item.fixture_height_m is not None
    origin_x, origin_y = to_projected.transform(item.longitude, item.latitude)
    origin = (origin_x, origin_y, item.fixture_height_m)
    forward, right, image_up = camera_basis(item.absolute_azimuth_deg, item.slot.downward_tilt_deg)
    profile = project.camera_pixel_density_profile
    try:
        planes = [
            project_frustum_plane(origin, forward, right, image_up, lens.horizontal_fov_deg, lens.vertical_fov_deg, height)
            for height in (profile.lower_projection_height_m, profile.measurement_height_m, profile.upper_projection_height_m)
        ]
        cap = distance_cap_polygon(origin_x, origin_y, profile.maximum_visible_distance_m)
        envelope_raw = unary_union([planes[0], planes[2]]).convex_hull.intersection(cap)
        if envelope_raw.is_empty or not isinstance(envelope_raw, (Polygon, MultiPolygon)):
            raise ValueError("Projection envelope is empty or non-polygonal.")
        envelope = canonical_polygonal(envelope_raw)
        midpoint_raw = planes[1].intersection(envelope).intersection(cap)
        if midpoint_raw.is_empty or not isinstance(midpoint_raw, Polygon):
            raise ValueError("Midpoint projection is empty, fragmented, or non-polygonal.")
        midpoint = canonical_polygonal(midpoint_raw)
        if not isinstance(midpoint, Polygon):
            raise ValueError("Midpoint projection is fragmented.")
        focal_length_px = camera.resolution_width_px / (2 * math.tan(math.radians(lens.horizontal_fov_deg) / 2))
        band_geometries = clip_midpoint_density_bands(
            midpoint, origin_xyz_m=origin, forward=forward, measurement_height_m=profile.measurement_height_m,
            focal_length_px=focal_length_px, legend=legend,
        )
    except ValueError as exc:
        result.warnings = [str(exc)]
        return result
    envelope_wgs84 = _transform_polygonal(envelope, to_wgs84)
    result.projection_envelope = CameraPixelDensityProjectionEnvelope(
        projected_rings_m=_rings(envelope, digits=PROJECTED_DIGITS),
        wgs84_rings=_rings(envelope_wgs84, digits=WGS84_DIGITS, sort_parts=False),
    )
    for band in band_geometries:
        wgs84 = _transform_polygonal(band.geometry, to_wgs84)
        result.bands.append(CameraPixelDensityBand(
            band_id=f"px-face-{band.threshold.minimum:g}", legend_id=legend.id, rank=band.rank,
            minimum_px_per_face=band.threshold.minimum, maximum_px_per_face=band.threshold.maximum,
            display_value_px_per_face=band.threshold.minimum, colour_token=band.threshold.token,
            projected_rings_m=_rings(band.geometry, digits=PROJECTED_DIGITS),
            wgs84_rings=_rings(wgs84, digits=WGS84_DIGITS, sort_parts=False), area_m2=round(band.geometry.area, AREA_DIGITS),
        ))
    result.valid = bool(result.bands)
    if not result.valid:
        result.warnings = ["Camera midpoint domain contains no visible pixel-density band."]
    return result


def aggregate_camera_warnings(camera_results: Sequence[CameraPixelDensityCameraResult]) -> list[str]:
    return [f"{item.footprint_id}: {warning}" for item in camera_results for warning in item.warnings]


def _stored_polygonal(rings: list[list[list[tuple[float, float]]]]) -> Polygon | MultiPolygon:
    polygons: list[Polygon] = []
    for polygon_rings in rings:
        if not polygon_rings:
            continue
        polygon = Polygon(polygon_rings[0], polygon_rings[1:])
        if not polygon.is_valid or polygon.area <= GEOMETRY_AREA_TOLERANCE_M2:
            raise ValueError("Persisted camera-density geometry is invalid or degenerate.")
        polygons.append(polygon)
    if not polygons:
        return Polygon()
    return polygons[0] if len(polygons) == 1 else MultiPolygon(polygons)


def calculate_density_overlaps(
    camera_results: Sequence[CameraPixelDensityCameraResult],
    *,
    to_wgs84: Transformer | None = None,
) -> list[CameraPixelDensityOverlapRegion]:
    features: list[tuple[str, int, str, Polygon | MultiPolygon]] = []
    for camera in sorted(camera_results, key=lambda item: item.footprint_id):
        if not camera.enabled or not camera.valid:
            continue
        for band in camera.bands:
            geometry = _stored_polygonal(band.projected_rings_m)
            if not geometry.is_empty:
                features.append((camera.footprint_id, band.rank, band.band_id, geometry))
    if len({item[0] for item in features}) < 2:
        return []

    geometries = [item[3] for item in features]
    tree = STRtree(geometries)
    participating: set[int] = set()
    for index, geometry in enumerate(geometries):
        for other_index in tree.query(geometry, predicate="intersects"):
            other = int(other_index)
            if other == index or features[other][0] == features[index][0]:
                continue
            if geometry.intersection(geometries[other]).area > GEOMETRY_AREA_TOLERANCE_M2:
                participating.update((index, other))
    if not participating:
        return []

    boundaries = unary_union([geometries[index].boundary for index in sorted(participating)])
    cells = sorted(
        (cell for cell in polygonize(boundaries) if cell.area > GEOMETRY_AREA_TOLERANCE_M2),
        key=lambda cell: tuple(canonical_ring(list(cell.exterior.coords))),
    )
    grouped: dict[tuple[tuple[str, ...], str, str, int], list[Polygon]] = {}
    for cell in cells:
        point = cell.representative_point()
        best_by_camera: dict[str, tuple[int, str]] = {}
        for index in sorted(participating):
            footprint_id, rank, band_id, geometry = features[index]
            if geometry.covers(point):
                prior = best_by_camera.get(footprint_id)
                if prior is None or (rank, band_id) > prior:
                    best_by_camera[footprint_id] = (rank, band_id)
        contributors = tuple(sorted(best_by_camera))
        if len(contributors) < 2:
            continue
        winning_rank = max(best_by_camera[item][0] for item in contributors)
        winning_camera = min(item for item in contributors if best_by_camera[item][0] == winning_rank)
        winning_band = best_by_camera[winning_camera][1]
        grouped.setdefault((contributors, winning_camera, winning_band, winning_rank), []).append(cell)

    regions: list[CameraPixelDensityOverlapRegion] = []
    for (contributors, winning_camera, winning_band, winning_rank), group_cells in sorted(grouped.items()):
        merged_raw = unary_union(group_cells)
        if not isinstance(merged_raw, (Polygon, MultiPolygon)) or merged_raw.is_empty:
            raise ValueError("Camera-density overlap partition produced non-polygonal geometry.")
        merged = canonical_polygonal(merged_raw)
        projected_rings = _rings(merged, digits=PROJECTED_DIGITS)
        wgs84_geometry = _transform_polygonal(merged, to_wgs84) if to_wgs84 is not None else merged
        identifier_payload = {
            "contributors": contributors,
            "winner": winning_camera,
            "winning_band_id": winning_band,
            "winning_rank": winning_rank,
            "projected_rings_m": projected_rings,
        }
        digest = hashlib.sha256(json.dumps(identifier_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        regions.append(CameraPixelDensityOverlapRegion(
            overlap_region_id=f"density-overlap-{digest[:24]}",
            camera_footprint_ids=list(contributors), multiplicity=len(contributors),
            winning_camera_footprint_id=winning_camera, winning_band_id=winning_band,
            winning_band_rank=winning_rank, projected_rings_m=projected_rings,
            wgs84_rings=_rings(
                wgs84_geometry, digits=WGS84_DIGITS, sort_parts=to_wgs84 is None,
            ), area_m2=round(merged.area, AREA_DIGITS),
        ))
    return sorted(regions, key=overlap_region_sort_key)


def overlap_region_sort_key(item: CameraPixelDensityOverlapRegion) -> tuple[object, ...]:
    geometry_sequence = tuple(
        tuple(tuple((float(x), float(y)) for x, y in ring) for ring in polygon)
        for polygon in item.projected_rings_m
    )
    return (
        item.multiplicity,
        tuple(item.camera_footprint_ids),
        item.winning_band_rank,
        geometry_sequence,
    )


def count_persisted_vertices(result: CameraPixelDensityResult) -> tuple[int, int]:
    projected = 0
    wgs84 = 0
    for camera in result.camera_results:
        projected += sum(len(ring) for polygon in camera.projection_envelope.projected_rings_m for ring in polygon)
        wgs84 += sum(len(ring) for polygon in camera.projection_envelope.wgs84_rings for ring in polygon)
        for band in camera.bands:
            projected += sum(len(ring) for polygon in band.projected_rings_m for ring in polygon)
            wgs84 += sum(len(ring) for polygon in band.wgs84_rings for ring in polygon)
    for region in result.overlap_regions:
        projected += sum(len(ring) for polygon in region.projected_rings_m for ring in polygon)
        wgs84 += sum(len(ring) for polygon in region.wgs84_rings for ring in polygon)
    return projected, wgs84


def validate_camera_pixel_density_result_limits(result: CameraPixelDensityResult) -> None:
    if len(result.overlap_regions) > MAX_OVERLAP_REGIONS:
        raise ValueError("Camera pixel-density result exceeds the 20,000-overlap-region safety limit.")
    projected, wgs84 = count_persisted_vertices(result)
    if projected > MAX_PERSISTED_VERTICES:
        raise ValueError("Camera pixel-density result exceeds the 250,000 projected-coordinate safety limit.")
    if wgs84 > MAX_PERSISTED_VERTICES:
        raise ValueError("Camera pixel-density result exceeds the 250,000 WGS84-coordinate safety limit.")
    payload = result.model_dump(mode="json")
    size_bytes = len(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    if size_bytes > MAX_RESULT_BYTES:
        raise ValueError("Camera pixel-density result exceeds the 25 MiB compact-JSON safety limit.")


def apply_camera_pixel_density_result(project: Project, result: CameraPixelDensityResult) -> Project:
    updated = project.model_copy(deep=True)
    updated.camera_pixel_density.result = result
    updated.camera_pixel_density.state = CameraPixelDensityState(
        status="current",
        calculation_input_sha256=result.calculation_input_sha256,
        message=None,
    )
    updated.layer_state.camera_pixel_density = True
    updated.updated_at = utc_now()
    return updated


def invalidate_stale_camera_pixel_density(
    project: Project,
    fixtures: FixtureModelCatalog,
    cameras: CameraEquipmentCatalog,
    legend: PixelDensityLegendDefinition,
) -> bool:
    layer = project.camera_pixel_density
    if layer.result is None or layer.state.status == "not-calculated":
        return False
    authoritative = camera_pixel_density_input_sha256(project, fixtures, cameras, legend)
    if authoritative == layer.result.calculation_input_sha256:
        return False
    changed = layer.state.status != "stale" or layer.state.message != "Stale — recalculate required" or project.layer_state.camera_pixel_density
    layer.state = CameraPixelDensityState(
        status="stale",
        calculation_input_sha256=layer.result.calculation_input_sha256,
        message="Stale — recalculate required",
    )
    project.layer_state.camera_pixel_density = False
    return changed


def calculate_camera_pixel_density(
    project: Project,
    fixtures: FixtureModelCatalog,
    cameras: CameraEquipmentCatalog,
    legend: PixelDensityLegendDefinition,
    *,
    calculated_at: datetime | None = None,
) -> CameraPixelDensityResult:
    if project.projected_crs is None:
        raise ValueError("Project engineering CRS is required for camera pixel-density calculation.")
    crs = validate_projected_metre_crs(project.projected_crs)
    to_projected, to_wgs84 = project_transformers(crs)
    resolved = resolve_camera_pixel_density_inputs(project, fixtures, cameras)
    enabled_count = sum(item.enabled for item in resolved)
    if enabled_count > MAX_ENABLED_CAMERAS:
        raise ValueError("Camera pixel-density calculation exceeds the 200-enabled-camera safety limit.")
    camera_results = [
        calculate_one_camera_density(project, item, legend, to_projected=to_projected, to_wgs84=to_wgs84)
        for item in resolved
    ]
    overlaps = calculate_density_overlaps(camera_results, to_wgs84=to_wgs84)
    result = CameraPixelDensityResult(
        calculated_at=calculated_at or utc_now(), projected_crs=project.projected_crs,
        calculation_input_sha256=camera_pixel_density_input_sha256(project, fixtures, cameras, legend),
        profile_snapshot=profile_snapshot(project.camera_pixel_density_profile, legend),
        camera_results=camera_results, overlap_regions=overlaps,
        warnings=aggregate_camera_warnings(camera_results), assumptions=PIXEL_DENSITY_ASSUMPTIONS,
    )
    validate_camera_pixel_density_result_limits(result)
    return result
