"""Read-only raster presentation of a current BL-016 pixel-density result.

The persisted vector result remains the authoritative calculation and inspection
record. This renderer evaluates its approved pinhole equation at tile pixel
centres; it never edits the project or adds camera densities together.
"""

from __future__ import annotations

import math
import struct
import zlib
from functools import lru_cache

import numpy as np
from pyproj import Transformer
from shapely import contains_xy
from shapely.geometry import Polygon

from app.models import PixelDensityLegendDefinition, Project
from app.services.camera_pixel_density import camera_basis


TILE_SIZE = 256
WEB_MERCATOR_HALF_WORLD_M = 20037508.342789244


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    payload = kind + data
    return struct.pack(">I", len(data)) + payload + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)


def _png(rgba: np.ndarray) -> bytes:
    height, width, channels = rgba.shape
    if channels != 4 or rgba.dtype != np.uint8:
        raise ValueError("heatmap pixels must be RGBA bytes")
    rows = b"".join(b"\x00" + rgba[row].tobytes() for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", header) + _png_chunk(b"IDAT", zlib.compress(rows, level=6)) + _png_chunk(b"IEND", b"")


@lru_cache(maxsize=1)
def transparent_tile() -> bytes:
    return _png(np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8))


def interpolate_legend_colours(values: np.ndarray, legend: PixelDensityLegendDefinition) -> np.ndarray:
    """Use the existing legend as colour stops, clamping 70+ to magenta."""
    stops = np.asarray([item.minimum for item in legend.thresholds], dtype=np.float64)
    rgb = np.asarray(
        [[int(item.colour[offset:offset + 2], 16) for offset in (1, 3, 5)] for item in legend.thresholds],
        dtype=np.float64,
    )
    return np.stack(
        [np.rint(np.interp(values, stops, rgb[:, channel])).astype(np.uint8) for channel in range(3)],
        axis=-1,
    )


def _projected_tile_centres(projected_crs: str, z: int, x: int, y: int) -> tuple[np.ndarray, np.ndarray]:
    world = WEB_MERCATOR_HALF_WORLD_M * 2
    pixel_span = world / ((1 << z) * TILE_SIZE)
    mercator_x = -WEB_MERCATOR_HALF_WORLD_M + ((x * TILE_SIZE) + np.arange(TILE_SIZE) + 0.5) * pixel_span
    mercator_y = WEB_MERCATOR_HALF_WORLD_M - ((y * TILE_SIZE) + np.arange(TILE_SIZE) + 0.5) * pixel_span
    grid_x, grid_y = np.meshgrid(mercator_x, mercator_y)
    projected_x, projected_y = Transformer.from_crs("EPSG:3857", projected_crs, always_xy=True).transform(grid_x, grid_y)
    return np.asarray(projected_x), np.asarray(projected_y)


def _tile_density(project: Project, projected_x: np.ndarray, projected_y: np.ndarray) -> np.ndarray:
    result = project.camera_pixel_density.result
    assert result is not None
    best = np.zeros(projected_x.shape, dtype=np.float64)
    finite = np.isfinite(projected_x) & np.isfinite(projected_y)
    if not finite.any():
        return best
    bounds = (
        float(np.min(projected_x[finite])), float(np.min(projected_y[finite])),
        float(np.max(projected_x[finite])), float(np.max(projected_y[finite])),
    )
    poles = {pole.id: pole for pole in project.source.poles}
    to_projected = Transformer.from_crs("EPSG:4326", result.projected_crs, always_xy=True)
    height = result.profile_snapshot.measurement_height_m
    for camera in sorted(result.camera_results, key=lambda item: item.footprint_id):
        if not camera.valid or not camera.bands:
            continue
        if any(value is None for value in (
            camera.resolution_width_px, camera.horizontal_fov_deg, camera.fixture_height_m,
            camera.camera_absolute_azimuth_deg, camera.fixed_downward_tilt_deg,
        )):
            continue
        source = poles.get(camera.pole_id)
        if source is None:
            continue
        mask = np.zeros(projected_x.shape, dtype=np.bool_)
        for band in camera.bands:
            for rings in band.projected_rings_m:
                polygon = Polygon(rings[0], holes=rings[1:])
                left, bottom, right, top = polygon.bounds
                if right < bounds[0] or left > bounds[2] or top < bounds[1] or bottom > bounds[3]:
                    continue
                mask |= contains_xy(polygon, projected_x, projected_y)
        mask &= finite
        if not mask.any():
            continue
        edit = project.pole_edits.get(camera.pole_id)
        longitude = edit.longitude if edit and edit.longitude is not None else source.longitude
        latitude = edit.latitude if edit and edit.latitude is not None else source.latitude
        origin_x, origin_y = to_projected.transform(longitude, latitude)
        forward, _, _ = camera_basis(camera.camera_absolute_azimuth_deg, camera.fixed_downward_tilt_deg)
        depth = (
            (projected_x - origin_x) * forward[0]
            + (projected_y - origin_y) * forward[1]
            + (height - camera.fixture_height_m) * forward[2]
        )
        focal_px = camera.resolution_width_px / (2 * math.tan(math.radians(camera.horizontal_fov_deg) / 2))
        density = np.zeros(projected_x.shape, dtype=np.float64)
        np.divide(focal_px * result.profile_snapshot.face_width_m, depth, out=density, where=mask & (depth > 1e-9))
        np.maximum(best, density, out=best)
    return best


def render_heatmap_tile(
    project: Project, legend: PixelDensityLegendDefinition, z: int, x: int, y: int,
) -> bytes:
    """Render exact per-location max camera density into a transparent XYZ PNG."""
    if z < 0 or z > 22 or x < 0 or y < 0 or x >= 1 << z or y >= 1 << z:
        raise ValueError("Invalid camera heatmap tile coordinates")
    layer = project.camera_pixel_density
    if (
        layer.state.status != "current" or layer.result is None
        or layer.state.calculation_input_sha256 != layer.result.calculation_input_sha256
    ):
        return transparent_tile()
    projected_x, projected_y = _projected_tile_centres(layer.result.projected_crs, z, x, y)
    density = _tile_density(project, projected_x, projected_y)
    visible = density >= legend.thresholds[0].minimum
    if not visible.any():
        return transparent_tile()
    rgba = np.zeros((TILE_SIZE, TILE_SIZE, 4), dtype=np.uint8)
    rgba[visible, :3] = interpolate_legend_colours(density[visible], legend)
    rgba[visible, 3] = round(legend.fill_opacity * 255)
    return _png(rgba)
