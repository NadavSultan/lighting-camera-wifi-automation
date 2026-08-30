export const CAP_DISCLAIMER = "Distance-qualified conceptual link; not RF-predicted. Graph-and-constraint planning only; not coverage, capacity, performance, service quality, installation feasibility, or compliance.";

export function capBlockers(inputs) {
  const profile = inputs.profile;
  const blockers = [];
  for (const key of ["product_mapping", "variant", "band_and_jurisdiction", "link_distance_m", "node_limit", "child_limit", "hop_limit", "gateway_appliance_counting", "colocated_fixture_counting", "redundancy"]) {
    if (profile[key]?.status !== "known" || profile[key]?.conflict_state === "unresolved") blockers.push(key);
  }
  for (const type of ["LITE", "WIFI", "SMART"]) if (profile.node_policy?.[type] === "unknown") blockers.push(`${type}_node_policy`);
  if (profile.mode_permission === "unknown") blockers.push("mode_permission");
  if (!inputs.candidates?.some((candidate) => !candidate.prohibited && candidate.mounting_confirmed && candidate.power_confirmed && candidate.backhaul_confirmed && candidate.enclosure_confirmed && candidate.survey_status === "confirmed" && candidate.indoor_outdoor !== "unknown")) blockers.push("feasible_candidate");
  return blockers;
}

export function isCapResultStale(project) {
  const layer = project?.cap_calculations;
  // Result and input digests intentionally describe different payloads, so comparing
  // them would label every valid result stale. The authoritative backend clears the
  // layer whenever its canonical input fingerprint changes.
  return Boolean(layer?.result && (layer.status !== "calculated" || !layer.calculation_input_sha256));
}

function significantCandidate(candidate) {
  if (!candidate) return candidate;
  const { notes, created_at, modified_at, ...significant } = candidate;
  return significant;
}

export function capSignificantProjectChange(previous, next) {
  if (!previous || !next) return Boolean(previous || next);
  const poleState = (project) => project.source.poles.map((pole) => {
    const edit = project.pole_edits[pole.id] ?? {};
    return [pole.id, pole.sequence_index, edit.fixture_type ?? project.defaults.fixture_type, edit.active ?? true, edit.location_edit_authorized === true ? [edit.longitude ?? pole.longitude, edit.latitude ?? pole.latitude] : [pole.longitude, pole.latitude]];
  });
  const inputs = (project) => ({
    profile: project.cap_planning_inputs.profile,
    candidates: project.cap_planning_inputs.candidates.map(significantCandidate).sort((a, b) => a.id.localeCompare(b.id)),
    excluded_node_ids: [...project.cap_planning_inputs.excluded_node_ids].sort(),
    excluded_candidate_ids: [...project.cap_planning_inputs.excluded_candidate_ids].sort(),
    locked_selected_candidate_ids: [...project.cap_planning_inputs.locked_selected_candidate_ids].sort(),
    primary_assignment_locks: project.cap_planning_inputs.primary_assignment_locks,
    parent_locks: project.cap_planning_inputs.parent_locks,
    projected_crs: project.projected_crs,
    poles: poleState(project),
  });
  return JSON.stringify(inputs(previous)) !== JSON.stringify(inputs(next));
}

export function invalidateCapIfSignificant(previous, next) {
  if (!capSignificantProjectChange(previous, next)) return next;
  const invalidated = structuredClone(next);
  invalidated.cap_calculations = { status: "not-calculated", calculation_input_sha256: null, calculated_at: null, result: null, warnings: [] };
  invalidated.cap_recommendations = { selected_candidate_ids: [], result_sha256: null };
  return invalidated;
}

export function capOperationEnabled(project, operation) {
  if (!project || capBlockers(project.cap_planning_inputs).length) return false;
  const profile = project.cap_planning_inputs.profile;
  return operation === "calculate" || profile.operation_mode === operation;
}
