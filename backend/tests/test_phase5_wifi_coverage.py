from __future__ import annotations

import copy
from pathlib import Path

import pytest
from pyproj import Transformer
from fastapi.testclient import TestClient
from shapely.geometry import Point

from app.main import create_app
from app.models import FixtureType, PoleEdit, Project, SourceLayer, SourcePole, WifiAnalysisArea, migrate_project_payload
from app.services.catalogs import CatalogStore
from app.services.store import ProjectStore
from app.services.configuration import BulkPoleConfigurationPatch, BulkPoleConfigurationRequest, apply_bulk_configuration
from app.services.wifi_coverage import apply_wifi_result, calculate_wifi_coverage, invalidate_stale_wifi_results, wifi_calculation_input_sha256


ROOT = Path(__file__).resolve().parents[2]


def wifi_project() -> Project:
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    points = [to_wgs84.transform(600000, 2850000), to_wgs84.transform(600040, 2850000)]
    poles = [SourcePole(id=f"p-{index}", sequence_index=index, name=f"P{index}", longitude=lon, latitude=lat, raw_coordinates=f"{lon},{lat},0") for index, (lon, lat) in enumerate(points)]
    project = Project(projected_crs="EPSG:32617", source=SourceLayer(poles=poles))
    project.pole_edits["p-0"] = PoleEdit(pole_id="p-0", fixture_type=FixtureType.WIFI)
    project.pole_edits["p-1"] = PoleEdit(pole_id="p-1", fixture_type=FixtureType.LITE)
    return project


def fixtures():
    return CatalogStore(root=ROOT / "backend" / "data" / "does-not-exist").fixtures()


def test_conceptual_circle_and_overlap_statistics_are_deterministic():
    project = wifi_project()
    result = calculate_wifi_coverage(project, fixtures())
    assert len(result.circles) == 1
    circle = result.circles[0]
    assert circle.id == "wifi-circle/p-0"
    assert len(circle.projected_ring) == 129
    assert circle.projected_ring[0] == circle.projected_ring[-1]
    assert result.global_statistics.union_covered_area_m2 == pytest.approx(2826.298041, abs=1e-6)
    assert result.global_statistics.pairwise_overlap_area_m2 == 0
    assert result.disclaimer.startswith("Conceptual geometric visualization only")


def test_analysis_area_clips_and_no_area_never_infers_boundary():
    project = wifi_project()
    no_area = calculate_wifi_coverage(project, fixtures())
    assert no_area.analysis_area_statistics == []
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    ring = [to_wgs84.transform(x, y) for x, y in ((599980, 2849980), (600020, 2849980), (600020, 2850020), (599980, 2850020), (599980, 2849980))]
    project.wifi_analysis_areas.append(WifiAnalysisArea(id="area", name="Road", wgs84_coordinates=ring))
    result = calculate_wifi_coverage(project, fixtures())
    assert result.analysis_area_statistics[0].covered_area_m2 > 0
    assert result.analysis_area_statistics[0].boundary_covered_percentage > 0


def test_three_circle_pairwise_sum_and_multiply_covered_union_are_distinct():
    project = wifi_project()
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    for index, x in enumerate((600000, 600010, 600020)):
        lon, lat = to_wgs84.transform(x, 2850000)
        pole = SourcePole(id=f"triple-{index}", sequence_index=index, name=f"Triple {index}", longitude=lon, latitude=lat, raw_coordinates=f"{lon},{lat},0")
        project.source.poles.append(pole)
        project.pole_edits[pole.id] = PoleEdit(pole_id=pole.id, fixture_type=FixtureType.WIFI)
    result = calculate_wifi_coverage(project, fixtures())
    assert result.global_statistics.overlap_pair_count >= 3
    assert result.global_statistics.pairwise_overlap_area_m2 > result.global_statistics.multiply_covered_union_area_m2


def test_disabled_and_inactive_poles_are_excluded_and_fingerprint_ignores_notes():
    project = wifi_project()
    project.pole_edits["p-0"].fixture_configuration = {"fixture_model_id": "phoenix-1-wifi", "fixture_model_revision": 1, "fixture_azimuth_deg": 0, "lighting_properties": {}, "wifi_configuration": {"enabled": False}}
    # Pydantic assignment validates the typed configuration on the next model boundary.
    project = Project.model_validate(project.model_dump(mode="json"))
    result = calculate_wifi_coverage(project, fixtures())
    assert result.global_statistics.circle_count == 0
    before = wifi_calculation_input_sha256(project)
    project.pole_edits["p-0"].fixture_configuration.wifi_configuration.notes = "field note"
    assert wifi_calculation_input_sha256(project) == before
    calculated = apply_wifi_result(project, result)
    calculated.pole_edits["p-0"].fixture_configuration.wifi_configuration.notes = "timestamp and note only"
    assert not invalidate_stale_wifi_results(calculated)
    calculated.pole_edits["p-0"].active = False
    assert invalidate_stale_wifi_results(calculated)


