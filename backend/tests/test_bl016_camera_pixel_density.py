from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from shapely.geometry import Polygon

from app.main import create_app
from app.models import (
    CameraPixelDensityBand,
    CameraPixelDensityProfile,
    CameraPixelDensityState,
    PixelDensityLegendDefinition,
    Project,
    SCHEMA_VERSION,
    SOFTWARE_VERSION,
    migrate_project_payload,
)
from app.services.camera_pixel_density import (
    camera_basis,
    camera_coordinates,
    clip_midpoint_density_bands,
    density_band_index,
    distance_cap_polygon,
    horizontal_density_px_per_face,
    project_frustum_plane,
)


SUPPORTED_LEGACY_VERSIONS = (
    "1.0.0",
    "2.0.0",
    "2.1.0",
    "2.2.0",
    "2.3.0",
    "2.4.0",
    "2.5.0",
    "2.6.0",
    "2.7.0",
)


def legacy_project_payload(version: str) -> dict:
    payload = Project().model_dump(mode="json")
    payload["schema_version"] = version
    payload["software_version"] = "legacy"
    payload.pop("camera_pixel_density_profile", None)
    payload.pop("camera_pixel_density", None)
    payload["recommended_layers"]["extension-preserved"] = {"bytes": "unchanged"}
    return payload


@pytest.mark.parametrize("version", SUPPORTED_LEGACY_VERSIONS)
def test_bl016_migration_is_lossless_empty_and_idempotent(version: str) -> None:
    payload = legacy_project_payload(version)
    original_source = copy.deepcopy(payload["source"])
    original_extensions = copy.deepcopy(payload["recommended_layers"])

    migrated = migrate_project_payload(payload)

    assert migrated["schema_version"] == "2.8.0" == SCHEMA_VERSION
    assert migrated["software_version"] == "0.8.0" == SOFTWARE_VERSION
    assert migrated["source"] == original_source
    assert migrated["recommended_layers"] == original_extensions
    assert migrated["camera_pixel_density_profile"] == {
        "lower_projection_height_m": 0.5,
        "upper_projection_height_m": 2.0,
        "measurement_height_mode": "midpoint",
        "maximum_visible_distance_m": 50.0,
        "legend_id": "face-density-0.16m-v1",
    }
    assert migrated["camera_pixel_density"] == {
        "state": {"status": "not-calculated", "calculation_input_sha256": None, "message": None},
        "result": None,
    }
    assert migrated["layer_state"]["camera_pixel_density"] is False
    assert migrate_project_payload(copy.deepcopy(migrated)) == migrated
    Project.model_validate(migrated)


@pytest.mark.parametrize(
    "payload",
    [
        {"lower_projection_height_m": math.nan},
        {"upper_projection_height_m": math.inf},
        {"lower_projection_height_m": 2.0, "upper_projection_height_m": 2.0},
        {"lower_projection_height_m": 3.0, "upper_projection_height_m": 2.0},
        {"maximum_visible_distance_m": 0.0},
        {"maximum_visible_distance_m": -1.0},
        {"legend_id": "invented"},
    ],
)
def test_bl016_profile_rejects_invalid_values(payload: dict) -> None:
    with pytest.raises(ValidationError):
        CameraPixelDensityProfile.model_validate(payload)


def test_bl016_state_and_band_validation_rejects_malformed_values() -> None:
    with pytest.raises(ValidationError):
        CameraPixelDensityState(status="unknown")
    with pytest.raises(ValidationError):
        CameraPixelDensityState(status="current", calculation_input_sha256="bad")
    with pytest.raises(ValidationError):
        CameraPixelDensityBand(
            band_id="px-face-2",
            legend_id="face-density-0.16m-v1",
            rank=1,
            minimum_px_per_face=2,
            maximum_px_per_face=3,
            display_value_px_per_face=2,
            colour_token="face-density-2",
            projected_rings_m=[[[[0, 0], [1, 0], [1, 1], [0, 0.5]]]],
            wgs84_rings=[[[[-80, 25], [-79.9, 25], [-79.9, 25.1], [-80, 25.05]]]],
            area_m2=1,
        )
    with pytest.raises(ValidationError):
        CameraPixelDensityBand(
            band_id="px-face-2",
            legend_id="face-density-0.16m-v1",
            rank=1,
            minimum_px_per_face=2,
            maximum_px_per_face=3,
            display_value_px_per_face=2,
            colour_token="face-density-2",
            projected_rings_m=[],
            wgs84_rings=[],
            area_m2=-1,
        )


