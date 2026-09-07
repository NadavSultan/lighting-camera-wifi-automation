/**
 * Presentation helpers for CAP workflow clarity.
 * Reuses blocker keys from phase6-cap-workflows; does not invent operational defaults.
 */

/**
 * @param {object | null | undefined} project
 * @returns {{ state: "not-calculated" | "current" | "current-with-unresolved" | "error", selectedIds: string[], unresolvedIds: string[] }}
 */
export function capResultSummary(project) {
  if (!project?.cap_calculations) {
    return { state: "not-calculated", selectedIds: [], unresolvedIds: [] };
  }
  const layer = project.cap_calculations;
  if (layer.status === "error") {
    return { state: "error", selectedIds: [], unresolvedIds: [] };
  }
  if (layer.status !== "calculated" || !layer.result) {
    return { state: "not-calculated", selectedIds: [], unresolvedIds: [] };
  }
  const selectedIds = Array.isArray(project.cap_recommendations?.selected_candidate_ids)
    ? [...project.cap_recommendations.selected_candidate_ids]
    : [];
  const unresolvedIds = Array.isArray(layer.result.unresolved_node_ids)
    ? [...layer.result.unresolved_node_ids]
    : [];
  return {
    state: unresolvedIds.length ? "current-with-unresolved" : "current",
    selectedIds,
    unresolvedIds,
  };
}

const BLOCKER_LABELS = {
  product_mapping: "Product mapping",
  variant: "Variant",
  band_and_jurisdiction: "Band / jurisdiction",
  link_distance_m: "Link distance",
  node_limit: "Node limit",
  child_limit: "Child limit",
  hop_limit: "Hop limit",
  gateway_appliance_counting: "Gateway appliance counting",
  colocated_fixture_counting: "Co-located fixture counting",
  redundancy: "Redundancy policy",
  LITE_node_policy: "LITE node disposition",
  WIFI_node_policy: "WIFI node disposition",
  SMART_node_policy: "SMART node disposition",
  mode_permission: "Mode permission",
  feasible_candidate: "Feasible CAP candidate",
};

const BLOCKER_FOCUS = {
  product_mapping: "cap-field-product_mapping",
  variant: "cap-field-variant",
  band_and_jurisdiction: "cap-field-band_and_jurisdiction",
  link_distance_m: "cap-field-link_distance_m",
  node_limit: "cap-field-node_limit",
  child_limit: "cap-field-child_limit",
  hop_limit: "cap-field-hop_limit",
  gateway_appliance_counting: "cap-field-gateway_appliance_counting",
  colocated_fixture_counting: "cap-field-colocated_fixture_counting",
  redundancy: "cap-field-redundancy",
  LITE_node_policy: "cap-field-node-LITE",
  WIFI_node_policy: "cap-field-node-WIFI",
  SMART_node_policy: "cap-field-node-SMART",
  mode_permission: "cap-field-mode_permission",
  feasible_candidate: "cap-section-candidates",
};

/**
 * @param {string} key
 */
export function blockerLabel(key) {
  return BLOCKER_LABELS[key] ?? `Unknown prerequisite (${key})`;
}

/**
 * @param {string} key
 * @returns {string | null}
 */
export function blockerFocusTarget(key) {
  return BLOCKER_FOCUS[key] ?? null;
}

/**
 * @param {object} project
 * @param {string} candidateId
 */
export function candidateDisplayLabel(project, candidateId) {
  const candidate = project?.cap_planning_inputs?.candidates?.find((item) => item.id === candidateId);
  if (!candidate) return candidateId;
  if (candidate.kind === "manual_non_pole") return "Manual non-pole site";
  const poleId = candidate.pole_id;
  const pole = project?.source?.poles?.find((item) => item.id === poleId);
  const editName = poleId ? project?.pole_edits?.[poleId]?.display_name : null;
  const name = editName || pole?.name || poleId;
  return name ? `Pole ${name}` : `Pole ${poleId ?? candidateId}`;
}