def test_significant_inputs_invalidate_but_area_timestamps_do_not():
    project = wifi_project()
    result = calculate_wifi_coverage(project, fixtures())
    calculated = apply_wifi_result(project, result)
    ring = [(-80.0, 25.0), (-79.999, 25.0), (-79.999, 25.001), (-80.0, 25.001), (-80.0, 25.0)]
    calculated.wifi_analysis_areas.append(WifiAnalysisArea(id="a", name="Area", wgs84_coordinates=ring))
    calculated.wifi_coverage.result = calculate_wifi_coverage(calculated, fixtures())
    calculated.wifi_coverage.state.calculation_input_sha256 = calculated.wifi_coverage.result.calculation_input_sha256
    calculated.wifi_analysis_areas[0].modified_at = calculated.wifi_analysis_areas[0].modified_at.replace(year=2027)
    assert not invalidate_stale_wifi_results(calculated)
    calculated.defaults.wifi_radius_m = 31
    assert invalidate_stale_wifi_results(calculated)


def test_exact_area_precision_is_used_for_many_circles():
    base = wifi_project()
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    poles = []
    for index in range(500):
        lon, lat = to_wgs84.transform(600000 + index * 300, 2850000)
        poles.append(SourcePole(id=f"p-{index}", sequence_index=index, name=f"P{index}", longitude=lon, latitude=lat, raw_coordinates=f"{lon},{lat},0"))
    project = Project(projected_crs="EPSG:32617", source=SourceLayer(poles=poles))
    for pole in poles:
        project.pole_edits[pole.id] = PoleEdit(pole_id=pole.id, fixture_type=FixtureType.WIFI)
    result = calculate_wifi_coverage(project, fixtures())
    to_projected = Transformer.from_crs("EPSG:4326", "EPSG:32617", always_xy=True)
    expected = round(sum(Point(*to_projected.transform(pole.longitude, pole.latitude)).buffer(30, quad_segs=32).area for pole in poles), 6)
    assert result.global_statistics.individual_area_m2 == pytest.approx(expected, abs=1e-6)
    assert abs(result.global_statistics.individual_area_m2 - sum(circle.area_m2 for circle in result.circles)) > 0.0001


def test_migration_is_additive_lossless_and_idempotent():
    project = wifi_project()
    payload = project.model_dump(mode="json")
    payload["schema_version"] = "2.4.0"
    payload["pole_edits"]["p-0"]["fixture_configuration"] = {"fixture_model_id": "phoenix-1-wifi", "fixture_model_revision": 1, "fixture_azimuth_deg": 0, "lighting_properties": {}, "wifi_configuration": {"notes": "legacy", "future_key": "preserve"}, "camera_overrides": {}}
    migrated = migrate_project_payload(copy.deepcopy(payload))
    opened = Project.model_validate(migrated)
    wifi = opened.pole_edits["p-0"].fixture_configuration.wifi_configuration
    assert opened.schema_version == "2.6.0"
    assert wifi is not None and wifi.notes == "legacy" and wifi.legacy_metadata["future_key"] == "preserve"
    assert migrate_project_payload(opened.model_dump(mode="json")) == opened.model_dump(mode="json")


def test_caps_reject_without_partial_result():
    project = wifi_project()
    project.defaults.wifi_radius_m = 1000
    result = calculate_wifi_coverage(project, fixtures())
    project.wifi_coverage.result = result
    object.__setattr__(project, "wifi_analysis_areas", [WifiAnalysisArea(id="a", name="Huge", wgs84_coordinates=[(-80, 25), (-79, 25), (-79, 26), (-80, 26), (-80, 25)])] * 201)
    with pytest.raises(ValueError, match="200"):
        calculate_wifi_coverage(project, fixtures())
    assert project.wifi_coverage.result is result