def test_bl016_canonical_legend_file_and_endpoint() -> None:
    root = Path(__file__).resolve().parents[2]
    payload = json.loads((root / "data/cameras/camera-pixel-density-legend.json").read_text(encoding="utf-8"))
    legend = PixelDensityLegendDefinition.model_validate(payload)

    assert legend.id == "face-density-0.16m-v1"
    assert legend.display_units == "px/face"
    assert legend.object_width_m == 0.16
    assert legend.fill_opacity == 0.58
    assert [row.minimum for row in legend.thresholds] == [2, 3, 5, 7, 10, 15, 20, 30, 45, 70]
    assert [row.colour for row in legend.thresholds] == [
        "#c7f9ff", "#8fe7f2", "#4cc9f0", "#3a86ff", "#2fb344",
        "#8bc34a", "#ffd43b", "#ff922b", "#f03e3e", "#d633ff",
    ]
    response = TestClient(create_app()).get("/api/reference/camera-pixel-density-legend")
    assert response.status_code == 200
    assert response.json() == payload


@pytest.mark.parametrize(("horizontal_fov_deg", "expected"), [
    (52.0, 66.528259051565),
    (69.0, 47.212132962364),
    (87.0, 34.193057505117),
])
def test_bl016_reference_lens_density(horizontal_fov_deg: float, expected: float) -> None:
    assert horizontal_density_px_per_face(4056, horizontal_fov_deg, 10.0) == pytest.approx(expected, abs=1e-12)


@pytest.mark.parametrize(("azimuth", "expected_forward"), [
    (0.0, (0.0, math.cos(math.radians(35)), -math.sin(math.radians(35)))),
    (90.0, (math.cos(math.radians(35)), 0.0, -math.sin(math.radians(35)))),
    (180.0, (0.0, -math.cos(math.radians(35)), -math.sin(math.radians(35)))),
    (270.0, (-math.cos(math.radians(35)), 0.0, -math.sin(math.radians(35)))),
    (360.0, (0.0, math.cos(math.radians(35)), -math.sin(math.radians(35)))),
])
def test_bl016_camera_basis_quadrants_and_wraparound(azimuth: float, expected_forward: tuple[float, float, float]) -> None:
    forward, right, image_up = camera_basis(azimuth, 35.0)
    assert forward == pytest.approx(expected_forward, abs=1e-12)
    assert sum(value * value for value in forward) == pytest.approx(1.0)
    assert sum(a * b for a, b in zip(forward, right, strict=True)) == pytest.approx(0.0, abs=1e-12)
    assert sum(value * value for value in image_up) == pytest.approx(1.0)


def test_bl016_camera_coordinates_front_behind_and_depth_tolerance() -> None:
    basis = camera_basis(0.0, 35.0)
    origin = (100.0, 200.0, 8.0)
    front = tuple(origin[index] + 10 * basis[0][index] for index in range(3))
    behind = tuple(origin[index] - 10 * basis[0][index] for index in range(3))
    assert camera_coordinates(front, origin, *basis)[2] == pytest.approx(10.0, abs=1e-12)
    assert camera_coordinates(behind, origin, *basis)[2] == pytest.approx(-10.0)
    with pytest.raises(ValueError, match="greater than 1e-9"):
        horizontal_density_px_per_face(4056, 52, 1e-9)


@pytest.mark.parametrize("args", [(0, 52, 10), (4056, 0, 10), (4056, 180, 10), (4056, math.inf, 10), (4056, 52, math.nan)])
def test_bl016_density_rejects_invalid_inputs(args: tuple[float, float, float]) -> None:
    with pytest.raises(ValueError):
        horizontal_density_px_per_face(*args)


