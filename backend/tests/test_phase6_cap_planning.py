from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pyproj import Transformer

from app.main import create_app
from app.models import CapCandidateSite, CapConstraintValue, CapKnowledge, CapNodeDisposition, CapPlanningInputs, FixtureType, PoleEdit, Project, SourceLayer, SourcePole, migrate_project_payload
from app.services.cap_planning import apply_cap_result, calculate_cap_plan, invalidate_stale_cap_results
from app.services.store import ProjectStore


def project_with_test_only_inputs() -> Project:
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    poles = []
    for i, x in enumerate((600000, 600010)):
        lon, lat = to_wgs84.transform(x, 2850000)
        poles.append(SourcePole(id=f"p{i}", sequence_index=i, name=f"P{i}", longitude=lon, latitude=lat, raw_coordinates=f"{lon},{lat},0"))
    project = Project(projected_crs="EPSG:32617", source=SourceLayer(poles=poles))
    project.pole_edits["p0"] = PoleEdit(pole_id="p0", fixture_type=FixtureType.WIFI)
    project.pole_edits["p1"] = PoleEdit(pole_id="p1", fixture_type=FixtureType.WIFI)
    known = lambda value, unit=None: CapConstraintValue(status=CapKnowledge.KNOWN, value=value, unit=unit, classification="user_approved_assumption", source="test-only approved assumption", applicability="test-only")
    profile = project.cap_planning_inputs.profile
    profile.product_mapping = known("JNET1")
    profile.variant = known("JGW-JNET1-915-ID")
    profile.band_and_jurisdiction = known("915 MHz test-only")
    profile.link_distance_m = known(20, "m")
    profile.node_limit = known(100, "node")
    profile.child_limit = known(16, "node")
    profile.hop_limit = known(64, "hop")
    profile.gateway_appliance_counting = known("excluded")
    profile.colocated_fixture_counting = known("distinct_managed_node_once")
    profile.redundancy = known("single_allowed_with_warning")
    profile.node_policy.LITE = CapNodeDisposition.NON_NODE
    profile.node_policy.WIFI = CapNodeDisposition.NODE
    profile.node_policy.SMART = CapNodeDisposition.NON_NODE
    profile.mode_permission = "recommend_from_approved_pool"
    project.cap_planning_inputs.candidates = [CapCandidateSite(id="cap-a", kind="existing_pole", pole_id="p0", mounting_confirmed=True, power_confirmed=True, backhaul_confirmed=True, enclosure_confirmed=True, indoor_outdoor="outdoor", survey_status="confirmed")]
    return project


def test_p6_dm_02_unknowns_block_without_mutation():
    project = Project(projected_crs="EPSG:32617")
    with pytest.raises(ValueError, match="product mapping is unknown"):
        calculate_cap_plan(project)
    assert project.cap_calculations.result is None


def test_p6_mg_01_migration_adds_only_empty_cap_collections_losslessly():
    project = Project(source=SourceLayer(poles=[SourcePole(id="p", sequence_index=0, name="P", longitude=-80, latitude=25, raw_coordinates="-80,25,0")]))
    payload = project.model_dump(mode="json")
    payload["schema_version"] = "2.5.0"
    payload.pop("cap_planning_inputs"); payload.pop("cap_calculations"); payload.pop("cap_recommendations")
    payload["recommended_layers"] = {"future": {"preserve": True}}
    migrated = migrate_project_payload(payload)
    assert migrated["schema_version"] == "2.6.0"
    assert migrated["source"] == payload["source"]
    assert migrated["recommended_layers"] == payload["recommended_layers"]
    assert Project.model_validate(migrated).cap_calculations.result is None
    assert migrate_project_payload(migrated) == migrated


def test_p6_sf_02_invalid_non_metre_crs_fails_without_result_mutation():
    project = project_with_test_only_inputs()
    with pytest.raises(ValueError, match="projected and use metre axes"):
        project.projected_crs = "EPSG:4326"
    assert project.cap_calculations.result is None


def test_p6_pr_01_result_has_catalog_model_crs_and_graph_only_disclaimer():
    result = calculate_cap_plan(project_with_test_only_inputs())
    assert result.model_version == "jnet1-graph-planning-1.0.0"
    assert result.projected_crs == "EPSG:32617"
    assert "not RF-predicted" in result.disclaimer


@pytest.mark.parametrize("field,value", [("node_limit", 1.5), ("child_limit", 2.1), ("hop_limit", True)])
def test_p6_dm_03_design_limits_require_genuine_integers(field, value):
    project = project_with_test_only_inputs()
    getattr(project.cap_planning_inputs.profile, field).value = value
    with pytest.raises(ValueError, match="must be an integer"):
        calculate_cap_plan(project)


