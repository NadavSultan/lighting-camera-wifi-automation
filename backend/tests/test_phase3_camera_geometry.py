from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.catalog_models import camera_absolute_azimuth, normalize_azimuth
from app.models import PriorityArea, Project, migrate_project_payload
from app.main import create_app
from app.services.camera_geometry import calculate_camera_geometry, canonical_ring, project_ground_footprint
from app.services.catalogs import CatalogStore
from app.services.configuration import BulkPoleConfigurationPatch, BulkPoleConfigurationRequest, apply_bulk_configuration
from app.services.kml import import_project
from app.services.store import ProjectStore


ROOT = Path(__file__).resolve().parents[2]
SEEDS = ROOT / "data" / "phase2"


def catalogs(tmp_path: Path) -> CatalogStore:
    return CatalogStore(tmp_path / "catalogs", SEEDS)


def miracle_project() -> Project:
    source = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
    return import_project(source.name, source.read_bytes(), "Phase 3 geometry")


def configure(project: Project, store: CatalogStore, pole_ids: list[str], fixture="phoenix-1-smart", lens="lens-jl-ln037", height=10.0, azimuth=0.0) -> Project:
    return apply_bulk_configuration(
        project,
        BulkPoleConfigurationRequest(pole_ids=pole_ids, patch=BulkPoleConfigurationPatch(
            fixture_model_id=fixture, pole_height_m=height, fixture_azimuth_deg=azimuth,
            lens_by_slot={"camera-1": lens, "camera-2": lens},
        )), store.fixtures(), store.cameras(),
    )


@pytest.mark.parametrize(("fixture", "relative", "expected"), [
    (0, -70, 290), (0, 70, 70), (90, -70, 20), (90, 70, 160), (350, -70, 280), (350, 70, 60),
    (0, -60, 300), (0, 60, 60), (90, -60, 30), (90, 60, 150), (350, -60, 290), (350, 60, 50),
])
def test_angle_normalization_and_approved_examples(fixture: float, relative: float, expected: float) -> None:
    assert camera_absolute_azimuth(fixture, relative) == expected
    assert normalize_azimuth(360) == 0
    assert 0 <= camera_absolute_azimuth(fixture, relative) < 360


@pytest.mark.parametrize(("hfov", "vfov"), [(52, 40), (69, 54), (87, 68)])
@pytest.mark.parametrize(("height", "azimuth"), [(4.0, 0.0), (10.0, 90.0), (18.0, 359.0)])
def test_projected_crs_ray_ground_intersection_is_deterministic_for_all_lenses(hfov: float, vfov: float, height: float, azimuth: float) -> None:
    ring = project_ground_footprint(500000, 2848000, height, azimuth, 35, hfov, vfov)
    assert ring[0] == ring[-1] and len(ring) == 5
    assert ring == canonical_ring(ring[:-1])
    assert all(math.isfinite(value) for point in ring for value in point)
    assert project_ground_footprint(500000, 2848000, height, azimuth, 35, hfov, vfov) == ring