def test_bl016_camera_primitives_reject_non_finite_inputs() -> None:
    with pytest.raises(ValueError):
        camera_basis(math.nan, 35)
    with pytest.raises(ValueError):
        camera_coordinates((math.inf, 0, 0), (0, 0, 0), *camera_basis(0, 35))


@pytest.mark.parametrize("threshold", [2, 3, 5, 7, 10, 15, 20, 30, 45, 70])
def test_bl016_threshold_boundaries(threshold: float) -> None:
    thresholds = [2, 3, 5, 7, 10, 15, 20, 30, 45, 70]
    expected = thresholds.index(threshold)
    assert density_band_index(threshold - 0.5e-9, thresholds) == expected
    assert density_band_index(threshold, thresholds) == expected
    above = density_band_index(threshold + 1e-6, thresholds)
    assert above == expected
    below = density_band_index(threshold - 1e-6, thresholds)
    assert below == (expected - 1 if expected else None)
    assert density_band_index(70, thresholds) == density_band_index(1000, thresholds) == 9
    assert density_band_index(1.999999, thresholds) is None


def test_bl016_projection_planes_midpoint_cap_and_band_partition() -> None:
    legend_path = Path(__file__).resolve().parents[2] / "data/cameras/camera-pixel-density-legend.json"
    legend = PixelDensityLegendDefinition.model_validate_json(legend_path.read_text(encoding="utf-8"))
    profile = CameraPixelDensityProfile()
    assert profile.measurement_height_m == 1.25
    origin = (0.0, 0.0, 8.0)
    forward, right, image_up = camera_basis(0.0, 35.0)
    lower = project_frustum_plane(origin, forward, right, image_up, 52.0, 40.0, profile.lower_projection_height_m)
    midpoint = project_frustum_plane(origin, forward, right, image_up, 52.0, 40.0, profile.measurement_height_m)
    upper = project_frustum_plane(origin, forward, right, image_up, 52.0, 40.0, profile.upper_projection_height_m)
    for polygon in (lower, midpoint, upper):
        assert polygon.is_valid and polygon.exterior.is_ccw
        assert polygon.exterior.coords[0] == polygon.exterior.coords[-1]
    cap = distance_cap_polygon(0, 0, 50)
    assert len(cap.exterior.coords) == 129
    assert cap.exterior.coords[0] == pytest.approx((0.0, 50.0), abs=1e-9)
    assert cap.exterior.is_ccw
    assert all(math.hypot(x, y) == pytest.approx(50.0, abs=1e-9) for x, y in list(cap.exterior.coords)[:-1])
    domain = midpoint.intersection(cap)
    focal_length_px = 4056 / (2 * math.tan(math.radians(52) / 2))
    bands = clip_midpoint_density_bands(
        domain,
        origin_xyz_m=origin,
        forward=forward,
        measurement_height_m=profile.measurement_height_m,
        focal_length_px=focal_length_px,
        legend=legend,
    )
    assert bands
    assert all(left.geometry.intersection(right.geometry).area <= 1e-8 for index, left in enumerate(bands) for right in bands[index + 1 :])
    assert sum(band.geometry.area for band in bands) == pytest.approx(domain.area, abs=1e-6)


def test_bl016_plane_and_cap_reject_invalid_geometry() -> None:
    origin = (0.0, 0.0, 8.0)
    forward, right, image_up = camera_basis(0.0, 35.0)
    with pytest.raises(ValueError):
        project_frustum_plane(origin, forward, right, image_up, 52.0, 40.0, 20.0)
    with pytest.raises(ValueError):
        project_frustum_plane(origin, forward, right, image_up, 180.0, 40.0, 1.25)
    with pytest.raises(ValueError):
        distance_cap_polygon(0, 0, 0)
    widest = project_frustum_plane(origin, forward, right, image_up, 87.0, 68.0, 1.25).intersection(distance_cap_polygon(0, 0, 50))
    assert all(math.hypot(x, y) <= 50.0 + 1e-9 for x, y in widest.exterior.coords)
