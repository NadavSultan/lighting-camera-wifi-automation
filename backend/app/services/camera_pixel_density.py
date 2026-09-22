from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from shapely.geometry import GeometryCollection, MultiPolygon, Polygon

from app.models import PixelDensityLegendDefinition, PixelDensityLegendThreshold


PIXEL_DENSITY_MODEL_VERSION = "camera-face-density-vector-1.0.0"
FACE_WIDTH_M = 0.16
FORWARD_DEPTH_TOLERANCE_M = 1e-9
THRESHOLD_SNAP_TOLERANCE = 1e-9
DISTANCE_CAP_SIDES = 128
PROJECTED_DIGITS = 9
WGS84_DIGITS = 10
AREA_DIGITS = 6
GEOMETRY_AREA_TOLERANCE_M2 = 1e-8

Vector3 = tuple[float, float, float]


@dataclass(frozen=True)
class BandGeometry:
    rank: int
    threshold: PixelDensityLegendThreshold
    geometry: Polygon | MultiPolygon


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


def canonical_ring(vertices: Sequence[tuple[float, float]], *, digits: int = PROJECTED_DIGITS) -> list[tuple[float, float]]:
    rounded = [(round(float(x), digits), round(float(y), digits)) for x, y in vertices]
    if rounded and rounded[0] == rounded[-1]:
        rounded.pop()
    if len(rounded) < 3 or not all(math.isfinite(value) for vertex in rounded for value in vertex):
        raise ValueError("Polygon ring must contain at least three finite vertices.")
    if _signed_area(rounded) < 0:
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
        if not isinstance(polygon, Polygon) or polygon.interiors:
            raise ValueError("Only simple polygonal camera-density geometry is supported.")
        ring = canonical_ring(list(polygon.exterior.coords))
        candidate = Polygon(ring)
        if not candidate.is_valid or candidate.area <= GEOMETRY_AREA_TOLERANCE_M2:
            raise ValueError("Camera-density geometry is invalid or degenerate.")
        normalized.append(candidate)
    normalized.sort(key=lambda item: tuple(item.exterior.coords))
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
