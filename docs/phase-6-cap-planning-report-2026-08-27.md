# Phase 6 CAP planning report

Date: 2026-08-27

Scope: planning and future implementation prompt only

Outcome: **Planning artifacts complete; all 20 decisions and Phase 6 implementation subsequently authorized; Phase 6 remains open and unaccepted.**

Post-planning gate update: the user explicitly approved every recommended implementation-policy decision and then separately authorized Phase 6 implementation using GPT-5.6 Terra on 2026-08-27 after the master review and corrective pass. This does not turn test-only values into approved Miracle Mile inputs or accept/close Phase 6 before independent QA and a master gate decision.

## Authorization observed

The user authorized Phase 6 planning only. This task did not implement Phase 6, launch an implementation task, or change application code, tests, schemas, catalogs, generated contracts, `Input/`, runtime data, or accepted Phase 1-5 behavior.

The future implementation is intended for GPT-5.6 Terra only after two later gates:

1. explicit approval or replacement of every applicable implementation-policy decision in the planning contract's section 16;
2. separate explicit Phase 6 implementation authorization.

Actual Miracle Mile operational values are a later runtime-input gate, not an implementation gate. The implementation may and must support unknown product/variant, fixture node dispositions, band/jurisdiction, link distance, project node/child/hop limits, gateway/node-count convention, candidate inventory/feasibility, and redundancy selection. It must persist those unknowns without defaults and block only the dependent runtime operation through preflight. Test-only values used for automated/rendered QA are not real-project approvals.

## Repository state

Startup was completed in the exact `AGENTS.md` order before planning. The initial repository state was:

- expected and actual HEAD: `100d458a066caa28c19b48bee28d392eb9fbc073`;
- commit subject: `docs: close Phase 5 after final QA pass`;
- `main` pointed at the same commit;
- worktree checkout state: detached `HEAD` at local `main`;
- initial worktree: clean;
- Phases 1-5: accepted and formally closed;
- project schema/software: `2.5.0` / `0.5.0`;
- Phase 6 implementation and Phase 7: unauthorized.

Only the three planning documents listed below were included in the original planning commit. The final commit hashes and clean status are reported by their task handoffs because a commit cannot truthfully contain its own final hash.

Corrective review on 2026-08-27 started from clean detached HEAD `82a8aed62a8469eb891cdd97768fc265af7dd9e9` (`docs: plan Phase 6 CAP workflow`). The correction is limited to the same three planning artifacts; it does not alter the accepted application baseline or authorize implementation.

## Evidence reviewed

### Governance and accepted architecture

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `docs/current-status.md`
- `docs/implementation-plan.md`
- `docs/architecture.md`
- `docs/data-model.md`
- `docs/phase-1-completion-report.md`
- exact Git status, HEAD, and recent history

### Phase 6 engineering evidence

- `docs/cap-datasheet-extraction.md`
- `docs/reference-input-inventory.md`
- `docs/engineering-open-questions.md`
- `docs/engineering-assumptions.md`
- `docs/engineering-data-completion-report.md`
- `docs/schema-contracts.md`
- `data/network/cap-constraints.json`
- `schemas/cap-constraints.schema.json`
- `data/fixtures/fixture-types.json`

### Original PDF verification

The PDF skill was read completely before PDF work. `Input/CAP/CAP datasheet.pdf` was never edited. Poppler identified a five-page A4, unencrypted PDF with no form or JavaScript. Every page was rendered to PNG at 140 dpi and visually inspected; all five pages were also text-extracted for comparison.

Source integrity evidence already frozen by the repository was retained:

- file: `Input/CAP/CAP datasheet.pdf`;
- SHA-256: `2a1692daef1f3e0537c9c84b144a5063e2041add1e970bbf27a25dad1bb52bce`;
- document: Juganu `JL-DS-GC JNET1 GW _2308`, Rev 1.2;
- manufacturer terminology: `JNET1 Gateway (Group Controller)`, not CAP.

### Existing implementation seams

The plan inspected:

