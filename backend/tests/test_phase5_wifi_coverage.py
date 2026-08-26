from __future__ import annotations

import copy
from pathlib import Path

import pytest
from pyproj import Transformer

from app.models import FixtureType, PoleEdit, Project, SourceLayer, SourcePole, WifiAnalysisArea, migrate_project_payload
from app.services.catalogs import CatalogStore
from app.services.wifi_coverage import calculate_wifi_coverage, invalidate_stale_wifi_results, wifi_calculation_input_sha256


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
    project.pole_edits["p-0"].active = False
    assert invalidate_stale_wifi_results(Project.model_validate({**project.model_dump(mode="json"), "wifi_coverage": {"result": result.model_dump(mode="json")}}))


def test_migration_is_additive_lossless_and_idempotent():
    project = wifi_project()
    payload = project.model_dump(mode="json")
    payload["schema_version"] = "2.4.0"
    payload["pole_edits"]["p-0"]["fixture_configuration"] = {"fixture_model_id": "phoenix-1-wifi", "fixture_model_revision": 1, "fixture_azimuth_deg": 0, "lighting_properties": {}, "wifi_configuration": {"notes": "legacy", "future_key": "preserve"}, "camera_overrides": {}}
    migrated = migrate_project_payload(copy.deepcopy(payload))
    opened = Project.model_validate(migrated)
    wifi = opened.pole_edits["p-0"].fixture_configuration.wifi_configuration
    assert opened.schema_version == "2.5.0"
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
