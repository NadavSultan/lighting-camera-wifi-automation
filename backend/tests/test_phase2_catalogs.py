from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from app.catalog_models import (
    CameraModel,
    CameraMountingTemplateRevision,
    IesFixtureAssociation,
    LensConfiguration,
    camera_absolute_azimuth,
)
from app.models import PoleCameraOverride, PoleEdit, PoleFixtureConfiguration, Project, migrate_project_payload
from app.main import create_app
from app.services.catalogs import CatalogStore
from app.services.configuration import (
    BulkPoleConfigurationPatch,
    BulkPoleConfigurationRequest,
    apply_bulk_configuration,
    validate_project_configuration,
)
from app.services.ies import IesValidationError, parse_ies_upload
from app.services.kml import import_project
from app.services.store import ProjectStore


ROOT = Path(__file__).resolve().parents[2]
SEEDS = ROOT / "data" / "phase2"


def store(tmp_path: Path) -> CatalogStore:
    return CatalogStore(tmp_path / "catalogs", SEEDS)


def sample_project() -> Project:
    source = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
    return import_project(source.name, source.read_bytes())


def test_six_required_fixture_models_and_capability_matrix(tmp_path: Path) -> None:
    catalog = store(tmp_path).fixtures()
    by_id = {item.id: item for item in catalog.fixture_models}
    assert set(by_id) == {
        "phoenix-1-lite", "phoenix-1-wifi", "phoenix-1-smart",
        "solitaire-lite", "solitaire-wifi", "solitaire-smart",
    }
    assert {(item.fixture_family, item.capability_variant.value) for item in by_id.values()} == {
        ("Phoenix 1", "LITE"), ("Phoenix 1", "WIFI"), ("Phoenix 1", "SMART"),
        ("Solitaire", "LITE"), ("Solitaire", "WIFI"), ("Solitaire", "SMART"),
    }
    assert all(item.capabilities.lighting for item in by_id.values())
    assert {item.capability_variant.value for item in by_id.values() if item.capabilities.wifi} == {"WIFI", "SMART"}
    assert {item.id for item in by_id.values() if item.capabilities.cameras} == {"phoenix-1-smart", "solitaire-smart"}
    assert {item.id for item in by_id.values() if item.mounting_template_revisions} == {"phoenix-1-smart", "solitaire-smart"}


@pytest.mark.parametrize(
    ("model_id", "fixture_azimuth", "expected", "separation"),
    [
        ("phoenix-1-smart", 0, [290, 70], 140),
        ("phoenix-1-smart", 90, [20, 160], 140),
        ("solitaire-smart", 0, [300, 60], 120),
        ("solitaire-smart", 90, [30, 150], 120),
    ],
)
def test_smart_mounting_geometry(tmp_path: Path, model_id: str, fixture_azimuth: float, expected: list[float], separation: float) -> None:
    model = next(item for item in store(tmp_path).fixtures().fixture_models if item.id == model_id)
    template = model.current_template()
    assert template is not None
    assert len(template.slots) == 2
    assert [camera_absolute_azimuth(fixture_azimuth, slot.relative_azimuth_deg) for slot in template.slots] == expected
    assert abs(template.slots[1].relative_azimuth_deg - template.slots[0].relative_azimuth_deg) == separation
    assert [slot.downward_tilt_deg for slot in template.slots] == [35, 35]


def test_ies_upload_validation_association_and_default_replacement(tmp_path: Path) -> None:
    catalogs = store(tmp_path)
    phoenix = ROOT / "Input" / "Lighting" / "JLED-SL-100W-PHOENIX1-40-D01.ies"
    record = catalogs.add_ies(parse_ies_upload(phoenix.name, phoenix.read_bytes()))
    assert record.validation_status == "valid"
    assert record.original_filename == phoenix.name
    assert record.parsed_metadata.photometric_type == "C"
    assert record.original_content_base64
    catalogs.associate_ies(IesFixtureAssociation(ies_file_id=record.id, fixture_model_id="phoenix-1-lite"))
    catalogs.associate_ies(IesFixtureAssociation(ies_file_id=record.id, fixture_model_id="phoenix-1-wifi"))
    assert len(catalogs.ies().fixture_associations) == 2
    catalogs.set_default_ies("phoenix-1-lite", record.id)
    assert next(item for item in catalogs.fixtures().fixture_models if item.id == "phoenix-1-lite").default_ies_file_id == record.id

    second = ROOT / "Input" / "Lighting" / "JLED-SL-120W-PHOENIX1-40-D01.IES"
    replacement = catalogs.add_ies(parse_ies_upload(second.name, second.read_bytes()))
    catalogs.associate_ies(IesFixtureAssociation(ies_file_id=replacement.id, fixture_model_id="phoenix-1-lite"))
    catalogs.set_default_ies("phoenix-1-lite", replacement.id)
    model = next(item for item in catalogs.fixtures().fixture_models if item.id == "phoenix-1-lite")
    assert model.default_ies_file_id == replacement.id
    assert record.id in model.compatible_ies_file_ids
    assert replacement.id in model.compatible_ies_file_ids

    deactivated = catalogs.set_ies_active(replacement.id, False)
    assert deactivated.active is False and deactivated.revision == 2
    assert not any(item.active and item.ies_file_id == replacement.id for item in catalogs.ies().fixture_associations)
    assert next(item for item in catalogs.fixtures().fixture_models if item.id == "phoenix-1-lite").default_ies_file_id is None

    with pytest.raises(IesValidationError, match="Unsupported IES format"):
        parse_ies_upload("broken.ies", b"not an ies file")


