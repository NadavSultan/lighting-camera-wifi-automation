from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pyproj import Transformer

from app.main import create_app
from app.models import CapCandidateSite, CapConstraintValue, CapKnowledge, CapNodeDisposition, CapPlanningInputs, FixtureType, PoleEdit, Project, SourceLayer, SourcePole, migrate_project_payload
from app.services.cap_planning import _adjacency, apply_cap_result, calculate_cap_plan, invalidate_stale_cap_results
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


@pytest.mark.parametrize("version", ["1.0.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0", "2.4.0", "2.5.0"])
def test_p6_mg_01_every_supported_version_preserves_prior_collections_and_source_bytes(version):
    project = Project(source=SourceLayer(poles=[SourcePole(id="p", sequence_index=0, name="P", longitude=-80, latitude=25, raw_coordinates="-80.000000,25.000000,0")]))
    payload = project.model_dump(mode="json")
    payload.update({
        "schema_version": version,
        "source_references": {"source_sha256": "a" * 64},
        "pole_edits": {"p": {"pole_id": "p", "name": "Edited", "fixture_type": "WIFI", "modified_at": project.updated_at.isoformat()}},
        "priority_areas": [], "calculation_areas": [], "lighting_calculations": {"state": {}, "result": None},
        "wifi_analysis_areas": [], "wifi_coverage": {"state": {}, "result": None},
        "camera_geometry": {"state": {}}, "recommended_layers": {"future": {"bytes": "preserve"}},
    })
    for key in ("cap_planning_inputs", "cap_calculations", "cap_recommendations"):
        payload.pop(key)
    original_source = payload["source"]
    original_prior = {key: payload[key] for key in ("pole_edits", "priority_areas", "calculation_areas", "lighting_calculations", "wifi_analysis_areas", "wifi_coverage", "camera_geometry", "recommended_layers", "source_references")}
    migrated = migrate_project_payload(payload)
    assert migrated["source"] == original_source
    assert {key: migrated[key] for key in original_prior} == original_prior
    assert migrated["cap_planning_inputs"] == {}
    assert migrated["cap_calculations"] == {}
    assert migrated["cap_recommendations"] == {}
    assert migrate_project_payload(migrated) == migrated


def test_p6_dm_01_strict_collections_reject_extra_nonfinite_and_keep_cap_data_separate():
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        CapPlanningInputs.model_validate({"unexpected": True})
    with pytest.raises(ValueError, match="finite"):
        CapCandidateSite(id="manual", kind="manual_non_pole", wgs84_coordinate=(float("nan"), 25))
    project = project_with_test_only_inputs()
    calculated = apply_cap_result(project, calculate_cap_plan(project))
    assert calculated.cap_planning_inputs.candidates[0].id == "cap-a"
    assert calculated.cap_calculations.result is not None
    assert calculated.cap_recommendations.selected_candidate_ids == ["cap-a"]
    assert calculated.recommended_layers == {}


@pytest.mark.parametrize("field", ["gateway_appliance_counting", "colocated_fixture_counting"])
def test_p6_dm_02_unknown_counting_convention_round_trips_and_blocks_exact_dependent_field(field):
    project = project_with_test_only_inputs()
    setattr(project.cap_planning_inputs.profile, field, CapConstraintValue())
    restored = Project.model_validate(project.model_dump(mode="json"))
    assert getattr(restored.cap_planning_inputs.profile, field).status is CapKnowledge.UNKNOWN
    with pytest.raises(ValueError, match=field.replace("_", " ").replace("colocated", "co-located")):
        calculate_cap_plan(restored)


@pytest.mark.parametrize("field,ceiling", [("node_limit", 1000), ("child_limit", 16), ("hop_limit", 64)])
def test_p6_dm_03_manufacturer_ceiling_rejects_more_permissive_project_limit(field, ceiling):
    project = project_with_test_only_inputs()
    getattr(project.cap_planning_inputs.profile, field).value = ceiling + 1
    with pytest.raises(ValueError, match=f"manufacturer ceiling {ceiling}"):
        calculate_cap_plan(project)


