"""Deterministic, deliberately non-RF CAP graph planning.

This service is pure: callers only persist its result after it returns.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import deque
from copy import deepcopy
from pathlib import Path
from shapely.geometry import Point
from shapely.strtree import STRtree

from pyproj.exceptions import ProjError

from app.crs import project_transformers, validate_projected_metre_crs
from app.models import CapAssignment, CapGraphLink, CapKnowledge, CapNodeDisposition, CapPlanningLimits, CapPlanningResult, CapScoreTrace, CapVertexSnapshot, Project, utc_now

DISCLAIMER = "Distance-qualified conceptual link; not RF-predicted. Graph-and-constraint planning only; not coverage, capacity, performance, service quality, installation feasibility, or compliance."
MAX_CANDIDATES = 500
MAX_PARTICIPATING_NODES = 2000
MAX_SELECTED_CAPS = 64
MAX_VERTICES = 2500
MAX_EDGE_EVALUATIONS = 250000
MAX_EDGES = 250000
MAX_TOPOLOGY_LINKS = 2000
MAX_IMPROVEMENT_PASSES = 8
MAX_N_PLUS_ONE_SCENARIOS = 64
MAX_SERIALIZED_PAYLOAD_BYTES = 25 * 1024 * 1024
EDGE_TOLERANCE_M = 1e-9
CAP_CONSTRAINTS_PATH = Path(__file__).resolve().parents[3] / "data" / "network" / "cap-constraints.json"
CAP_CONSTRAINTS_SHA256 = hashlib.sha256(CAP_CONSTRAINTS_PATH.read_bytes()).hexdigest()
CAP_CONSTRAINTS_VERSION = "1.0.0"
CAP_DATASHEET_REVISION = "Juganu JNET1 Gateway data sheet Rev 1.2"


def cap_input_sha256(project: Project) -> str:
    payload = project.cap_planning_inputs.model_dump(mode="json")
    payload["projected_crs"] = project.projected_crs
    payload["model_version"] = "jnet1-graph-planning-1.0.0"
    payload["constants"] = {"tolerance_m": EDGE_TOLERANCE_M, "participating_nodes": MAX_PARTICIPATING_NODES, "candidates": MAX_CANDIDATES, "selected_caps": MAX_SELECTED_CAPS, "vertices": MAX_VERTICES, "edge_evaluations": MAX_EDGE_EVALUATIONS, "edges": MAX_EDGES, "topology_links": MAX_TOPOLOGY_LINKS, "improvement_passes": MAX_IMPROVEMENT_PASSES, "n_plus_one_scenarios": MAX_N_PLUS_ONE_SCENARIOS, "serialized_payload_bytes": MAX_SERIALIZED_PAYLOAD_BYTES}
    payload["poles"] = [[p.id, p.longitude, p.latitude, p.sequence_index, (project.pole_edits.get(p.id).fixture_type.value if project.pole_edits.get(p.id) and project.pole_edits.get(p.id).fixture_type else project.defaults.fixture_type.value), (project.pole_edits.get(p.id).active if project.pole_edits.get(p.id) and project.pole_edits.get(p.id).active is not None else True)] for p in project.source.poles]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def invalidate_stale_cap_results(project: Project) -> bool:
    layer = project.cap_calculations
    if layer.result is None or layer.calculation_input_sha256 == cap_input_sha256(project):
        return False
    layer.status, layer.result, layer.calculation_input_sha256, layer.calculated_at, layer.warnings = "not-calculated", None, None, None, []
    project.cap_recommendations.selected_candidate_ids = []
    project.cap_recommendations.result_sha256 = None
    return True


def _known(value, name: str):
    if value.conflict_state == "unresolved":
        raise ValueError(f"CAP preflight blocked: {name} has an unresolved precedence conflict")
    if value.status is not CapKnowledge.KNOWN:
        raise ValueError(f"CAP preflight blocked: {name} is unknown")
    return value.value


def _number(value, name: str, ceiling: int | None = None) -> float:
    raw = _known(value, name)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(raw) or raw <= 0:
        raise ValueError(f"CAP preflight blocked: {name} must be a finite positive number")
    if ceiling is not None and raw > ceiling:
        raise ValueError(f"CAP preflight blocked: {name} exceeds manufacturer ceiling {ceiling}")
    return float(raw)


def _integer(value, name: str, ceiling: int) -> int:
    raw = _known(value, name)
    # bool is intentionally rejected although it is an int subclass.
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 1:
        raise ValueError(f"CAP preflight blocked: {name} must be an integer from 1 through {ceiling}")
    if raw > ceiling:
        raise ValueError(f"CAP preflight blocked: {name} exceeds manufacturer ceiling {ceiling}")
    return raw


def _preflight(project: Project) -> tuple[float, int, int, int]:
    profile = project.cap_planning_inputs.profile
    for label, field in (("product mapping", profile.product_mapping), ("variant", profile.variant), ("band and jurisdiction", profile.band_and_jurisdiction), ("gateway appliance counting", profile.gateway_appliance_counting), ("co-located fixture counting", profile.colocated_fixture_counting), ("redundancy policy", profile.redundancy)):
        _known(field, label)
    if profile.gateway_appliance_counting.value not in {"included", "excluded"}:
        raise ValueError("CAP preflight blocked: gateway appliance counting must be included or excluded")
    if profile.colocated_fixture_counting.value not in {"distinct_managed_node_once", "merged_not_separate"}:
        raise ValueError("CAP preflight blocked: co-located fixture counting must be distinct_managed_node_once or merged_not_separate")
    if profile.redundancy.value not in {"single_allowed_with_warning", "n_plus_one_validation", "user_supplied_only"}:
        raise ValueError("CAP preflight blocked: redundancy policy is invalid")
    for kind in ("LITE", "WIFI", "SMART"):
        if getattr(profile.node_policy, kind) is CapNodeDisposition.UNKNOWN:
            raise ValueError(f"CAP preflight blocked: {kind} node membership is unknown")
    if profile.mode_permission == "unknown":
        raise ValueError("CAP preflight blocked: mode permission is unknown")
    distance = _number(profile.link_distance_m, "per-link planning distance")
    node_limit = _integer(profile.node_limit, "node limit", 1000)
    child_limit = _integer(profile.child_limit, "children-per-parent limit", 16)
    hop_limit = _integer(profile.hop_limit, "hop limit", 64)
    candidates = project.cap_planning_inputs.candidates
    if not candidates:
        raise ValueError("CAP preflight blocked: no approved candidate sites")
    if len(candidates) > MAX_CANDIDATES:
        raise ValueError(f"CAP candidate sites exceed safety cap {MAX_CANDIDATES}")
    return distance, node_limit, child_limit, hop_limit


def _canonical_link(a: str, b: str, distance: float) -> tuple[str, str, str, float]:
    if a == b:
        raise ValueError("CAP topology forbids self-links")
    left, right = sorted((a, b))
    return left, right, f"cap-link/{left}/{right}", round(distance, 6)


def _adjacency(vertices: list[dict], limit: float) -> tuple[dict[str, list[tuple[str, float]]], int, list[tuple[str, str, str, float]]]:
    """Bounded STRtree distance graph; comparisons retain unrounded metres."""
    if len(vertices) > MAX_VERTICES:
        raise ValueError(f"CAP graph vertices exceed safety cap {MAX_VERTICES}")
    tree = STRtree([Point(item["x"], item["y"]) for item in vertices])
    adjacent = {item["id"]: [] for item in vertices}
    links: list[tuple[str, str, str, float]] = []
    evaluations = 0
    by_index = {index: item for index, item in enumerate(vertices)}
    for index, item in by_index.items():
        indices = tree.query(Point(item["x"], item["y"]).buffer(limit + EDGE_TOLERANCE_M))
        for other_index in indices:
            other_index = int(other_index)
            if other_index <= index:
                continue
            evaluations += 1
            if evaluations > MAX_EDGE_EVALUATIONS:
                raise ValueError(f"CAP spatial distance evaluations exceed safety cap {MAX_EDGE_EVALUATIONS}")
            other = by_index[other_index]
            distance = math.hypot(item["x"] - other["x"], item["y"] - other["y"])
            if math.isfinite(distance) and distance <= limit + EDGE_TOLERANCE_M:
                left, right, link_id, persisted = _canonical_link(item["id"], other["id"], distance)
                links.append((left, right, link_id, persisted))
                adjacent[item["id"]].append((other["id"], distance))
                adjacent[other["id"]].append((item["id"], distance))
                if len(links) > MAX_EDGES:
                    raise ValueError(f"CAP graph edges exceed safety cap {MAX_EDGES}")
    for key in adjacent:
        adjacent[key].sort(key=lambda value: (value[1], value[0]))
    return adjacent, evaluations, sorted(links, key=lambda item: item[2])


def _forest(roots: list[dict], nodes: list[dict], adjacency: dict[str, list[tuple[str, float]]], node_limit: int, child_limit: int, hop_limit: int, appliance_counting: str, primary_locks: dict[str, str], parent_locks: dict[str, str], auto_assign: bool = True) -> dict[str, dict]:
    root_ids = {root["id"] for root in roots}
    if any(node in root_ids for node in parent_locks):
        raise ValueError("CAP topology forbids a root parent lock")
    node_ids = {node["id"] for node in nodes}
    for node, root in primary_locks.items():
        if node not in node_ids or root not in root_ids:
            raise ValueError("CAP primary assignment lock references a missing node or selected CAP")
    for node, parent in parent_locks.items():
        if node not in node_ids or parent not in node_ids | root_ids:
            raise ValueError("CAP parent lock references a missing node or selected CAP")
        if node == parent:
            raise ValueError("CAP topology forbids self-parenting")
        if all(neighbor != parent for neighbor, _ in adjacency[node]):
            raise ValueError("CAP parent lock is not a distance-qualified graph edge")
    # Detect directed cycles in user locks before traversal, including longer cycles.
    for start in parent_locks:
        seen: set[str] = set()
        current = start
        while current in parent_locks:
            current = parent_locks[current]
            if current == start or current in seen:
                raise ValueError("CAP parent locks contain a cycle")
            seen.add(current)
    counts = {root["id"]: (1 if appliance_counting == "included" else 0) for root in roots}
    children = {vertex: 0 for vertex in root_ids | node_ids}
    assignment: dict[str, dict] = {}
    queue = deque((root["id"], root["id"], 0) for root in sorted(roots, key=lambda item: item["id"]))
    while queue:
        parent, gateway, hop = queue.popleft()
        if hop >= hop_limit:
            continue
        for child, distance in adjacency[parent]:
            if child not in node_ids or child in assignment or children[parent] >= child_limit or counts[gateway] >= node_limit:
                continue
            if not auto_assign and child not in primary_locks and child not in parent_locks:
                continue
            lock_gateway = primary_locks.get(child)
            lock_parent = parent_locks.get(child)
            if (lock_gateway and lock_gateway != gateway) or (lock_parent and lock_parent != parent):
                continue
            assignment[child] = {"node_id": child, "gateway_id": gateway, "parent_id": parent, "hop": hop + 1, "distance_m": round(distance, 6)}
            counts[gateway] += 1; children[parent] += 1
            queue.append((child, gateway, hop + 1))
    # A lock that could not be constructed is a contradiction, never silently repaired.
    if set(primary_locks) - set(assignment) or set(parent_locks) - set(assignment):
        raise ValueError("CAP locked assignment or parent is unreachable or exceeds a graph constraint")
    if len(assignment) > MAX_TOPOLOGY_LINKS:
        raise ValueError(f"CAP persisted topology links exceed safety cap {MAX_TOPOLOGY_LINKS}")
    return assignment


def _nodes_for_roots(nodes: list[dict], roots: list[dict], colocated_counting: str) -> list[dict]:
    if colocated_counting == "distinct_managed_node_once":
        return nodes
    co_located = {root.get("pole_id") for root in roots if root.get("pole_id")}
    return [node for node in nodes if node["pole_id"] not in co_located]


def _redundancy(policy: str, selected: list[dict], nodes: list[dict], adjacency: dict[str, list[tuple[str, float]]], limits: tuple[int, int, int], appliance_counting: str, locks: dict[str, str], parents: dict[str, str]) -> list[str]:
    if policy == "single_allowed_with_warning":
        return ["Single-CAP conceptual plan; single point of failure is not mitigated by this graph result."] if len(selected) == 1 else []
    if policy == "user_supplied_only":
        return ["Redundancy is user-supplied only; this result makes no redundancy acceptance statement."]
    # N+1 is a graph/capacity stress test, not a failover or RF claim.
    if len(selected) < 2:
        raise ValueError("CAP N+1 validation requires at least two selected CAPs")
    if len(selected) > MAX_N_PLUS_ONE_SCENARIOS:
        raise ValueError(f"CAP N+1 removal scenarios exceed safety cap {MAX_N_PLUS_ONE_SCENARIOS}")
    node_limit, child_limit, hop_limit = limits
    for removed in sorted(selected, key=lambda item: item["id"]):
        survivors = [item for item in selected if item["id"] != removed["id"]]
        surviving_locks = {node: root for node, root in locks.items() if root in {r["id"] for r in survivors}}
        trial = _forest(survivors, nodes, adjacency, node_limit, child_limit, hop_limit, appliance_counting, surviving_locks, parents)
        if len(trial) != len(nodes):
            raise ValueError(f"CAP N+1 graph validation failed after removal of {removed['candidate_id']}")
    return ["N+1 result is a deterministic distance-graph/capacity stress test only; it does not establish RF or failover behavior."]


def calculate_cap_plan(project: Project) -> CapPlanningResult:
    distance_limit, node_limit, child_limit, hop_limit = _preflight(project)
    if not project.projected_crs:
        raise ValueError("CAP planning requires a selected projected CRS with metre axes")
    crs = validate_projected_metre_crs(project.projected_crs)
    transformer, _ = project_transformers(crs)
    profile, inputs = project.cap_planning_inputs.profile, project.cap_planning_inputs
    source = {pole.id: pole for pole in project.source.poles}
    nodes: list[dict[str, Any]] = []
    for pole in sorted(project.source.poles, key=lambda item: (item.sequence_index, item.id)):
        edit = project.pole_edits.get(pole.id)
        fixture = edit.fixture_type if edit and edit.fixture_type else project.defaults.fixture_type
        # A disabled fixture may remain in the immutable customer source, but cannot
        # silently participate as a managed CAP node.
        active = edit.active if edit and edit.active is not None else True
        if not active or getattr(profile.node_policy, fixture.value) is not CapNodeDisposition.NODE or pole.id in inputs.excluded_node_ids:
            continue
        x, y = transformer.transform(pole.longitude, pole.latitude)
        if not all(math.isfinite(v) for v in (x, y)):
            raise ValueError(f"CAP node {pole.id} projected to non-finite coordinates")
        nodes.append({"id": f"fixture/{pole.id}", "pole_id": pole.id, "x": x, "y": y})
    if len(nodes) > MAX_PARTICIPATING_NODES:
        raise ValueError(f"CAP eligible nodes exceed safety cap {MAX_PARTICIPATING_NODES}")
    roots = []
    for candidate in sorted(inputs.candidates, key=lambda item: item.id):
        feasible = all(value is True for value in (candidate.mounting_confirmed, candidate.power_confirmed, candidate.backhaul_confirmed, candidate.enclosure_confirmed)) and candidate.survey_status == "confirmed" and candidate.indoor_outdoor != "unknown"
        if candidate.prohibited or candidate.id in inputs.excluded_candidate_ids:
            continue
        if not feasible:
            if profile.operation_mode == "validate" and (candidate.locked_selected or candidate.id in inputs.locked_selected_candidate_ids):
                raise ValueError(f"CAP selected candidate {candidate.id} has unresolved feasibility")
            continue
        coordinate = (source[candidate.pole_id].longitude, source[candidate.pole_id].latitude) if candidate.kind == "existing_pole" else candidate.wgs84_coordinate
        try:
            x, y = transformer.transform(*coordinate)
        except ProjError as exc:
            raise ValueError(f"CAP candidate {candidate.id} cannot be projected") from exc
        roots.append({"id": f"gateway/{candidate.id}", "candidate_id": candidate.id, "pole_id": candidate.pole_id, "x": x, "y": y, "preferred": candidate.preferred, "locked": candidate.locked_selected, "priority": candidate.priority})
    candidate_by_id = {root["candidate_id"]: root for root in roots}
    missing_locks = set(inputs.locked_selected_candidate_ids) - set(candidate_by_id)
    if missing_locks:
        raise ValueError(f"CAP selected lock references excluded or missing candidate: {sorted(missing_locks)}")
    selected = [root for root in roots if root["locked"] or root["candidate_id"] in inputs.locked_selected_candidate_ids]
    if profile.operation_mode == "validate" and not selected:
        raise ValueError("CAP validate mode requires explicit selected CAP locks")
    if profile.operation_mode == "recommend" and profile.mode_permission != "recommend_from_approved_pool":
        raise ValueError("CAP profile mode conflicts with approved mode permission")
    if profile.operation_mode == "validate" and profile.mode_permission not in {"validate_only", "recommend_from_approved_pool"}:
        raise ValueError("CAP profile mode conflicts with approved mode permission")
    if len(selected) > MAX_SELECTED_CAPS:
        raise ValueError(f"CAP selected candidates exceed safety cap {MAX_SELECTED_CAPS}")
    # The complete graph is constructed once from all eligible roots/nodes; each
    # candidate-selection pass rebuilds its constrained forest from this graph.
    adjacency, evaluations, canonical_links = _adjacency([*roots, *nodes], distance_limit)
    if profile.operation_mode == "recommend":
        # Locked selections are an immutable first step, not just a bias in the
        # greedy score.  Build their full constrained forest before considering
        # any additional candidate, then score only still-unserved nodes.
        locked_nodes = _nodes_for_roots(nodes, selected, str(profile.colocated_fixture_counting.value))
        locked_forest = _forest(selected, locked_nodes, adjacency, node_limit, child_limit, hop_limit, str(profile.gateway_appliance_counting.value), inputs.primary_assignment_locks, inputs.parent_locks)
        remaining = {node["id"] for node in locked_nodes if node["id"] not in locked_forest}
        selected_ids = {root["id"] for root in selected}
        score_trace = []
        while remaining:
            ranked = []
            for root in roots:
                if root["id"] in selected_ids:
                    continue
                trial = [*selected, root]
                trial_nodes = _nodes_for_roots(nodes, trial, str(profile.colocated_fixture_counting.value))
                trial_forest = _forest(trial, trial_nodes, adjacency, node_limit, child_limit, hop_limit, str(profile.gateway_appliance_counting.value), inputs.primary_assignment_locks, inputs.parent_locks)
                reachable = [node for node in trial_nodes if node["id"] in remaining and node["id"] in trial_forest]
                candidate = next(item for item in inputs.candidates if item.id == root["candidate_id"])
                ranked.append((-len(reachable), candidate.priority, 0 if candidate.kind == "existing_pole" else 1, candidate.id, root, reachable))
            if not ranked:
                break
            best = min(ranked, key=lambda item: item[:4])
            if not best[5]:
                break
            selected.append(best[4]); selected_ids.add(best[4]["id"])
            remaining -= {node["id"] for node in best[5]}
            score_trace.append({"candidate_id": best[4]["candidate_id"], "marginal_serviceable_nodes": len(best[5]), "priority": best[1]})
            if len(selected) >= MAX_SELECTED_CAPS:
                break
    else:
        score_trace = []
    active_nodes = _nodes_for_roots(nodes, selected, str(profile.colocated_fixture_counting.value))
    assignments = _forest(selected, active_nodes, adjacency, node_limit, child_limit, hop_limit, str(profile.gateway_appliance_counting.value), inputs.primary_assignment_locks, inputs.parent_locks, auto_assign=profile.operation_mode == "recommend" or profile.auto_assign_unlocked_nodes)
    unresolved = sorted(node["id"] for node in active_nodes if node["id"] not in assignments)
    warnings = _redundancy(str(profile.redundancy.value), selected, active_nodes, adjacency, (node_limit, child_limit, hop_limit), str(profile.gateway_appliance_counting.value), inputs.primary_assignment_locks, inputs.parent_locks)
    payload = {"model_version": "jnet1-graph-planning-1.0.0", "projected_crs": project.projected_crs, "disclaimer": DISCLAIMER, "heuristic": "deterministic non-optimal graph heuristic", "selected_candidate_ids": [r["candidate_id"] for r in selected], "assignments": [assignments[key] for key in sorted(assignments)], "canonical_links": [{"left_id": left, "right_id": right, "id": link_id, "distance_m": distance} for left, right, link_id, distance in canonical_links], "node_snapshots": [{"id": node["id"], "kind": "fixture_node", "source_pole_id": node["pole_id"], "candidate_id": None, "projected_x_m": node["x"], "projected_y_m": node["y"]} for node in nodes], "candidate_snapshots": [{"id": root["id"], "kind": "gateway_root", "source_pole_id": root["pole_id"], "candidate_id": root["candidate_id"], "projected_x_m": root["x"], "projected_y_m": root["y"]} for root in roots], "unresolved_node_ids": unresolved, "objective_trace": score_trace, "limits": {"link_distance_m": distance_limit, "node_limit": node_limit, "child_limit": child_limit, "hop_limit": hop_limit, "edge_evaluations": evaluations, "canonical_link_count": len(canonical_links)}, "provenance": {"constraints_catalog": {"version": CAP_CONSTRAINTS_VERSION, "sha256": CAP_CONSTRAINTS_SHA256}, "datasheet_revision": CAP_DATASHEET_REVISION, "profile_constraints": {name: getattr(profile, name).model_dump(mode="json") for name in ("product_mapping", "variant", "band_and_jurisdiction", "link_distance_m", "node_limit", "child_limit", "hop_limit", "gateway_appliance_counting", "colocated_fixture_counting", "redundancy")}, "operation_mode": profile.operation_mode, "projected_crs": project.projected_crs, "safety_caps": {"participating_nodes": MAX_PARTICIPATING_NODES, "candidate_sites": MAX_CANDIDATES, "selected_caps": MAX_SELECTED_CAPS, "vertices": MAX_VERTICES, "edge_evaluations": MAX_EDGE_EVALUATIONS, "edges": MAX_EDGES, "topology_links": MAX_TOPOLOGY_LINKS, "improvement_passes": MAX_IMPROVEMENT_PASSES, "n_plus_one_scenarios": MAX_N_PLUS_ONE_SCENARIOS, "serialized_payload_bytes": MAX_SERIALIZED_PAYLOAD_BYTES}}, "warnings": warnings}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    result = CapPlanningResult(result_sha256=digest, assignments=[CapAssignment(**item) for item in payload["assignments"]], canonical_links=[CapGraphLink(**item) for item in payload["canonical_links"]], node_snapshots=[CapVertexSnapshot(**item) for item in payload["node_snapshots"]], candidate_snapshots=[CapVertexSnapshot(**item) for item in payload["candidate_snapshots"]], objective_trace=[CapScoreTrace(**item) for item in payload["objective_trace"]], limits=CapPlanningLimits(**payload["limits"]), **{key: value for key, value in payload.items() if key not in {"assignments", "canonical_links", "node_snapshots", "candidate_snapshots", "objective_trace", "limits"}})
    if len(result.model_dump_json().encode("utf-8")) > MAX_SERIALIZED_PAYLOAD_BYTES:
        raise ValueError(f"CAP serialized planning payload exceeds safety cap {MAX_SERIALIZED_PAYLOAD_BYTES} bytes")
    return result


def apply_cap_result(project: Project, result: CapPlanningResult) -> Project:
    updated = deepcopy(project)
    updated.cap_calculations.status = "calculated"
    updated.cap_calculations.result = result
    updated.cap_calculations.calculation_input_sha256 = cap_input_sha256(updated)
    updated.cap_calculations.calculated_at = utc_now()
    updated.cap_calculations.warnings = list(result.warnings)
    updated.cap_recommendations.selected_candidate_ids = list(result.selected_candidate_ids)
    updated.cap_recommendations.result_sha256 = result.result_sha256
    return updated
