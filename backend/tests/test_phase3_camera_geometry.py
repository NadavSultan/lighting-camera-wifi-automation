from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from pyproj import Transformer
from pyproj.exceptions import ProjError

from app.catalog_models import camera_absolute_azimuth, normalize_azimuth
from app.crs import project_transformers, validate_projected_metre_crs
from app.models import CalculationArea, PriorityArea, Project, migrate_project_payload
from app.main import create_app
from app.services.camera_geometry import calculate_camera_geometry, camera_calculation_input_sha256, canonical_ring, project_ground_footprint
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


def test_camera_calculation_persists_input_fingerprint_without_migration_invention(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = configure(miracle_project(), store, [miracle_project().source.poles[0].id])
    layer = calculate_camera_geometry(project, store.fixtures(), store.cameras())
    assert layer.calculation_input_sha256 == camera_calculation_input_sha256(project)
    assert len(layer.calculation_input_sha256) == 64
    migrated = migrate_project_payload({
        **project.model_dump(mode="json"),
        "schema_version": "2.2.0",
        "camera_geometry": {"calculated_at": layer.calculated_at.isoformat(), "footprints": []},
    })
    assert "calculation_input_sha256" not in migrated["camera_geometry"] or migrated["camera_geometry"].get("calculation_input_sha256") is None
    validated = Project.model_validate({**migrated, "camera_geometry": {"calculated_at": layer.calculated_at.isoformat(), "footprints": []}})
    assert validated.camera_geometry.calculation_input_sha256 is None


def test_camera_geometry_crs_boundary_preserves_approved_behavior(tmp_path: Path) -> None:
    store = catalogs(tmp_path)
    project = miracle_project()
    project = configure(project, store, [project.source.poles[0].id])

    valid = calculate_camera_geometry(project, store.fixtures(), store.cameras())
    assert valid.projected_crs == "EPSG:32617"
    assert len(valid.footprints) == 2
    assert all(footprint.valid for footprint in valid.footprints)

    for unsupported in ("NOT-A-CRS", "EPSG:4326", "EPSG:2263"):
        with pytest.raises(ValidationError, match="[Pp]roject engineering CRS"):
            Project.model_validate({**project.model_dump(mode="json"), "projected_crs": unsupported})
        bypassed = project.model_copy(update={"projected_crs": unsupported})
        with pytest.raises(ValueError, match="[Pp]roject engineering CRS"):
            calculate_camera_geometry(bypassed, store.fixtures(), store.cameras())

    missing = calculate_camera_geometry(Project(), store.fixtures(), store.cameras())
    assert missing.projected_crs is None and missing.footprints == []


def test_project_transformer_construction_translates_only_expected_pyproj_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    crs = validate_projected_metre_crs("EPSG:32617")

    def expected_failure(*args, **kwargs):
        raise ProjError("controlled construction failure")

    monkeypatch.setattr("app.crs.Transformer.from_crs", expected_failure)
    with pytest.raises(ValueError, match="Could not construct transformations"):
        project_transformers(crs)

    def unexpected_failure(*args, **kwargs):
        raise RuntimeError("programming defect")

    monkeypatch.setattr("app.crs.Transformer.from_crs", unexpected_failure)
    with pytest.raises(RuntimeError, match="programming defect"):
        project_transformers(crs)


@pytest.mark.parametrize("invalid_crs", ["NOT-A-CRS", "EPSG:4326", "EPSG:2263"])
def test_unsupported_project_crs_is_controlled_across_every_shared_api_path_and_preserves_exact_state(
    tmp_path: Path, invalid_crs: str
) -> None:
    catalog_store = catalogs(tmp_path)
    project_store = ProjectStore(tmp_path / "projects")
    project = miracle_project()
    project = configure(project, catalog_store, [project.source.poles[0].id])
    to_projected = Transformer.from_crs("EPSG:4326", project.projected_crs, always_xy=True)
    to_wgs84 = Transformer.from_crs(project.projected_crs, "EPSG:4326", always_xy=True)
    center_x, center_y = to_projected.transform(project.source.poles[0].longitude, project.source.poles[0].latitude)
    project.calculation_areas = [CalculationArea(
        id="crs-area", name="CRS regression area", classification="OTHER", grid_spacing_m=2,
        wgs84_coordinates=[to_wgs84.transform(x, y) for x, y in (
            (center_x - 2.1, center_y - 2.1), (center_x + 2.1, center_y - 2.1),
            (center_x + 2.1, center_y + 2.1), (center_x - 2.1, center_y + 2.1),
            (center_x - 2.1, center_y - 2.1),
        )],
    )]
    project_store.save(project)
    client = TestClient(create_app(project_store, catalog_store))
    valid_payload = project.model_dump(mode="json")
    valid_save = client.put(f"/api/projects/{project.id}", json=valid_payload)
    assert valid_save.status_code == 200, valid_save.text
    assert len(valid_save.json()["camera_geometry"]["footprints"]) == 2
    valid_payload = valid_save.json()
    project_path = project_store.root / project.id / "project.json"
    prior_valid_bytes = project_path.read_bytes()

    invalid_payload = copy.deepcopy(valid_payload)
    invalid_payload["projected_crs"] = invalid_crs

    save_response = client.put(f"/api/projects/{project.id}", json=invalid_payload)
    assert save_response.status_code == 422
    assert "project engineering crs" in save_response.text.lower()
    assert project_path.read_bytes() == prior_valid_bytes

    project_count = len(project_store.list())
    open_payload = copy.deepcopy(invalid_payload)
    open_payload["id"] = f"invalid-open-{invalid_crs.split(':')[-1].lower().replace('-', '_')}"
    open_response = client.post("/api/projects/open", json=open_payload)
    assert open_response.status_code == 422
    assert "project engineering crs" in open_response.text.lower()
    assert len(project_store.list()) == project_count
    assert project_path.read_bytes() == prior_valid_bytes
    assert not (project_store.root / open_payload["id"]).exists()

    camera_response = client.post(f"/api/projects/{project.id}/camera-geometry/recalculate", json=invalid_payload)
    assert camera_response.status_code == 422
    assert "project engineering crs" in camera_response.text.lower()
    assert project_path.read_bytes() == prior_valid_bytes

    lighting_response = client.post(f"/api/projects/{project.id}/lighting/calculate/crs-area", json=invalid_payload)
    assert lighting_response.status_code == 422
    assert "project engineering crs" in lighting_response.text.lower()
    assert project_path.read_bytes() == prior_valid_bytes

    corrupt_payload = copy.deepcopy(invalid_payload)
    corrupt_payload["id"] = f"invalid-stored-{invalid_crs.split(':')[-1].lower().replace('-', '_')}"
    corrupt_path = project_store.root / corrupt_payload["id"] / "project.json"
    corrupt_path.parent.mkdir(parents=True)
    corrupt_path.write_text(json.dumps(corrupt_payload, indent=2), encoding="utf-8")
    corrupt_bytes = corrupt_path.read_bytes()

    get_response = client.get(f"/api/projects/{corrupt_payload['id']}")
    assert get_response.status_code == 422
    assert "Stored project is invalid or corrupt" in get_response.json()["detail"]
    assert "project engineering crs" in get_response.json()["detail"].lower()
    assert corrupt_path.read_bytes() == corrupt_bytes

    bulk_response = client.patch(
        f"/api/projects/{corrupt_payload['id']}/poles/bulk",
        json={"pole_ids": [project.source.poles[0].id], "patch": {"pole_height_m": 12}},
    )
    assert bulk_response.status_code == 422
    assert "project engineering crs" in bulk_response.json()["detail"].lower()
    assert corrupt_path.read_bytes() == corrupt_bytes
    assert project_path.read_bytes() == prior_valid_bytes


def test_projected_metre_crs_and_missing_crs_contract_remain_operational_across_shared_paths(tmp_path: Path) -> None:
    catalog_store = catalogs(tmp_path)
    project_store = ProjectStore(tmp_path / "projects")
    client = TestClient(create_app(project_store, catalog_store))

    blank = client.post("/api/projects", json={"name": "Blank project without source"})
    assert blank.status_code == 201 and blank.json()["projected_crs"] is None
    assert client.get(f"/api/projects/{blank.json()['id']}").status_code == 200

    project = miracle_project()
    project = configure(project, catalog_store, [project.source.poles[0].id])
    to_projected = Transformer.from_crs("EPSG:4326", "EPSG:32617", always_xy=True)
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    center_x, center_y = to_projected.transform(project.source.poles[0].longitude, project.source.poles[0].latitude)
    project.calculation_areas = [CalculationArea(
        id="valid-area", name="Valid projected-metre area", classification="OTHER", grid_spacing_m=2,
        wgs84_coordinates=[to_wgs84.transform(x, y) for x, y in (
            (center_x - 2.1, center_y - 2.1), (center_x + 2.1, center_y - 2.1),
            (center_x + 2.1, center_y + 2.1), (center_x - 2.1, center_y + 2.1),
            (center_x - 2.1, center_y - 2.1),
        )],
    )]
    project_store.save(project)
    payload = project.model_dump(mode="json")

    saved = client.put(f"/api/projects/{project.id}", json=payload)
    assert saved.status_code == 200 and saved.json()["projected_crs"] == "EPSG:32617"
    assert len(saved.json()["camera_geometry"]["footprints"]) == 2
    fetched = client.get(f"/api/projects/{project.id}")
    assert fetched.status_code == 200 and len(fetched.json()["camera_geometry"]["footprints"]) == 2
    bulk = client.patch(f"/api/projects/{project.id}/poles/bulk", json={
        "pole_ids": [project.source.poles[0].id], "patch": {"pole_height_m": 11},
    })
    assert bulk.status_code == 200 and len(bulk.json()["camera_geometry"]["footprints"]) == 2
    recalculated = client.post(f"/api/projects/{project.id}/camera-geometry/recalculate", json=bulk.json())
    assert recalculated.status_code == 200 and all(
        item["valid"] for item in recalculated.json()["camera_geometry"]["footprints"]
    )
    lighting = client.post(f"/api/projects/{project.id}/lighting/calculate/valid-area", json=recalculated.json())
    assert lighting.status_code == 200, lighting.text
    assert lighting.json()["lighting_calculations"]["results"]["valid-area"]["statistics"]["point_count"] > 0

    reopened_payload = copy.deepcopy(lighting.json())
    reopened_payload["id"] = "valid-open-epsg-32617"
    reopened = client.post("/api/projects/open", json=reopened_payload)
    assert reopened.status_code == 200, reopened.text
    assert reopened.json()["projected_crs"] == "EPSG:32617"
    assert len(reopened.json()["camera_geometry"]["footprints"]) == 2
    assert reopened.json()["lighting_calculations"]["results"]["valid-area"]["statistics"]["point_count"] > 0



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
    assert migrated_payload["schema_version"] == "2.7.0"
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