def test_p6_dm_04_unresolved_conflict_preserves_source_and_never_selects_permissive_value():
    project = project_with_test_only_inputs()
    constraint = project.cap_planning_inputs.profile.node_limit
    constraint.classification = "manufacturer_hard_constraint"
    constraint.source = "exact-product manufacturer evidence"
    constraint.applicability = "test-only exact variant"
    constraint.conflict_state = "unresolved"
    restored = Project.model_validate(project.model_dump(mode="json"))
    assert restored.cap_planning_inputs.profile.node_limit.model_dump(mode="json") == constraint.model_dump(mode="json")
    with pytest.raises(ValueError, match="node limit has an unresolved precedence conflict"):
        calculate_cap_plan(restored)


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


def test_p6_gr_01_projected_distance_accepts_tolerance_boundary_and_rejects_above_it():
    vertices = [{"id": "a", "x": 0.0, "y": 0.0}, {"id": "b", "x": 20.000000001, "y": 0.0}]
    _, _, links = _adjacency(vertices, 20.0)
    assert [(left, right) for left, right, _, _ in links] == [("a", "b")]
    vertices[1]["x"] = 20.0000000011
    _, _, links = _adjacency(vertices, 20.0)
    assert links == []


def test_p6_gr_02_manual_non_pole_candidate_is_separate_user_data_and_not_a_fixture_node():
    project = project_with_test_only_inputs()
    source_poles = list(project.source.poles)
    project.cap_planning_inputs.candidates = [CapCandidateSite(
        id="manual-cap", kind="manual_non_pole", wgs84_coordinate=(source_poles[0].longitude, source_poles[0].latitude),
        mounting_confirmed=True, power_confirmed=True, backhaul_confirmed=True, enclosure_confirmed=True,
        indoor_outdoor="outdoor", survey_status="confirmed",
    )]
    result = calculate_cap_plan(project)
    assert project.source.poles == source_poles
    assert result.candidate_snapshots[0].source_pole_id is None
    assert result.candidate_snapshots[0].candidate_id == "manual-cap"
    assert all(snapshot.id.startswith("fixture/") for snapshot in result.node_snapshots)


def test_p6_gr_03_chain_topology_and_shuffled_source_input_are_canonical():
    project = project_with_test_only_inputs()
    to_wgs84 = Transformer.from_crs("EPSG:32617", "EPSG:4326", always_xy=True)
    lon, lat = to_wgs84.transform(600020, 2850000)
    project.source.poles.append(SourcePole(id="p2", sequence_index=2, name="P2", longitude=lon, latitude=lat, raw_coordinates=f"{lon},{lat},0"))
    project.pole_edits["p2"] = PoleEdit(pole_id="p2", fixture_type=FixtureType.WIFI)
    project.cap_planning_inputs.profile.link_distance_m.value = 11
    expected = calculate_cap_plan(project)
    project.source.poles.reverse()
    rerun = calculate_cap_plan(project)
    assert rerun == expected
    assert [(item.node_id, item.parent_id, item.hop) for item in expected.assignments] == [
        ("fixture/p0", "gateway/cap-a", 1), ("fixture/p1", "gateway/cap-a", 1), ("fixture/p2", "fixture/p1", 2),
    ]


def test_p6_al_02_candidate_tie_breaks_by_stable_candidate_id_not_input_order():
    project = project_with_test_only_inputs()
    project.cap_planning_inputs.profile.link_distance_m.value = 15
    project.cap_planning_inputs.candidates = [
        CapCandidateSite(id="cap-z", kind="existing_pole", pole_id="p0", mounting_confirmed=True, power_confirmed=True, backhaul_confirmed=True, enclosure_confirmed=True, indoor_outdoor="outdoor", survey_status="confirmed"),
        CapCandidateSite(id="cap-a", kind="existing_pole", pole_id="p1", mounting_confirmed=True, power_confirmed=True, backhaul_confirmed=True, enclosure_confirmed=True, indoor_outdoor="outdoor", survey_status="confirmed"),
    ]
    result = calculate_cap_plan(project)
    assert result.selected_candidate_ids == ["cap-a"]
    project.cap_planning_inputs.candidates.reverse()
    assert calculate_cap_plan(project).selected_candidate_ids == ["cap-a"]


def test_p6_rd_01_and_p6_rd_03_use_exact_non_failover_diagnostics():
    project = project_with_test_only_inputs()
    result = calculate_cap_plan(project)
    assert result.warnings == ["Single-CAP conceptual plan; single point of failure is not mitigated by this graph result."]
    project.cap_planning_inputs.profile.redundancy.value = "user_supplied_only"
    result = calculate_cap_plan(project)
    assert result.warnings == ["Redundancy is user-supplied only; this result makes no redundancy acceptance statement."]