def test_wifi_api_calculate_and_controlled_errors_preserve_project(tmp_path: Path):
    project = wifi_project()
    store = ProjectStore(tmp_path / "projects")
    store.save(project)
    client = TestClient(create_app(store, CatalogStore(root=tmp_path / "catalogs", seed_root=ROOT / "data" / "phase2")))
    response = client.post(f"/api/projects/{project.id}/wifi-coverage/calculate", json=project.model_dump(mode="json"))
    assert response.status_code == 200
    calculated = response.json()
    assert calculated["wifi_coverage"]["result"]["disclaimer"].startswith("Conceptual geometric visualization only")
    assert client.post(f"/api/projects/{project.id}/wifi-coverage/calculate", json={**calculated, "id": "wrong"}).status_code == 409
    assert client.post("/api/projects/missing/wifi-coverage/invalidate").status_code == 404
    invalid_area = {"id": "bad", "name": "Bad", "wgs84_coordinates": [[0, 0], [1, 1], [0, 1], [1, 0], [0, 0]]}
    failed = client.post(f"/api/projects/{project.id}/wifi-analysis-areas", json=invalid_area)
    assert failed.status_code == 422
    assert store.load(project.id).wifi_coverage.result is not None


def test_bulk_wifi_set_and_clear_are_explicit_and_atomic():
    project = wifi_project()
    request = BulkPoleConfigurationRequest(pole_ids=["p-0"], patch=BulkPoleConfigurationPatch(fixture_model_id="phoenix-1-wifi", wifi_radius_override_m=42, wifi_enabled=False, wifi_notes="bulk"))
    updated = apply_bulk_configuration(project, request, fixtures())
    wifi = updated.pole_edits["p-0"].fixture_configuration.wifi_configuration
    assert wifi.radius_override_m == 42 and wifi.enabled is False and wifi.configuration_revision == 2
    clear = BulkPoleConfigurationRequest(pole_ids=["p-0"], patch=BulkPoleConfigurationPatch(clear_wifi_radius_override=True, clear_wifi_enabled_override=True))
    cleared = apply_bulk_configuration(updated, clear, fixtures())
    wifi = cleared.pole_edits["p-0"].fixture_configuration.wifi_configuration
    assert wifi.radius_override_m is None and wifi.enabled is None and wifi.configuration_revision == 3
    with pytest.raises(ValueError, match="unknown poles"):
        apply_bulk_configuration(project, BulkPoleConfigurationRequest(pole_ids=["missing"], patch=BulkPoleConfigurationPatch(wifi_radius_override_m=10)), fixtures())


def test_bulk_wifi_noop_and_meaningful_revision_semantics():
    project = apply_bulk_configuration(project=wifi_project(), request=BulkPoleConfigurationRequest(pole_ids=["p-0"], patch=BulkPoleConfigurationPatch(fixture_model_id="phoenix-1-wifi", wifi_notes="baseline")), fixtures=fixtures())
    wifi = project.pole_edits["p-0"].fixture_configuration.wifi_configuration
    wifi.notes = "same"
    wifi.modified_at = "2026-01-01T00:00:00Z"
    wifi.configuration_revision = 7

    def apply(patch):
        return apply_bulk_configuration(project, BulkPoleConfigurationRequest(pole_ids=["p-0"], patch=patch), fixtures()).pole_edits["p-0"].fixture_configuration.wifi_configuration

    unchanged = apply(BulkPoleConfigurationPatch(wifi_notes="same", clear_wifi_radius_override=False, clear_wifi_enabled_override=False))
    assert unchanged.configuration_revision == 7
    assert unchanged.modified_at.isoformat() == "2026-01-01T00:00:00+00:00"
    unchanged_flags = apply(BulkPoleConfigurationPatch(clear_wifi_radius_override=False, clear_wifi_enabled_override=False))
    assert unchanged_flags.configuration_revision == 7 and unchanged_flags.modified_at.isoformat() == "2026-01-01T00:00:00+00:00"
    unchanged_value = apply(BulkPoleConfigurationPatch(wifi_radius_override_m=None, wifi_enabled=None, wifi_notes="same"))
    assert unchanged_value.configuration_revision == 7 and unchanged_value.modified_at.isoformat() == "2026-01-01T00:00:00+00:00"

    changed_note = apply(BulkPoleConfigurationPatch(wifi_notes="changed"))
    assert changed_note.configuration_revision == 8 and changed_note.notes == "changed"
    project.pole_edits["p-0"].fixture_configuration.wifi_configuration.radius_override_m = 42
    project.pole_edits["p-0"].fixture_configuration.wifi_configuration.enabled = False
    project.pole_edits["p-0"].fixture_configuration.wifi_configuration.configuration_revision = 7
    combined = apply(BulkPoleConfigurationPatch(wifi_notes="combined", wifi_radius_override_m=50, wifi_enabled=True))
    assert combined.configuration_revision == 8 and combined.notes == "combined" and combined.radius_override_m == 50 and combined.enabled is True
    cleared = apply(BulkPoleConfigurationPatch(clear_wifi_radius_override=True, clear_wifi_enabled_override=True))
    assert cleared.configuration_revision == 8 and cleared.radius_override_m is None and cleared.enabled is None