def test_p6_dm_04_unresolved_conflict_round_trips_and_blocks_only_operation():
    project = project_with_test_only_inputs()
    project.cap_planning_inputs.profile.variant.conflict_state = "unresolved"
    restored = Project.model_validate(project.model_dump(mode="json"))
    assert restored.cap_planning_inputs.profile.variant.conflict_state == "unresolved"
    with pytest.raises(ValueError, match="unresolved"):
        calculate_cap_plan(restored)


def test_p6_ct_01_p6_gr_01_p6_al_01_deterministic_projected_graph_preserves_root_fixture_identity():
    project = project_with_test_only_inputs()
    result = calculate_cap_plan(project)
    assert result == calculate_cap_plan(project)
    assert [item.node_id for item in result.assignments] == ["fixture/p0", "fixture/p1"]
    assert result.assignments[0].gateway_id == "gateway/cap-a"
    assert result.assignments[0].distance_m == 0
    assert result.assignments[0].hop == 1
    calculated = apply_cap_result(project, result)
    assert not invalidate_stale_cap_results(calculated)
    calculated.cap_planning_inputs.profile.link_distance_m.value = 10
    assert invalidate_stale_cap_results(calculated)


def test_p6_ap_02_api_preflight_failure_is_atomic(tmp_path: Path):
    project = project_with_test_only_inputs()
    store = ProjectStore(tmp_path / "projects")
    store.save(project)
    client = TestClient(create_app(store))
    bad = project.model_dump(mode="json")
    bad["updated_at"] = "2000-01-01T00:00:00Z"
    response = client.post(f"/api/projects/{project.id}/cap-planning/calculate", json=bad)
    assert response.status_code == 409
    assert store.load(project.id).cap_calculations.result is None


def test_p6_mn_01_parent_cycle_and_missing_selection_locks_fail_closed():
    project = project_with_test_only_inputs()
    project.cap_planning_inputs.locked_selected_candidate_ids = ["missing"]
    with pytest.raises(ValueError, match="missing candidate"):
        calculate_cap_plan(project)
    project = project_with_test_only_inputs()
    project.cap_planning_inputs.parent_locks = {"fixture/p0": "fixture/p1", "fixture/p1": "fixture/p0"}
    with pytest.raises(ValueError, match="cycle"):
        calculate_cap_plan(project)


def test_p6_ct_01_merged_colocated_fixture_is_not_an_implicit_node():
    project = project_with_test_only_inputs()
    project.cap_planning_inputs.profile.colocated_fixture_counting.value = "merged_not_separate"
    result = calculate_cap_plan(project)
    assert "fixture/p0" not in [item.node_id for item in result.assignments]


def test_p6_dm_01_inactive_fixture_is_never_a_managed_cap_node():
    project = project_with_test_only_inputs()
    project.pole_edits["p1"].active = False
    result = calculate_cap_plan(project)
    assert "fixture/p1" not in [item.node_id for item in result.assignments]
    assert "fixture/p1" not in result.unresolved_node_ids


def test_p6_al_02_p6_al_03_recommendation_builds_locked_forest_before_marginal_ranking():
    project = project_with_test_only_inputs()
    project.cap_planning_inputs.candidates = [
        CapCandidateSite(id="cap-z", kind="existing_pole", pole_id="p0", mounting_confirmed=True, power_confirmed=True, backhaul_confirmed=True, enclosure_confirmed=True, indoor_outdoor="outdoor", survey_status="confirmed", locked_selected=True),
        CapCandidateSite(id="cap-a", kind="existing_pole", pole_id="p1", mounting_confirmed=True, power_confirmed=True, backhaul_confirmed=True, enclosure_confirmed=True, indoor_outdoor="outdoor", survey_status="confirmed"),
    ]
    result = calculate_cap_plan(project)
    assert result.selected_candidate_ids == ["cap-z"]
    assert {item.gateway_id for item in result.assignments} == {"gateway/cap-z"}
    assert result.objective_trace == []


def test_p6_al_04_validate_mode_requires_explicit_auto_assign_for_unlocked_nodes():
    project = project_with_test_only_inputs()
    profile = project.cap_planning_inputs.profile
    profile.operation_mode = "validate"
    profile.mode_permission = "validate_only"
    project.cap_planning_inputs.locked_selected_candidate_ids = ["cap-a"]
    result = calculate_cap_plan(project)
    assert result.assignments == []
    assert result.unresolved_node_ids == ["fixture/p0", "fixture/p1"]
    profile.auto_assign_unlocked_nodes = True
    assigned = calculate_cap_plan(project)
    assert len(assigned.assignments) == 2


def test_p6_ap_01_candidate_replace_rejects_stale_record_revision_atomically(tmp_path: Path):
    project = project_with_test_only_inputs()
    store = ProjectStore(tmp_path / "projects")
    store.save(project)
    client = TestClient(create_app(store))
    candidate = project.cap_planning_inputs.candidates[0].model_dump(mode="json")
    response = client.put(f"/api/projects/{project.id}/cap-planning/candidates/cap-a", json=candidate)
    assert response.status_code == 409
    assert store.load(project.id).cap_planning_inputs.candidates[0].revision == 1