def test_camera_and_lens_catalog_crud_and_compatibility(tmp_path: Path) -> None:
    catalogs = store(tmp_path)
    camera = CameraModel(id="camera-test", display_name="Test camera", compatible_lens_ids=[])
    catalogs.upsert_camera(camera)
    lens = LensConfiguration(id="lens-test", display_name="Test lens", focal_length_mm=4, compatible_camera_model_ids=["camera-test"])
    catalogs.upsert_lens(lens)
    camera.compatible_lens_ids = ["lens-test"]
    camera.display_name = "Edited camera"
    updated = catalogs.upsert_camera(camera)
    assert updated.revision == 2
    assert next(item for item in catalogs.cameras().camera_models if item.id == "camera-test").display_name == "Edited camera"
    lens.active = False
    assert catalogs.upsert_lens(lens).active is False
    incompatible = copy.deepcopy(camera)
    incompatible.compatible_lens_ids = ["missing"]
    with pytest.raises(ValueError, match="unknown lens"):
        catalogs.upsert_camera(incompatible)


def test_assign_each_fixture_bulk_preserves_coordinates_and_unrelated_values(tmp_path: Path) -> None:
    catalogs = store(tmp_path)
    project = sample_project()
    coordinates = [(pole.id, pole.raw_coordinates, pole.longitude, pole.latitude) for pole in project.source.poles]
    model_ids = [item.id for item in catalogs.fixtures().fixture_models]
    for pole, model_id in zip(project.source.poles[:6], model_ids, strict=True):
        project = apply_bulk_configuration(
            project,
            BulkPoleConfigurationRequest(pole_ids=[pole.id], patch=BulkPoleConfigurationPatch(fixture_model_id=model_id)),
            catalogs.fixtures(),
        )
        assert project.pole_edits[pole.id].fixture_configuration is not None
        assert project.pole_edits[pole.id].fixture_configuration.fixture_model_id == model_id

    targets = [pole.id for pole in project.source.poles[:3]]
    before_configs = {pole_id: copy.deepcopy(project.pole_edits[pole_id].fixture_configuration) for pole_id in targets}
    project = apply_bulk_configuration(
        project,
        BulkPoleConfigurationRequest(pole_ids=targets, patch=BulkPoleConfigurationPatch(pole_height_m=9.5)),
        catalogs.fixtures(),
    )
    assert all(project.pole_edits[pole_id].height_m == 9.5 for pole_id in targets)
    assert all(project.pole_edits[pole_id].fixture_configuration == before_configs[pole_id] for pole_id in targets)
    assert [(pole.id, pole.raw_coordinates, pole.longitude, pole.latitude) for pole in project.source.poles] == coordinates


def test_overrides_are_separate_non_smart_rejected_and_templates_are_pinned(tmp_path: Path) -> None:
    catalogs = store(tmp_path)
    project = sample_project()
    pole_id = project.source.poles[0].id
    project = apply_bulk_configuration(
        project,
        BulkPoleConfigurationRequest(pole_ids=[pole_id], patch=BulkPoleConfigurationPatch(fixture_model_id="phoenix-1-smart")),
        catalogs.fixtures(),
    )
    template_before = catalogs.fixtures().model_dump()
    config = project.pole_edits[pole_id].fixture_configuration
    assert config is not None and config.mounting_template_revision == 1
    config.camera_overrides["camera-1"] = PoleCameraOverride(slot_id="camera-1", relative_azimuth_deg=-65, lens_id="lens-jl-ln039")
    assert catalogs.fixtures().model_dump() == template_before

    model = next(item for item in catalogs.fixtures().fixture_models if item.id == "phoenix-1-smart")
    old = model.current_template()
    assert old is not None
    catalogs.add_template_revision(
        model.id,
        CameraMountingTemplateRevision(revision=2, created_at="2026-08-14T12:00:00Z", notes="Explicit revision", slots=copy.deepcopy(old.slots)),
    )
    assert config.mounting_template_revision == 1

    lite_config = PoleFixtureConfiguration(
        fixture_model_id="phoenix-1-lite", fixture_model_revision=1,
        camera_overrides={"camera-1": PoleCameraOverride(slot_id="camera-1", camera_model_id="camera-imx477")},
    )
    project.pole_edits[pole_id] = PoleEdit(pole_id=pole_id, fixture_configuration=lite_config)
    errors = validate_project_configuration(project, catalogs.fixtures(), catalogs.cameras(), catalogs.ies())
    assert any("non-SMART" in error for error in errors)