@pytest.mark.parametrize(("tilt", "vfov", "message"), [
    (0, 40, "horizontal, upward"), (10, 40, "horizontal, upward"), (35, 180, "invalid height"),
])
def test_invalid_horizontal_upward_and_degenerate_rays_return_no_fabricated_polygon(tilt: float, vfov: float, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        project_ground_footprint(0, 0, 10, 0, tilt, 52, vfov)
    with pytest.raises(ValueError, match="non-finite"):
        project_ground_footprint(0, 0, math.nan, 0, 35, 52, 40)


def test_rotation_moves_both_cameras_together_preserving_template_separation_and_coordinates(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    pole = project.source.poles[0]
    original = (pole.id, pole.raw_coordinates, pole.longitude, pole.latitude)
    project = configure(project, store, [pole.id], azimuth=10)
    first = calculate_camera_geometry(project, store.fixtures(), store.cameras())
    project.pole_edits[pole.id].fixture_configuration.fixture_azimuth_deg = 100  # type: ignore[union-attr]
    second = calculate_camera_geometry(project, store.fixtures(), store.cameras())
    assert [item.camera_absolute_azimuth_deg for item in first.footprints] == [300, 80]
    assert [item.camera_absolute_azimuth_deg for item in second.footprints] == [30, 170]
    assert (second.footprints[1].camera_absolute_azimuth_deg - second.footprints[0].camera_absolute_azimuth_deg) % 360 == 140
    assert (pole.id, pole.raw_coordinates, pole.longitude, pole.latitude) == original


def test_camera_geometry_crs_boundary_preserves_approved_behavior(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    project = configure(project, store, [project.source.poles[0].id])

    valid = calculate_camera_geometry(project, store.fixtures(), store.cameras())
    assert valid.projected_crs == "EPSG:32617"
    assert len(valid.footprints) == 2
    assert all(footprint.valid for footprint in valid.footprints)

    for unsupported in ("EPSG:4326", "EPSG:2263"):
        project.projected_crs = unsupported
        empty = calculate_camera_geometry(project, store.fixtures(), store.cameras())
        assert empty.projected_crs == unsupported
        assert empty.footprints == []

    project.projected_crs = "NOT-A-CRS"
    with pytest.raises(ValueError, match="Invalid projected CRS for camera geometry: NOT-A-CRS"):
        calculate_camera_geometry(project, store.fixtures(), store.cameras())


def test_invalid_camera_crs_is_controlled_across_shared_api_paths_and_preserves_store(tmp_path: Path) -> None:
    catalog_store = catalogs(tmp_path)
    project_store = ProjectStore(tmp_path / "projects")
    project = miracle_project()
    project_store.save(project)
    client = TestClient(create_app(project_store, catalog_store))
    valid_payload = project.model_dump(mode="json")
    invalid_payload = copy.deepcopy(valid_payload)
    invalid_payload["projected_crs"] = "NOT-A-CRS"

    save_response = client.put(f"/api/projects/{project.id}", json=invalid_payload)
    assert save_response.status_code == 422
    assert save_response.json()["detail"] == "Invalid projected CRS for camera geometry: NOT-A-CRS"
    assert project_store.load(project.id).projected_crs == "EPSG:32617"

    project_count = len(project_store.list())
    invalid_open_project = Project(name="Invalid CRS open probe", projected_crs="NOT-A-CRS")
    open_response = client.post("/api/projects/open", json=invalid_open_project.model_dump(mode="json"))
    assert open_response.status_code == 422
    assert open_response.json()["detail"] == "Invalid projected CRS for camera geometry: NOT-A-CRS"
    assert len(project_store.list()) == project_count
    assert project_store.load(project.id).projected_crs == "EPSG:32617"
    assert not (project_store.root / invalid_open_project.id).exists()

    camera_response = client.post(f"/api/projects/{project.id}/camera-geometry/recalculate", json=invalid_payload)
    assert camera_response.status_code == 422
    assert camera_response.json()["detail"] == "Invalid projected CRS for camera geometry: NOT-A-CRS"
    assert project_store.load(project.id).projected_crs == "EPSG:32617"

    project_path = project_store.root / project.id / "project.json"
    project_path.write_text(json.dumps(invalid_payload), encoding="utf-8")
    corrupt_bytes = project_path.read_bytes()

    get_response = client.get(f"/api/projects/{project.id}")
    assert get_response.status_code == 422
    assert "Stored project is invalid or corrupt: Invalid projected CRS for camera geometry: NOT-A-CRS" == get_response.json()["detail"]

    bulk_response = client.patch(
        f"/api/projects/{project.id}/poles/bulk",
        json={"pole_ids": [project.source.poles[0].id], "patch": {"pole_height_m": 12}},
    )
    assert bulk_response.status_code == 422
    assert bulk_response.json()["detail"] == "Invalid projected CRS for camera geometry: NOT-A-CRS"
    assert project_path.read_bytes() == corrupt_bytes

    project_store.save(project)
    valid_response = client.put(f"/api/projects/{project.id}", json=valid_payload)
    assert valid_response.status_code == 200
    assert valid_response.json()["projected_crs"] == "EPSG:32617"


def test_fixed_zero_origin_provenance_missing_data_disabled_and_legacy_override_policy(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    pole_id = project.source.poles[0].id
    project = configure(project, store, [pole_id], lens="lens-jl-ln039")
    layer = calculate_camera_geometry(project, store.fixtures(), store.cameras())
    assert all(item.valid and item.origin_offset_xyz_m == (0, 0, 0) for item in layer.footprints)
    assert all(item.fixture_model_revision == 2 and item.mounting_template_revision == 2 for item in layer.footprints)
    assert all(item.camera_model_revision == 1 and item.lens_revision == 1 for item in layer.footprints)
    assert all(item.horizontal_fov_deg == 52 and item.vertical_fov_deg == 40 for item in layer.footprints)
    assert all(item.geometry_contract_version == "fixed-zero-origin-1.0.0" for item in layer.footprints)
    assert all(item.pixel_density.value is None and item.pixel_density.method == "not-calculated" for item in layer.footprints)

    config = project.pole_edits[pole_id].fixture_configuration
    assert config
    config.camera_overrides["camera-1"].lens_id = None
    config.camera_overrides["camera-1"].lens_revision = None
    project.pole_edits[pole_id].height_m = None
    missing = calculate_camera_geometry(project, store.fixtures(), store.cameras()).footprints[0]
    assert not missing.valid and missing.projected_coordinates_m is None
    assert any("height" in warning for warning in missing.warnings)
    assert any("lens" in warning for warning in missing.warnings)

    project.pole_edits[pole_id].height_m = 10
    config.camera_overrides["camera-1"].enabled = False
    disabled = calculate_camera_geometry(project, store.fixtures(), store.cameras()).footprints[0]
    assert not disabled.valid and disabled.warnings == [] and disabled.projected_coordinates_m is None
    config.camera_overrides["camera-1"].enabled = True
    config.camera_overrides["camera-1"].lens_id = "lens-jl-ln039"
    config.camera_overrides["camera-1"].lens_revision = 1
    config.camera_overrides["camera-1"].relative_azimuth_deg = -65
    legacy = calculate_camera_geometry(project, store.fixtures(), store.cameras()).footprints[0]
    assert not legacy.valid and any("Legacy" in warning for warning in legacy.warnings)
    assert config.camera_overrides["camera-1"].relative_azimuth_deg == -65
    config.fixture_model_revision = 999
    missing_revision = calculate_camera_geometry(project, store.fixtures(), store.cameras()).footprints[0]
    assert not missing_revision.valid and missing_revision.projected_coordinates_m is None
    assert any("fixture model revision" in warning for warning in missing_revision.warnings)


def test_overlap_priority_intersection_and_save_reopen_coordinate_integrity(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    coordinates = [(pole.id, pole.raw_coordinates, pole.longitude, pole.latitude) for pole in project.source.poles]
    project = configure(project, store, [project.source.poles[0].id, project.source.poles[1].id])
    initial = calculate_camera_geometry(project, store.fixtures(), store.cameras())
    assert initial.overlaps and all(item.intersection_area_m2 > 0 for item in initial.overlaps)
    first = next(item for item in initial.footprints if item.valid)
    project.priority_areas = [PriorityArea(id="priority-1", name="Camera one footprint", wgs84_coordinates=first.wgs84_coordinates)]  # type: ignore[arg-type]
    project.camera_geometry = calculate_camera_geometry(project, store.fixtures(), store.cameras())
    summary = project.camera_geometry.priority_area_summaries[0]
    assert summary.area_m2 > 0 and summary.covered_percentage == pytest.approx(100, abs=1e-4)
    assert f"{first.pole_id}/{first.camera_slot_id}" in summary.intersecting_footprint_ids
    reopened = Project.model_validate_json(project.model_dump_json())
    assert reopened.priority_areas == project.priority_areas
    assert reopened.camera_geometry == project.camera_geometry
    assert [(pole.id, pole.raw_coordinates, pole.longitude, pole.latitude) for pole in reopened.source.poles] == coordinates


@pytest.mark.parametrize("version", ["1.0.0", "2.0.0", "2.1.0", "2.2.0"])
def test_phase3_additive_migrations_preserve_legacy_orientation_bytes(version: str) -> None:
    project = miracle_project()
    pole_id = project.source.poles[0].id
    payload = project.model_dump(mode="json")
    payload["schema_version"] = version
    payload.pop("priority_areas", None)
    payload.pop("camera_geometry", None)
    payload["pole_edits"][pole_id] = {"pole_id": pole_id, "fixture_type": "SMART", "location_edit_authorized": False, "fixture_configuration": {"fixture_model_id": "phoenix-1-smart", "fixture_model_revision": 1, "mounting_template_revision": 1, "fixture_azimuth_deg": 0, "lighting_properties": {}, "wifi_configuration": {}, "camera_overrides": {"camera-1": {"slot_id": "camera-1", "relative_azimuth_deg": -65, "downward_tilt_deg": 30, "metadata": {"legacy": "preserve"}}}}}
    migrated_payload = migrate_project_payload(copy.deepcopy(payload))
    assert migrated_payload["schema_version"] == "2.4.0"
    assert migrated_payload["pole_edits"][pole_id]["fixture_configuration"]["camera_overrides"]["camera-1"] == payload["pole_edits"][pole_id]["fixture_configuration"]["camera_overrides"]["camera-1"]
    assert migrated_payload["priority_areas"] == [] and migrated_payload["camera_geometry"] == {}


def test_priority_area_validation_and_lossless_legacy_quarantine() -> None:
    with pytest.raises(ValueError, match="invalid|self-intersection"):
        PriorityArea(id="bad", name="Bow tie", wgs84_coordinates=[(0, 0), (1, 1), (0, 1), (1, 0), (0, 0)])
    project = miracle_project().model_dump(mode="json")
    project["schema_version"] = "2.2.0"
    invalid = {"id": "bad", "name": "Bow tie", "wgs84_coordinates": [[0, 0], [1, 1], [0, 1], [1, 0], [0, 0]], "created_at": project["created_at"], "modified_at": project["updated_at"]}
    project["priority_areas"] = [invalid]
    migrated = migrate_project_payload(copy.deepcopy(project))
    assert migrated["priority_areas"] == []
    assert migrated["legacy_invalid_priority_areas"] == [invalid]


def test_project_schema_and_openapi_are_exactly_fresh_in_memory() -> None:
    project_schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", **Project.model_json_schema()}
    assert json.loads((ROOT / "schemas" / "project.schema.json").read_text(encoding="utf-8")) == project_schema
    assert json.loads((ROOT / "schemas" / "openapi.json").read_text(encoding="utf-8")) == create_app().openapi()


def test_project_summary_aggregates_enabled_camera_warnings_only(tmp_path: Path) -> None:
    catalog_store = catalogs(tmp_path)
    project = configure(miracle_project(), catalog_store, [miracle_project().source.poles[0].id])
    pole_id = project.source.poles[0].id
    project.pole_edits[pole_id].height_m = None
    project.defaults.pole_height_m = None
    project.pole_edits[pole_id].fixture_configuration.camera_overrides["camera-2"].enabled = False  # type: ignore[union-attr]
    project.camera_geometry = calculate_camera_geometry(project, catalog_store.fixtures(), catalog_store.cameras())
    project_store = ProjectStore(tmp_path / "projects")
    project_store.save(project)
    assert project_store.list()[0].warning_count == 1