- `backend/app/models.py` strict project models, schema/version constants, `LayerState.cap_locations`, `LayerState.cap_connections`, generic `recommended_layers`, and lossless migration pattern;
- `backend/app/main.py` full-project responses, save/open/calculate paths, and existing 404/409/422 behavior;
- `backend/app/services/store.py` source immutability and temporary-file replacement;
- lighting/Wi-Fi fingerprints, stale invalidation, projected-CRS services, safety caps, and atomic-failure patterns;
- frontend typed transport, disabled `Recommend CAP` action, gated CAP layers, current green CAP colors, exact fixture colors, undo/redo, save/reopen, and rendered tests;
- project/OpenAPI generated schemas;
- Phase 5 planning, Terra-style implementation prompt, implementation report, rendered QA, independent review, corrections, focused retest, and master closure as structural precedents.

No external research was performed because it was not necessary to identify the safe planning boundary. Any later research must use primary manufacturer, regulator, or standards sources only.

## Datasheet comparison result

The repository extraction correctly records the major manufacturer statements and correctly refuses to turn marketing maxima into design rules. The following material cautions were added to the Phase 6 plan:

| Evidence | Verified observation | Planning consequence |
|---|---|---|
| Page 1 | “Up to 1,000 nodes,” up to 10 km open air, up to 8 km dense urban, indoor RJ45/outdoor cellular, and roaming are claims/capabilities. | 1,000 is a ceiling only. Range claims never become a per-link distance. Roaming never becomes a redundancy rule. |
| Page 2 | 433.05-434.79 MHz and 902-928 MHz; the document also uses 900/915 labels. | Band family, exact range, ordered variant, jurisdiction, and approval source must be explicit project inputs. |
| Page 4 | 1,000 nodes/gateway, 64 hops, 16 children/parent, 60-300 ms/hop, 40/200 kbps aggregate goodput. | Node/child/hop values may bound user design limits after product mapping; load/latency are not MVP constraints without approved inputs. |
| Page 4 | It states a 32-hop broadcast range of 300-9,600 ms while `32 × 60 ms = 1,920 ms`. | Internal latency inconsistency blocks latency enforcement pending manufacturer clarification. |
| Page 4 | A scan example assumes 3,000 responding nodes despite a 1,000-node-per-gateway maximum. | The example does not define per-gateway design load; its scope requires clarification. |
| Page 3 | Standards vary by indoor/outdoor model and market and additional local standards apply. | No compliance claim; exact ordered model certificates and jurisdiction must be verified separately. |
| Page 4 | Parent adoption uses proprietary Juganu criteria. | Phase 6 topology is an explainable graph approximation, not protocol simulation. |

The extraction also omits some nonessential datasheet details such as channel spacing and performance-example assumptions. They are not needed for the safe graph MVP and must not be silently operationalized.

## Recommended planning outcome

The safest useful MVP is a two-mode, projected-distance graph planner:

- **Validate mode** checks a user-authored CAP selection/topology.
- **Recommend-from-approved-pool mode** deterministically ranks and selects only explicit feasible candidate sites. It never generates coordinates and is labelled heuristic/non-optimal.

Recommended candidate sites may be existing customer poles or separately stored, manually placed non-pole equipment sites. Both require explicit mounting, power, backhaul, enclosure, prohibition/preference, and survey facts. A manual site is never a pole.

The engine should use an approved per-link planning distance, capacity-constrained breadth-first trees, deterministic greedy marginal selection, bounded improvement, explicit tie-breaks, manual locks/exclusions/reassignments, and optional N+1 removal revalidation. Every link remains `distance-qualified conceptual link; not RF-predicted`.

Recommended additive targets are:

- project schema `2.6.0`;
- software/API `0.6.0`;
- planning model `jnet1-graph-planning-1.0.0`;
- strict separate `cap_planning_inputs`, `cap_calculations`, and `cap_recommendations` collections;
- existing generic `recommended_layers` preserved losslessly rather than repurposed with untyped CAP data.

