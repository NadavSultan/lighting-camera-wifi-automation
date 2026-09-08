"use client";

import { useEffect, useRef } from "react";
import type { CapCandidateSite, EffectivePole, FixtureType, Project } from "../lib/types";
import { CAP_DISCLAIMER, capBlockers, capOperationEnabled } from "../lib/phase6-cap-workflows.mjs";
import { blockerFocusTarget, blockerLabel, candidateDisplayLabel, capResultSummary } from "../lib/cap-workflow-view.mjs";

type CapPlanningPanelProps = {
  project: Project | null;
  selected: EffectivePole | null;
  busy: boolean;
  focused: boolean;
  focusNonce: number;
  manualCapLongitude: string;
  manualCapLatitude: string;
  onManualCapLongitude: (value: string) => void;
  onManualCapLatitude: (value: string) => void;
  mutateProject: (recipe: (draft: Project) => void) => void;
  runCap: (operation: "calculate" | "validate" | "recommend") => void;
  addSelectedPoleCapCandidate: () => void;
  addManualCapCandidate: () => void;
  updateCapCandidate: (candidate: CapCandidateSite, patch: Partial<CapCandidateSite>) => void;
  removeCapCandidate: (candidateId: string) => void;
  onShowSelectedSites: () => void;
  onFocusCandidate: (candidateId: string) => void;
  onReviewInput: (elementId: string) => void;
};