def test_phase_one_migration_preserves_coordinates_and_requires_model_selection() -> None:
    project = sample_project()
    pole = project.source.poles[0]
    phase_one = project.model_dump(mode="json")
    phase_one["schema_version"] = "1.0.0"
    phase_one.pop("legacy_fixture_assignments_require_model_selection")
    phase_one["pole_edits"][pole.id] = {"pole_id": pole.id, "fixture_type": "SMART", "location_edit_authorized": False}
    migrated = Project.model_validate(migrate_project_payload(json.loads(json.dumps(phase_one))))
    assert migrated.schema_version == "2.0.0"
    assert migrated.legacy_fixture_assignments_require_model_selection is True
    assert migrated.pole_edits[pole.id].fixture_type.value == "SMART"
    assert migrated.pole_edits[pole.id].fixture_configuration is None
    assert migrated.source.poles[0].raw_coordinates == pole.raw_coordinates
    assert (migrated.source.poles[0].longitude, migrated.source.poles[0].latitude) == (pole.longitude, pole.latitude)


@pytest.mark.parametrize(
    ("schema_name", "data_name"),
    [
        ("fixture-model-catalog.schema.json", "fixture-model-catalog.json"),
        ("camera-equipment-catalog.schema.json", "camera-equipment-catalog.json"),
        ("ies-library.schema.json", "ies-library.json"),
    ],
)
def test_phase_two_seed_catalogs_validate_against_checked_in_contracts(schema_name: str, data_name: str) -> None:
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    data = json.loads((SEEDS / data_name).read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(data)


def test_phase_two_api_catalog_upload_and_bulk_configuration(tmp_path: Path) -> None:
    catalogs = store(tmp_path)
    client = TestClient(create_app(ProjectStore(tmp_path / "projects"), catalogs))
    fixtures = client.get("/api/catalogs/fixtures")
    assert fixtures.status_code == 200
    assert len(fixtures.json()["fixture_models"]) == 6

    ies_path = ROOT / "Input" / "Lighting" / "JLED-SL-100W-PHOENIX1-40-D01.ies"
    upload = client.post("/api/catalogs/ies/upload", content=ies_path.read_bytes(), headers={"Origin": "http://127.0.0.1:3000", "X-Filename": ies_path.name, "Content-Type": "application/octet-stream"})
    assert upload.status_code == 201, upload.text
    assert upload.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    ies_id = upload.json()["id"]
    for fixture_id in ("phoenix-1-smart", "solitaire-smart"):
        response = client.put(f"/api/catalogs/ies/{ies_id}/fixtures/{fixture_id}", json={"active": True})
        assert response.status_code == 200, response.text

    source = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
    imported = client.post("/api/projects/import", content=source.read_bytes(), headers={"X-Filename": source.name, "Content-Type": "application/octet-stream"})
    assert imported.status_code == 201
    project = imported.json()
    pole_ids = [item["id"] for item in project["source"]["poles"][:2]]
    coordinates = [(item["raw_coordinates"], item["longitude"], item["latitude"]) for item in project["source"]["poles"]]
    configured = client.patch(
        f"/api/projects/{project['id']}/poles/bulk",
        json={"pole_ids": pole_ids, "patch": {"fixture_model_id": "phoenix-1-smart", "ies_file_id": ies_id, "pole_height_m": 8.5, "fixture_azimuth_deg": 90, "lens_by_slot": {"camera-1": "lens-jl-ln039", "camera-2": "lens-jl-ln039"}}},
    )
    assert configured.status_code == 200, configured.text
    result = configured.json()
    assert all(result["pole_edits"][pole_id]["fixture_configuration"]["fixture_model_id"] == "phoenix-1-smart" for pole_id in pole_ids)
    assert [(item["raw_coordinates"], item["longitude"], item["latitude"]) for item in result["source"]["poles"]] == coordinates

    lite = client.patch(f"/api/projects/{project['id']}/poles/bulk", json={"pole_ids": [pole_ids[0]], "patch": {"fixture_model_id": "phoenix-1-lite"}})
    assert lite.status_code == 200
    rejected = client.patch(f"/api/projects/{project['id']}/poles/bulk", json={"pole_ids": [pole_ids[0]], "patch": {"camera_model_by_slot": {"camera-1": "camera-imx477"}}})
    assert rejected.status_code == 422
    assert "non-SMART" in rejected.json()["detail"]