The corrected source precedence is binding on the future implementation design: applicable law/regulator/AHJ/adopted standards control first, followed by exact-product authoritative manufacturer hard constraints. User-approved project values and assumptions may be stricter only; they can never waive or enlarge those bounds. Conflicts and uncertain applicability remain visible and block the dependent operation rather than selecting a permissive source.

## Material decisions awaiting approval

The planning contract contains 20 numbered implementation-policy decisions. The most consequential are:

1. approve support for the supplied JNET1 Gateway/Group Controller as the provisional product record while leaving the Miracle Mile mapping nullable;
2. approve explicit `node/non_node/unknown` membership fields separately from Wi-Fi capability, without locking real-site values;
3. approve existing-pole plus manual non-pole candidate site kinds, or narrow the allowed schema/workflow;
4. authorize Validate mode and/or recommendation from an approved pool;
5. require nullable exact band/variant/jurisdiction provenance fields and runtime blocking;
6. require a nullable per-link planning distance in metres without deriving a default from 8/10 km marketing claims;
7. require nullable project node/CAP, children/parent, and hop limits bounded by 1,000/16/64;
8. approve separate provenance-bearing appliance-counting and co-located-fixture-counting fields: the recommended assumptions exclude the appliance and count an eligible co-located fixture once at zero distance/hop 1, while tests also cover included-appliance/merged-fixture alternatives, unknown blocking, self/root-parent/cycles, and no implicit node at a manual site;
9. keep load/goodput/latency out of MVP enforcement pending a traffic model and clarification;
10. approve graph planning rather than RF prediction;
11. approve candidate utility/mounting/survey field and preflight rules;
12. approve selectable single-CAP warning, N+1 graph validation, and user-supplied-only redundancy semantics without choosing a Miracle Mile value;
13. approve the deterministic non-optimal heuristic and tie-breaks;
14. approve manual locks, exclusions, reassignment, parent locks, and atomic rejection;
15. approve versions/data separation/migration;
16. approve API, 404/409/422, undo/redo, fingerprint, and stale-result behavior;
17. approve application safety caps;
18. approve terminology, green CAP layers, exact disclaimers, and warning/error semantics;
19. keep Phase 6 export JSON-only and defer reporting/KML CAP layers to Phase 7;
20. require the full adversarial acceptance matrix and independent QA gate.

No recommendation is recorded as approved by this report.

## Planning artifacts

- `docs/phase-6-cap-planning-and-implementation-contract.md` - evidence hierarchy, known/unknown facts, safe MVP, strict architecture/data/API/UI/migration design, deterministic algorithms/tie-breaks, safety caps, invalidation/provenance, adversarial acceptance matrix, and 20 implementation-policy decisions.
- `docs/phase-6-master-implementation-prompt.md` - bounded execution prompt for the authorized GPT-5.6 Terra implementation task, with exact startup, file boundary, work packages, invariants, commands, rendered QA, handoff, and stop conditions.
- `docs/phase-6-cap-planning-report-2026-08-27.md` - this evidence and gate report.

No other file is authorized or intended to change in this planning task.

## Blockers and next gate

The implementation-policy decisions and separate Phase 6 implementation authorization are approved. The Terra implementation task may proceed; it is **not** blocked merely because real-project engineering inputs are missing.

The repository still has no approved Miracle Mile CAP/product mapping, node-membership matrix, band/variant/jurisdiction, planning link distance, conservative node/child/hop limits, gateway/node-count convention, site feasibility inventory, or redundancy selection. Those are legitimate runtime `unknown` values. After implementation they must prevent dependent calculate/validate/recommend operations until entered with required provenance, but they do not prevent implementation of the approved unknown-state models, UI, preflight, algorithms, and tests.

The required review, decision approval, and separate implementation authorization gates are complete. The authorized Terra task is the next action. If the user later wants any real-site value locked into the implementation contract, record it separately and explicitly; do not infer that intent from implementation authorization. Phase 6 still requires independent QA and master acceptance, and Phase 7 remains gated.