export default function CapPlanningPanel({
  project,
  selected,
  busy,
  focused,
  focusNonce,
  manualCapLongitude,
  manualCapLatitude,
  onManualCapLongitude,
  onManualCapLatitude,
  mutateProject,
  runCap,
  addSelectedPoleCapCandidate,
  addManualCapCandidate,
  updateCapCandidate,
  removeCapCandidate,
  onShowSelectedSites,
  onFocusCandidate,
  onReviewInput,
}: CapPlanningPanelProps) {
  const panelRef = useRef<HTMLElement | null>(null);
  const summary = capResultSummary(project);
  const blockers = project ? capBlockers(project.cap_planning_inputs) : [];

  useEffect(() => {
    if (focusNonce > 0 && panelRef.current) {
      panelRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
      panelRef.current.focus({ preventScroll: true });
    }
  }, [focusNonce]);

  return (
    <section
      ref={panelRef}
      id="cap-planning-panel"
      className={`section cap-planning-panel${focused ? " cap-planning-panel-focused" : ""}`}
      tabIndex={-1}
      aria-label="CAP Planning"
    >
      <div className="section-heading">
        <h3>CAP Planning</h3>
        <span className="helper">Phase 6 · JNET1 graph</span>
      </div>
      <p className="lighting-disclaimer">{CAP_DISCLAIMER}</p>

      {!project ? (
        <p className="helper">Import or create a project to preserve unknown CAP inputs and inspect blockers.</p>
      ) : (
        <>
          <div className="cap-result-summary" aria-live="polite">
            {summary.state === "not-calculated" && (
              <p className="helper">No current CAP result. Complete prerequisites, then Calculate / rank, Validate, or Recommend.</p>
            )}
            {summary.state === "error" && (
              <div className="warning-card"><strong>CAP calculation error</strong><p>The last operation failed. Review inputs and try again. This is not an installation-ready answer.</p></div>
            )}
            {(summary.state === "current" || summary.state === "current-with-unresolved") && (
              <>
                <p><strong>Recommended CAP units: {summary.selectedIds.length}</strong></p>
                {summary.state === "current-with-unresolved" && (
                  <div className="warning-card"><strong>{summary.unresolvedIds.length} unresolved node{summary.unresolvedIds.length === 1 ? "" : "s"}</strong><p>Incomplete graph coverage — not an installation-ready answer.</p></div>
                )}
                {summary.selectedIds.length === 0 ? (
                  <p className="helper">Current result has zero selected CAP sites.</p>
                ) : (
                  <ul className="cap-selected-list">
                    {summary.selectedIds.map((id) => (
                      <li key={id}>
                        <span><code>{id}</code> · {candidateDisplayLabel(project, id)}</span>
                        <button type="button" className="quiet-button" onClick={() => onFocusCandidate(id)}>Locate</button>
                      </li>
                    ))}
                  </ul>
                )}
                <button type="button" className="quiet-button" onClick={onShowSelectedSites} disabled={!summary.selectedIds.length}>
                  Show selected sites on map
                </button>
                {project.cap_calculations.result?.warnings?.length ? (
                  <div className="cap-result-warnings">
                    {project.cap_calculations.result.warnings.map((warning) => (
                      <div className="warning-card" key={warning}>{warning}</div>
                    ))}
                  </div>
                ) : null}
                <p className="helper">{CAP_DISCLAIMER}</p>
              </>
            )}
          </div>

          <div className="cap-panel-block">
            <h4>Prerequisites</h4>
            <p className="helper">Product, variant, band/jurisdiction, explicit LITE/WIFI/SMART node dispositions, design limits, counting, redundancy, and surveyed candidates remain separate user inputs.</p>
            {blockers.length ? (
              <div className="warning-card">
                <strong>CAP preflight blockers</strong>
                <ul className="cap-blocker-list">
                  {blockers.map((key) => {
                    const target = blockerFocusTarget(key);
                    return (
                      <li key={key}>
                        <span>{blockerLabel(key)}</span>
                        {target && (
                          <button type="button" className="quiet-button" onClick={() => onReviewInput(target)}>Review input</button>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            ) : (
              <div className="warning-card info">Preflight complete for the selected test/project inputs.</div>
            )}

            <details className="cap-required-inputs" open>
              <summary>Required CAP inputs and candidates</summary>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="cap-field-operation_mode">Operation mode</label>
                <select id="cap-field-operation_mode" value={project.cap_planning_inputs.profile.operation_mode} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.operation_mode = event.target.value as "validate" | "recommend"; })}>
                  <option value="validate">Validate explicit CAP selection</option>
                  <option value="recommend">Recommend from approved pool</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="cap-field-mode_permission">Mode permission</label>
                <select id="cap-field-mode_permission" value={project.cap_planning_inputs.profile.mode_permission} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.mode_permission = event.target.value as "validate_only" | "recommend_from_approved_pool" | "unknown"; })}>
                  <option value="unknown">Unknown — blocks planning</option>
                  <option value="validate_only">Validate only</option>
                  <option value="recommend_from_approved_pool">Recommend from approved pool</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="cap-field-gateway_appliance_counting">Gateway appliance counting</label>
                <select id="cap-field-gateway_appliance_counting" value={String(project.cap_planning_inputs.profile.gateway_appliance_counting.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.gateway_appliance_counting; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}>
                  <option value="">Unknown — blocks planning</option>
                  <option value="included">Included in per-CAP node count</option>
                  <option value="excluded">Excluded from per-CAP node count</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="cap-field-colocated_fixture_counting">Co-located fixture counting</label>
                <select id="cap-field-colocated_fixture_counting" value={String(project.cap_planning_inputs.profile.colocated_fixture_counting.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.colocated_fixture_counting; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}>
                  <option value="">Unknown — blocks planning</option>
                  <option value="distinct_managed_node_once">Distinct managed fixture node once</option>
                  <option value="merged_not_separate">Merged, not a separate fixture node</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="cap-field-redundancy">Redundancy policy</label>
                <select id="cap-field-redundancy" value={String(project.cap_planning_inputs.profile.redundancy.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.redundancy; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}>
                  <option value="">Unknown — blocks planning</option>
                  <option value="single_allowed_with_warning">Single allowed with warning</option>
                  <option value="n_plus_one_validation">N+1 graph validation</option>
                  <option value="user_supplied_only">User supplied only</option>
                </select>
              </div>
            </div>

            <div className="form-grid">
              {(["LITE", "WIFI", "SMART"] as FixtureType[]).map((type) => (
                <div className="field" key={type}>
                  <label htmlFor={`cap-field-node-${type}`}>{type} node disposition</label>
                  <select id={`cap-field-node-${type}`} value={project.cap_planning_inputs.profile.node_policy[type]} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.node_policy[type] = event.target.value as "node" | "non_node" | "unknown"; })}>
                    <option value="unknown">Unknown — blocks planning</option>
                    <option value="node">Node</option>
                    <option value="non_node">Non-node</option>
                  </select>
                </div>
              ))}
            </div>

            <div className="form-grid">
              {(["product_mapping", "variant", "band_and_jurisdiction", "link_distance_m", "node_limit", "child_limit", "hop_limit"] as const).map((field) => (
                <div className="field" key={field}>
                  <label htmlFor={`cap-field-${field}`}>{field.replaceAll("_", " ")} · provenance-bearing</label>
                  <input
                    id={`cap-field-${field}`}
                    value={String(project.cap_planning_inputs.profile[field].value ?? "")}
                    onChange={(event) => mutateProject((draft) => {
                      const value = event.target.value;
                      const target = draft.cap_planning_inputs.profile[field];
                      target.value = field.endsWith("limit") || field === "link_distance_m" ? (value === "" ? null : Number(value)) : value || null;
                      target.status = value ? "known" : "unknown";
                      target.source = value ? "user-entered project input" : null;
                      target.applicability = value ? "project planning" : null;
                      target.classification = value ? "user_approved_assumption" : "unknown";
                    })}
                  />
                </div>
              ))}
            </div>
            </details>
          </div>

          <div className="cap-panel-block" id="cap-section-candidates">
            <h4>Candidates and locks</h4>
            <div className="button-row">
              <button className="quiet-button" onClick={addSelectedPoleCapCandidate} disabled={!selected || busy}>Add selected pole as CAP site</button>
              <button className="quiet-button" disabled={!selected || busy} onClick={() => selected && mutateProject((draft) => {
                const nodeId = `fixture/${selected.id}`;
                const ids = draft.cap_planning_inputs.excluded_node_ids;
                draft.cap_planning_inputs.excluded_node_ids = ids.includes(nodeId) ? ids.filter((id) => id !== nodeId) : [...ids, nodeId];
              })}>
                {selected && project.cap_planning_inputs.excluded_node_ids.includes(`fixture/${selected.id}`) ? "Include current CAP node" : "Exclude current CAP node"}
              </button>
            </div>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="manual-cap-longitude">Manual non-pole longitude</label>
                <input id="manual-cap-longitude" type="number" min="-180" max="180" step="any" value={manualCapLongitude} onChange={(event) => onManualCapLongitude(event.target.value)} />
              </div>
              <div className="field">
                <label htmlFor="manual-cap-latitude">Manual non-pole latitude</label>
                <input id="manual-cap-latitude" type="number" min="-90" max="90" step="any" value={manualCapLatitude} onChange={(event) => onManualCapLatitude(event.target.value)} />
              </div>
            </div>
            <div className="button-row">
              <button className="quiet-button" onClick={addManualCapCandidate} disabled={busy}>Add distinct manual non-pole CAP site</button>
            </div>
            {project.cap_planning_inputs.candidates.map((candidate) => (
              <div className="priority-row" key={candidate.id}>
                <strong>{candidate.kind === "existing_pole" ? `Pole ${candidate.pole_id}` : "Manual non-pole site"}</strong>
                <span>mounting {String(candidate.mounting_confirmed)} · power {String(candidate.power_confirmed)} · backhaul {String(candidate.backhaul_confirmed)} · survey {candidate.survey_status} · priority {candidate.priority}</span>
                <div>
                  <button className="quiet-button" onClick={() => updateCapCandidate(candidate, { mounting_confirmed: true, power_confirmed: true, backhaul_confirmed: true, enclosure_confirmed: true, indoor_outdoor: "outdoor", survey_status: "confirmed", notes: "TEST-ONLY feasibility values; not approved site engineering." })}>Mark test-only feasible</button>
                  <button className="quiet-button" onClick={() => updateCapCandidate(candidate, { preferred: !candidate.preferred })}>{candidate.preferred ? "Remove preference" : "Prefer"}</button>
                  <button className="quiet-button" onClick={() => updateCapCandidate(candidate, { prohibited: !candidate.prohibited })}>{candidate.prohibited ? "Allow" : "Prohibit"}</button>
                  <button className="quiet-button" onClick={() => updateCapCandidate(candidate, { locked_selected: !candidate.locked_selected })}>{candidate.locked_selected ? "Unlock selected" : "Lock selected"}</button>
                  <button className="quiet-button" disabled={!selected} onClick={() => selected && mutateProject((draft) => {
                    const nodeId = `fixture/${selected.id}`;
                    const gatewayId = `gateway/${candidate.id}`;
                    const locks = draft.cap_planning_inputs.primary_assignment_locks;
                    if (locks[nodeId] === gatewayId) delete locks[nodeId]; else locks[nodeId] = gatewayId;
                  })}>{selected && project.cap_planning_inputs.primary_assignment_locks[`fixture/${selected.id}`] === `gateway/${candidate.id}` ? "Unlock current node assignment" : "Lock current node to this CAP"}</button>
                  <button className="quiet-button" disabled={!selected} onClick={() => selected && mutateProject((draft) => {
                    const nodeId = `fixture/${selected.id}`;
                    const gatewayId = `gateway/${candidate.id}`;
                    const locks = draft.cap_planning_inputs.parent_locks;
                    if (locks[nodeId] === gatewayId) delete locks[nodeId]; else locks[nodeId] = gatewayId;
                  })}>{selected && project.cap_planning_inputs.parent_locks[`fixture/${selected.id}`] === `gateway/${candidate.id}` ? "Unlock current parent" : "Lock current parent to this CAP"}</button>
                  <button className="quiet-button" onClick={() => mutateProject((draft) => {
                    const ids = draft.cap_planning_inputs.excluded_candidate_ids;
                    draft.cap_planning_inputs.excluded_candidate_ids = ids.includes(candidate.id) ? ids.filter((id) => id !== candidate.id) : [...ids, candidate.id];
                  })}>{project.cap_planning_inputs.excluded_candidate_ids.includes(candidate.id) ? "Include candidate" : "Exclude candidate"}</button>
                  <button className="quiet-button" onClick={() => onFocusCandidate(candidate.id)}>Locate</button>
                  <button className="quiet-button" onClick={() => removeCapCandidate(candidate.id)}>Delete site</button>
                </div>
              </div>
            ))}
            {!project.cap_planning_inputs.candidates.length && <p className="helper">No CAP candidates yet. Add an existing-pole or distinct manual non-pole site.</p>}
          </div>

          <div className="cap-panel-block">
            <h4>Actions</h4>
            <div className="button-row">
              <button className="quiet-button" onClick={() => runCap("calculate")} disabled={!capOperationEnabled(project, "calculate") || busy} title="Calculate / rank: inspect candidate ranking">Calculate / rank</button>
              <button className="quiet-button" onClick={() => runCap("validate")} disabled={!capOperationEnabled(project, "validate") || busy} title="Validate: check your explicit selection">Validate</button>
              <button className="quiet-button" onClick={() => runCap("recommend")} disabled={!capOperationEnabled(project, "recommend") || busy} title="Recommend: choose from the approved candidate pool">Recommend</button>
            </div>
            <p className="helper">Calculate / rank: inspect candidate ranking. Validate: check your explicit selection. Recommend: choose from the approved candidate pool.</p>
            <p>{project.cap_planning_inputs.candidates.length} explicit CAP candidate sites · {project.cap_recommendations.selected_candidate_ids.length} selected.</p>
          </div>

          <details className="lighting-provenance">
            <summary>Advanced topology, score trace, and provenance</summary>
            {project.cap_calculations.result ? (
              <>
                <p>Fingerprint {project.cap_calculations.calculation_input_sha256} · CRS {project.cap_calculations.result.projected_crs}</p>
                {project.cap_calculations.result.assignments.map((item) => (
                  <p key={item.node_id}>{item.node_id} → {item.parent_id} · hop {item.hop} · {item.distance_m.toFixed(6)} m · distance-qualified conceptual link; not RF-predicted</p>
                ))}
                {project.cap_calculations.result.warnings.map((warning) => <p key={warning}>{warning}</p>)}
              </>
            ) : (
              <p className="helper">No topology until a successful calculation exists.</p>
            )}
          </details>
        </>
      )}
    </section>
  );
}
