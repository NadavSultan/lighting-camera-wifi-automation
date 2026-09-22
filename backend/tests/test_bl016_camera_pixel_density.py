from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

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