def test_bulk_wifi_api_noop_preserves_revision_and_timestamp(tmp_path: Path):
    project = apply_bulk_configuration(project=wifi_project(), request=BulkPoleConfigurationRequest(pole_ids=["p-0"], patch=BulkPoleConfigurationPatch(fixture_model_id="phoenix-1-wifi", wifi_notes="baseline")), fixtures=fixtures())
    wifi = project.pole_edits["p-0"].fixture_configuration.wifi_configuration
    wifi.notes = "same"
    wifi.modified_at = "2026-01-01T00:00:00Z"
    wifi.configuration_revision = 7
    store = ProjectStore(tmp_path / "projects")
    store.save(project)
    client = TestClient(create_app(store, CatalogStore(root=tmp_path / "catalogs", seed_root=ROOT / "data" / "phase2")))
    response = client.patch(f"/api/projects/{project.id}/poles/bulk", json={"pole_ids": ["p-0"], "patch": {"wifi_notes": "same", "clear_wifi_radius_override": False, "clear_wifi_enabled_override": False}})
    assert response.status_code == 200
    returned = response.json()["pole_edits"]["p-0"]["fixture_configuration"]["wifi_configuration"]
    assert returned["configuration_revision"] == 7
    assert returned["modified_at"] == "2026-01-01T00:00:00Z"


def _full_replacement_project() -> Project:
    project = apply_bulk_configuration(
        project=wifi_project(),
        request=BulkPoleConfigurationRequest(
            pole_ids=["p-0"],
            patch=BulkPoleConfigurationPatch(fixture_model_id="phoenix-1-wifi", wifi_notes="same"),
        ),
        fixtures=fixtures(),
    )
    wifi = project.pole_edits["p-0"].fixture_configuration.wifi_configuration
    wifi.radius_override_m = 42
    wifi.enabled = False
    wifi.notes = "same"
    wifi.legacy_metadata = {"source": "test"}
    wifi.modified_at = "2026-01-01T00:00:00Z"
    wifi.configuration_revision = 7
    return project


def test_bulk_wifi_full_replacement_noop_preserves_typed_metadata():
    project = _full_replacement_project()
    original = copy.deepcopy(project.pole_edits["p-0"].fixture_configuration.wifi_configuration)
    replacement = {
        "radius_override_m": 42,
        "enabled": False,
        "notes": "same",
        "legacy_metadata": {"source": "test"},
    }
    updated = apply_bulk_configuration(
        project,
        BulkPoleConfigurationRequest(pole_ids=["p-0"], patch=BulkPoleConfigurationPatch(wifi_configuration=replacement)),
        fixtures(),
    )
    actual = updated.pole_edits["p-0"].fixture_configuration.wifi_configuration
    assert actual == original
    assert actual.configuration_revision == 7
    assert actual.modified_at.isoformat() == "2026-01-01T00:00:00+00:00"


def test_bulk_wifi_api_full_replacement_noop_preserves_revision_and_timestamp(tmp_path: Path):
    project = _full_replacement_project()
    store = ProjectStore(tmp_path / "projects")
    store.save(project)
    client = TestClient(create_app(store, CatalogStore(root=tmp_path / "catalogs", seed_root=ROOT / "data" / "phase2")))
    response = client.patch(
        f"/api/projects/{project.id}/poles/bulk",
        json={
            "pole_ids": ["p-0"],
            "patch": {
                "wifi_configuration": {
                    "radius_override_m": 42,
                    "enabled": False,
                    "notes": "same",
                    "legacy_metadata": {"source": "test"},
                }
            },
        },
    )
    assert response.status_code == 200
    returned = response.json()["pole_edits"]["p-0"]["fixture_configuration"]["wifi_configuration"]
    assert returned["configuration_revision"] == 7
    assert returned["modified_at"] == "2026-01-01T00:00:00Z"


def test_bulk_wifi_full_replacement_meaningful_change_increments_once():
    project = _full_replacement_project()
    updated = apply_bulk_configuration(
        project,
        BulkPoleConfigurationRequest(
            pole_ids=["p-0"],
            patch=BulkPoleConfigurationPatch(
                wifi_configuration={
                    "radius_override_m": 55,
                    "enabled": True,
                    "notes": "changed",
                    "legacy_metadata": {"source": "replacement"},
                }
            ),
        ),
        fixtures(),
    )
    actual = updated.pole_edits["p-0"].fixture_configuration.wifi_configuration
    assert actual.radius_override_m == 55
    assert actual.enabled is True
    assert actual.notes == "changed"
    assert actual.legacy_metadata == {"source": "replacement"}
    assert actual.configuration_revision == 8
    assert actual.modified_at.isoformat() != "2026-01-01T00:00:00+00:00"