def test_p6_rd_02_n_plus_one_reassigns_or_fails_for_capacity_stranding():
    project = project_with_test_only_inputs()
    project.cap_planning_inputs.candidates = [
        CapCandidateSite(id="cap-a", kind="existing_pole", pole_id="p0", mounting_confirmed=True, power_confirmed=True, backhaul_confirmed=True, enclosure_confirmed=True, indoor_outdoor="outdoor", survey_status="confirmed", locked_selected=True),
        CapCandidateSite(id="cap-b", kind="existing_pole", pole_id="p1", mounting_confirmed=True, power_confirmed=True, backhaul_confirmed=True, enclosure_confirmed=True, indoor_outdoor="outdoor", survey_status="confirmed", locked_selected=True),
    ]
    project.cap_planning_inputs.profile.redundancy.value = "n_plus_one_validation"
    assert "stress test only" in calculate_cap_plan(project).warnings[0]
    project.cap_planning_inputs.profile.node_limit.value = 1
    with pytest.raises(ValueError, match=r"N\+1 graph validation failed"):
        calculate_cap_plan(project)


def test_p6_sf_01_candidate_safety_boundary_is_atomic():
    project = project_with_test_only_inputs()
    candidate = project.cap_planning_inputs.candidates[0]
    project.cap_planning_inputs.candidates = [candidate.model_copy(update={"id": f"cap-{index}"}) for index in range(501)]
    with pytest.raises(ValueError, match="candidate sites exceed safety cap 500"):
        calculate_cap_plan(project)
    assert project.cap_calculations.result is None


def test_p6_fp_01_input_fingerprint_invalidates_results_without_mutating_inputs():
    project = project_with_test_only_inputs()
    applied = apply_cap_result(project, calculate_cap_plan(project))
    before = applied.cap_planning_inputs.model_dump(mode="json")
    assert invalidate_stale_cap_results(applied) is False
    applied.cap_planning_inputs.candidates[0].preferred = True
    assert invalidate_stale_cap_results(applied) is True
    assert applied.cap_planning_inputs.model_dump(mode="json")["candidates"][0]["preferred"] is True
    assert before["candidates"][0]["id"] == "cap-a"


def test_p6_pr_01_provenance_captures_catalog_datasheet_constraints_and_crs():
    result = calculate_cap_plan(project_with_test_only_inputs())
    provenance = result.provenance
    assert provenance["constraints_catalog"]["version"] == "1.0.0"
    assert len(provenance["constraints_catalog"]["sha256"]) == 64
    assert provenance["datasheet_revision"] == "Juganu JNET1 Gateway data sheet Rev 1.2"
    assert provenance["projected_crs"] == "EPSG:32617"
    assert provenance["profile_constraints"]["link_distance_m"]["unit"] == "m"
    assert provenance["profile_constraints"]["node_limit"]["source"] == "test-only approved assumption"


def test_p6_ap_01_and_p6_ex_01_successful_calculation_returns_complete_project_and_reopens(tmp_path: Path):
    project = project_with_test_only_inputs()
    store = ProjectStore(tmp_path / "projects")
    saved = store.save(project)
    client = TestClient(create_app(store))
    response = client.post(f"/api/projects/{saved.id}/cap-planning/calculate", json=saved.model_dump(mode="json"))
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["id"] == saved.id
    assert payload["cap_planning_inputs"]["candidates"][0]["id"] == "cap-a"
    assert payload["cap_calculations"]["result"]["selected_candidate_ids"] == ["cap-a"]
    assert payload["cap_recommendations"]["selected_candidate_ids"] == ["cap-a"]
    assert store.load(saved.id).model_dump(mode="json")["cap_calculations"] == payload["cap_calculations"]


def test_p6_ap_02_invalid_manual_constraints_are_422_and_preserve_exact_project_bytes(tmp_path: Path):
    project = project_with_test_only_inputs()
    store = ProjectStore(tmp_path / "projects")
    saved = store.save(project)
    project_path = tmp_path / "projects" / saved.id / "project.json"
    before = project_path.read_bytes()
    client = TestClient(create_app(store))
    response = client.put(f"/api/projects/{saved.id}/cap-planning/manual-constraints", json={
        "excluded_node_ids": ["fixture/missing"], "excluded_candidate_ids": [], "locked_selected_candidate_ids": [],
        "primary_assignment_locks": {}, "parent_locks": {},
    })
    assert response.status_code == 422
    assert project_path.read_bytes() == before
