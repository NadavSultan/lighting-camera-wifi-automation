# Phase 6 CAP planning and implementation contract

Date: 2026-08-27

Status: planning decisions approved; implementation explicitly authorized; Phase 6 open and unaccepted

Controlling repository state: `100d458a066caa28c19b48bee28d392eb9fbc073` (`docs: close Phase 5 after final QA pass`)

## 1. Authorization boundary

The user explicitly approved all 20 implementation-policy recommendations in section 16 and separately authorized Phase 6 implementation using GPT-5.6 Terra on 2026-08-27. They are binding scope for the implementation task. This authorization does not approve real-site operational values, expand Phase 6 beyond this contract, authorize Phase 7, or accept/close Phase 6 before independent QA and a master gate decision.

Implementation-policy approval and real-project runtime input are separate gates:

- Before implementation, the user must approve the product/architecture boundary, allowed modes and site kinds, field schemas and unknown-state behavior, algorithms and tie-breaks, versions, application safety caps, terminology/disclaimers, export boundary, and acceptance matrix.
- Actual Miracle Mile operational values - including product/variant mapping, LITE/WIFI/SMART node dispositions, band/jurisdiction, link distance, project node/child/hop limits, node-count convention, candidate inventory/feasibility, and redundancy selection - may remain `unknown` while the software is implemented. The model and UI must preserve those unknowns without defaults, and runtime preflight must block the dependent calculate/validate/recommend operation until the required values and provenance are entered.
- Tests and rendered QA may use conspicuously labelled test-only inputs. They are fixtures for proving behavior and are not approvals or defaults for Miracle Mile.
- If the user wants any real-site value frozen into the implementation contract, that must be recorded as a separate explicit project-input decision; implementation-policy approval alone never locks a Miracle Mile value.

The safest useful Phase 6 MVP is explainable graph-and-constraint planning for a provisionally mapped JNET1 Gateway/Group Controller. It may validate a user-authored design and, only when separately enabled, rank and select from explicit user-approved candidate sites. It is not RF prediction and it does not establish professional, performance, service, legal, or standards compliance.

Existing-pole mode remains mandatory. Phase 6 must never create, redistribute, optimize, move, or delete a customer lighting pole. A manually entered non-pole equipment site, if approved, is separate user data and must never be added to `source.poles` or represented as a lighting pole.

### In scope after approval

- explicit project CAP/JNET1 planning inputs and their provenance;
- explicit network-node eligibility and explicit CAP candidate-site feasibility;
- user-supplied existing-pole and, if approved, manually placed non-pole candidate sites;
- deterministic projected-metre adjacency graphs from an approved planning distance;
- explainable candidate ranking, bounded heuristic CAP selection, node assignment, source-routing-tree construction, and constraint validation;
- manual CAP locks, candidate exclusions, node exclusions, primary-node reassignment locks, and deterministic revalidation;
- capacity, children-per-parent, hop, distance, required-site-utility, and selected redundancy-policy checks;
- separate user, calculated, and recommended data with fingerprints, provenance, warnings, and stale-result invalidation;
- save/reopen, undo/redo, JSON archive persistence, UI layers, and regression-safe API behavior.

### Non-goals

- verified RF coverage, link budget, propagation, terrain, foliage/building obstruction, antenna pattern, interference, channel planning, or spectrum coordination;
- throughput, latency, availability, service-quality, failover-performance, or professional design guarantees;
- legal or standards-compliance approval;
- automatic lighting-pole placement, coordinate optimization, free-space candidate generation, or movement of any customer pole;
- automatic inference of fixture participation, gateway identity, band, range, capacity margins, hop targets, or redundancy policy;
- CAP procurement/BOM approval, installation drawings, backhaul design, power design, permitting, commissioning, or field-survey substitution;
- CAP KML/KMZ, CSV/XLSX, PDF, or presentation reporting, which remains Phase 7 scope.

## 2. Source hierarchy and evidence

When sources conflict, the future implementation must apply this precedence and retain every conflict visibly:

1. applicable law, regulator, authority-having-jurisdiction (AHJ) requirement, and legally adopted standard for the installation jurisdiction;
2. authoritative exact-product manufacturer hard constraints for the ordered hardware/firmware revision, except where a stricter applicable legal/AHJ rule controls;
3. user-approved project design limits and policies, identified by approver/source/date, only when they are within every applicable item above;
4. other authoritative manufacturer engineering guidance for the exact product/revision;
5. the supplied Juganu datasheet as a manufacturer claim/specification source, with marketing claims kept non-operational unless independently qualified;
6. repository-derived values with a stated equation whose inputs obey the higher-precedence bounds;
7. user-editable engineering assumptions explicitly approved for this project, only within all higher-precedence bounds;
8. unknown, which blocks the dependent operation.

A user approval can make a project rule stricter but can never waive, enlarge, or override an applicable legal/AHJ/regulatory requirement or authoritative manufacturer hard limit. If applicability, revision, or precedence cannot be resolved, store the competing claims and block the dependent operational validation/recommendation. Do not select the more permissive value.

Marketing language is never promoted into a design rule. The frozen `data/network/cap-constraints.json` and `schemas/cap-constraints.schema.json` remain reference evidence at `1.0.0`; Phase 6 should consume them read-only and store project-specific operational inputs separately.

Evidence reviewed for this plan:

- the required repository startup and governance documents;
- `docs/cap-datasheet-extraction.md`, reference inventory, open questions, assumptions, engineering-data completion report, and schema contracts;
- `data/network/cap-constraints.json` and its Draft 2020-12 schema;
- all five visually rendered pages and extracted text of `Input/CAP/CAP datasheet.pdf`, SHA-256 `2a1692daef1f3e0537c9c84b144a5063e2041add1e970bbf27a25dad1bb52bce`;
- Phase 5 planning, implementation, rendered QA, independent review, corrective, focused-retest, and master-gate documents as structural examples;
- current Pydantic models/migrations, FastAPI error patterns, atomic project store, calculation fingerprints, UI gates/layers, `recommended_layers`, generated contracts, and tests.

No external research was necessary. Future research, if required by an unresolved approval item, must use only primary manufacturer, regulator, or standards sources and must not convert general marketing claims into project limits.

## 3. Terminology

| Term | Phase 6 meaning |
|---|---|
| CAP | Project-domain label. It is not yet confirmed to mean the supplied JNET1 Gateway/Group Controller. |
| JNET1 Gateway / Group Controller | Product named by the supplied Juganu Rev 1.2 datasheet; model family `JGW-JNET1`. |
| network node | An existing customer pole fixture explicitly classified by the approved project profile as a JNET1 node. It is not inferred from Wi-Fi capability. |
| candidate site | A user-approved location at which a gateway could be considered. It is either an existing-pole reference or a separate manual non-pole equipment site. |
| selected CAP | A candidate site chosen and locked by the user or selected by the bounded recommendation heuristic. Selection is a planning recommendation, not installation approval. |
| link | A graph edge allowed only because projected separation is within the user-approved planning distance. It is not a predicted RF link. |
| parent/child | A directed relationship in the conceptual source-routing tree. It does not reproduce Juganu's proprietary parent-adoption algorithm. |
| hard manufacturer maximum | A stated product/protocol ceiling. It is never a preferred operating point. |
| project design limit | A conservative project input approved by the user/engineer and bounded by an applicable hard maximum where one exists. |
| planning assumption | A user-editable, approval-bearing value used only for graph planning; it is neither manufacturer-verified nor a guarantee. |
| calculated data | Deterministic adjacency, feasibility, constraint checks, scores, and diagnostics derived from current inputs. |
| recommended data | Ranked/selected candidates, assignments, and conceptual tree topology produced by the heuristic. |

UI copy should use `CAP / JNET1 Gateway` until the terminology mapping is approved. Even after approval, provenance must retain the manufacturer product name and document revision.

## 4. Known facts, discrepancies, and unknowns

### 4.1 Manufacturer statements that may act as ceilings only

| Topic | Datasheet statement | Phase 6 treatment |
|---|---:|---|
| nodes per gateway | up to 1,000 nodes | Hard ceiling only after product mapping and the meaning of “node” are approved. Project design limit must be `<= 1,000 nodes/CAP`. |
| children per parent | maximum 16 nodes | Hard ceiling for the conceptual tree; project design limit must be `<= 16 children/parent`. |
| hop count | maximum 64 hops | Protocol ceiling only; approved project hop limit must be `<= 64 hops`. |
| claimed open-air coverage | up to 10 km | Marketing maximum with no antenna, height, reliability, propagation, or per-link/network-extent definition. Never a default or automatic bound. |
| claimed dense-urban coverage | up to 8 km | Same restriction; never a project design distance. |
| bands | 433.05-434.79 MHz and 902-928 MHz; page 4/ordering call the latter 915 MHz | Store exact variant/band family and jurisdictional approval source. Do not call 902-928 MHz universally legal. |
| raw rate | 100 kbps at 433 MHz; 500 kbps at 900/915 MHz | Informational manufacturer value, not application throughput. |
| aggregate goodput | 40 kbps at 433 MHz; 200 kbps at 915 MHz | Informational unless an approved message/load model exists. |
| hop delay | 60-300 ms/hop | Manufacturer range, not a latency guarantee or accepted design limit. |
| backhaul | indoor wired IPv4 over RJ45; outdoor cellular broadband | Variant capability, not proof that a candidate site has usable backhaul. |
| power/enclosure | indoor 5 VDC/0.5 A, 2.5 W, IP20; outdoor 100-240 VAC/50-60 Hz, 20 W, IP65 enclosure | Variant specification, not proof of site power, mounting, or environmental feasibility. |
| roaming | nodes may roam between gateways | Capability statement only; it does not define redundancy, overlap, failover time, or spare capacity. |

The page-1 phrase “other GWs cover only app. 200 nodes” is an unexplained comparison and must not set a design rule.

### 4.2 Verified source discrepancies and cautions

- Page 4 describes a typical 32-hop broadcast travel range as `300` to `9,600 ms` while also stating `60` to `300 ms/hop`. Multiplication yields `1,920` to `9,600 ms`; the lower bound is internally inconsistent. Latency enforcement is blocked pending manufacturer clarification.
- Page 4's broadcast scan example uses 3,000 responding nodes, while the same datasheet states 1,000 nodes per gateway. The example may describe multiple subtrees but does not say so. It must not define per-gateway load.
- The radio family is variously labelled `900 MHz`, `915 MHz`, and `902-928 MHz`. The project should store `915` as the ordering family plus the exact stated range; it must not collapse these into an unsupported regulatory conclusion.
- The standards table varies by indoor/outdoor model and market, and the datasheet says additional local standards apply. Listing a standard is not evidence that the ordered unit/project is compliant.
- The parent-adoption algorithm/criteria are proprietary. The Phase 6 tree is an explainable planning approximation, not protocol simulation.

### 4.3 Blocking unknowns

The supplied evidence does not establish:

- that project CAP definitively means this JNET1 Gateway/Group Controller;
- which LITE/WIFI/SMART fixtures are JNET1 nodes or can host a gateway;
- whether the 1,000-node maximum counts only managed nodes or includes the gateway;
- a recommended per-link design distance or its conditions/margin;
- a conservative node load, child, hop, goodput, or latency design target;
- exact regional band legality, ordered variant, antenna, mounting height, LOS/NLOS rule, obstruction, terrain, propagation, or interference inputs;
- candidate-site power, backhaul, enclosure, mounting, access, security, ownership, clearance, permitting, or survey feasibility;
- redundancy, overlap, failover, spare-capacity, or single-CAP acceptance policy;
- whether separate non-pole equipment sites are allowed;
- whether the engine may recommend from an approved pool or only validate a fully user-authored design.

Every dependent operation must remain blocked until the corresponding project input is approved. Unknowns may be displayed and saved; they may not be silently defaulted.

## 5. Recommended safe MVP

The recommended MVP is a two-mode planning tool:

1. **Validate mode** validates explicit selected CAPs, primary assignments, parent locks, and exclusions. It is the lowest-risk mode and should always be available once the required inputs are complete.
2. **Recommend-from-approved-pool mode** ranks and selects only from explicit feasible candidates. It never invents a coordinate. The output is a deterministic heuristic recommendation, not an optimum and not an installation design.

The graph uses projected straight-line distance only. Phase 6 must say: “Conceptual graph-and-constraint planning only. Links are distance-qualified, not RF-predicted. Results do not establish coverage, throughput, latency, availability, service quality, legal compliance, or installation feasibility.”

Required runtime inputs before either mode may run (they are not prerequisites for implementing the approved unknown-state workflow):

- approved CAP-to-product mapping and exact product/variant record;
- required band family and jurisdiction/approval provenance;
- explicit node participation for each active fixture type present in the project;
- user-approved planning link distance in metres and its source/status;
- project node-per-CAP, children-per-parent, and hop limits, each with source/status and within applicable manufacturer maxima;
- explicit redundancy policy;
- at least one candidate site with explicit power, backhaul, enclosure, mounting, and prohibition/preference dispositions;
- explicit permission for the requested mode (`validate_only` or `recommend_from_approved_pool`).

Goodput/load and latency are not MVP constraints unless the user supplies an approved traffic model and manufacturer clarification. Their absence produces a persistent warning, not an invented limit. RF/terrain/obstruction/antenna/interference omissions always remain visible limitations.

## 6. Proposed data architecture

Approved additive versions:

- project schema `2.6.0` from `2.5.0`;
- software/API `0.6.0`;
- planning model `jnet1-graph-planning-1.0.0`;
- project CAP input contract `1.0.0`.

Do not change the seven frozen engineering catalogs or their schemas. Keep the current `recommended_layers` dictionary intact for lossless compatibility; use new strict first-class collections rather than placing untyped Phase 6 payloads into it.

| Collection/model | Ownership and required content |
|---|---|
| `Project.cap_planning_inputs` | User data: profile, candidate sites, node overrides/exclusions, selected-CAP locks, parent/reassignment locks, prohibited/preferred-site flags, revisions, approval provenance, and field-survey notes. |
| `CapPlanningProfile` | Product mapping, exact variant, band family/range, jurisdiction, operating mode, project design limits, explicit gateway/node-count convention, redundancy policy, missing-input disposition, and permanent disclaimer. |
| `CapConstraintValue` | `value`, explicit unit, classification (`legal_regulatory_requirement`, `manufacturer_hard_constraint`, `manufacturer_guidance`, `project_design_limit`, `user_approved_assumption`, `derived_value`, `unknown`), source/approver/date, applicability/revision, conflict state, and notes. Unknown or unresolved conflict is nullable and blocks its dependent check. |
| `CapCandidateSite` | Stable ID; kind `existing_pole` or `manual_non_pole`; pole reference or WGS84 coordinate; indoor/outdoor; mounting height if known; power/backhaul/enclosure/mounting/survey status; preferred/prohibited; user notes; revision/timestamps. |
| `CapNodePolicy` | LITE/WIFI/SMART disposition `node`, `non_node`, or `unknown`; optional per-pole explicit exclusion; no inference from fixture Wi-Fi/camera capability. |
| `CapManualConstraints` | Locked selected candidates, excluded candidates/nodes, locked primary CAP assignment, and optional locked parent. Every reference uses a stable ID and is atomically validated. |
| `Project.cap_calculations` | Calculated data only: canonical node/candidate snapshots, graph summary, adjacency diagnostics, candidate feasibility/ranking facts, constraint violations, warnings, fingerprint, limits, model/version, and provenance. |
| `Project.cap_recommendations` | Recommended data only: selected candidates, primary assignments, parent/child topology, hop/distance/capacity diagnostics, redundancy validations, unresolved nodes, objective trace, fingerprint, status, warnings, and disclaimer. |

Manual non-pole sites are user data, never source data. Their WGS84 coordinates are display/interchange values; their transformed projected coordinates are calculated snapshots. Existing-pole sites reference the immutable source pole ID and use its effective coordinate only if an explicit authorized location edit exists. Neither site kind may alter a source pole.

All records are strict, finite, JSON-safe Pydantic models. IDs must be stable and independent of display names. Unknown fields remain rejected except for explicitly named legacy-metadata containers used only by migration.

## 7. Constraint semantics

### 7.1 Maxima, design limits, and margins

The UI and persisted model must keep these categories visibly separate:

| Constraint | Manufacturer ceiling | Required project input | Enforcement |
|---|---:|---:|---|
| managed nodes per CAP | 1,000 nodes | integer `1..1000 nodes/CAP` | Hard reject above 1,000; validate assignments against project limit. |
| children per parent | 16 nodes | integer `1..16 children/parent` | Hard reject above 16; validate every gateway/node parent. |
| hop count | 64 hops | integer `1..64 hops` | Hard reject above 64; validate every assigned path. |
| link distance | none suitable | positive finite metres with approved source/assumption | No default. Do not derive from 8/10 km claims. |
| load/goodput | 40/200 kbps aggregate stated | absent unless an approved traffic model exists | Warning and out of optimization scope by default. |
| latency | 60-300 ms/hop stated, inconsistent example | absent pending clarification or approved engineering rule | Informational diagnostic only; no guarantee. |

If the user approves a planning margin, store it explicitly rather than hiding it in the range. Recommended representation is `approved_link_distance_m` plus an optional descriptive `margin_basis`; the engine uses the approved distance exactly.

Every project design value must be checked against applicable law/AHJ/regulatory bounds and exact-product manufacturer hard constraints before it is accepted. A stricter project value is permitted; a more permissive one is 422. An unresolved applicability or source conflict is not a warning-only state: it blocks the dependent operation.

### 7.2 Gateway and co-located fixture node accounting

The datasheet says “nodes per gateway” but does not state whether the gateway appliance is included in the 1,000-node count. The project profile therefore needs a required, provenance-bearing `gateway_node_count_convention` object with two independently explicit fields:

- `gateway_appliance_counting`: `excluded`, `included`, or `unknown`;
- `colocated_fixture_counting`: `distinct_managed_node_once`, `merged_not_separate`, or `unknown`.

Each field carries classification/source/approver/date/notes. Either `unknown` blocks dependent capacity/topology validation. If the appliance is `included`, it consumes one unit of the applicable nodes/CAP limit; a distinct co-located fixture consumes one additional unit. The engine must never count any fixture record more than once.

Recommended planning convention pending manufacturer confirmation:

- the gateway appliance itself is excluded from the managed-node count because the document describes nodes *per gateway*;
- when an existing-pole candidate is selected as a CAP, a fixture on that same pole remains a distinct managed network node if its approved fixture-type/per-pole policy says `node`;
- that co-located fixture is counted exactly once against the selected CAP's project/manufacturer node limit;
- it is assigned to the co-located gateway at exactly `0.000000 m`, at primary hop `1`, with the gateway represented by a distinct root vertex ID rather than the fixture node ID;
- the co-located fixture cannot be its own parent, cannot parent the gateway root, and participates in ordinary child/cycle validation if it parents other fixture nodes;
- a manual non-pole gateway has no implicit fixture node and contributes only a gateway root, not a managed node.

This is a project planning convention, not a verified manufacturer fact. If the runtime convention is `unknown`, or if the user selects an alternative without required provenance, capacity/topology validation and recommendation are blocked. A future authoritative manufacturer clarification supersedes the assumption subject to visible conflict review and migration/revalidation; it is never silently applied to stored results.

### 7.3 Band and legal applicability

Band is a required project input even though the MVP distance graph does not model RF. Allowed datasheet families are `433` (433.05-434.79 MHz) and `915` (902-928 MHz). The record must include exact ordered variant, country/jurisdiction, approval authority/source, and status. `unknown` blocks planning. The UI must state that product availability and legal operation require separate verification.

### 7.4 Candidate feasibility

A candidate is feasible only when all approved required dispositions pass:

- not prohibited;
- mounting feasibility `confirmed`;
- power availability `confirmed` for the selected indoor/outdoor variant;
- backhaul availability `confirmed` and compatible with the variant;
- enclosure/environment disposition `confirmed`;
- field-survey status satisfies the approved project policy.

`unknown` is not equivalent to false. Recommended default is to exclude an unknown candidate from recommendation and show a blocking reason; Validate mode may retain it only as an explicit invalid candidate, never as passing.

### 7.5 Redundancy

The policy is required and one of:

- `single_allowed_with_warning`: one CAP may be recommended, with a persistent single-point-of-failure warning;
- `n_plus_one_validation`: every served node must remain assignable after removal of any one selected CAP, by deterministic full revalidation under the same node/children/hop/distance limits;
- `user_supplied_only`: the engine reports reachability/overlap but makes no redundancy acceptance statement.

Roaming is not proof of failover. N+1 validation is a graph/capacity stress test only; it does not guarantee roaming behavior, backhaul diversity, power independence, transition time, or RF availability. Physical utility/path diversity remains a field input and warning.

## 8. Deterministic graph and recommendation algorithms

### 8.1 Canonical graph construction

1. Resolve effective existing-pole coordinates without changing source data; transform all participating nodes and candidates into the validated projected CRS in metres. Represent each selected gateway appliance as a distinct root vertex `cap-root/<candidate_id>` even when it is co-located with a fixture node.
2. Sort nodes by `(source.sequence_index, pole_id)`. Sort candidates by `(user_priority ascending, kind existing_pole before manual_non_pole, candidate_id)`; lower user-priority number is preferred.
3. Build an undirected conceptual adjacency graph using a spatial index. Add an edge only when Euclidean projected distance is finite and `distance_m <= approved_link_distance_m + 1e-9 m`.
4. Candidate-to-node edges and node-to-node edges are permitted. Candidate-to-candidate edges do not serve nodes and are excluded in MVP. Under the approved recommended counting convention, an existing-pole candidate and its distinct fixture node receive a canonical zero-distance root-to-node edge; the fixture counts once, at hop 1, and the gateway appliance does not count as a managed node. A manual non-pole root creates no implicit node.
5. Persist link distances rounded to 6 decimal places; comparisons use unrounded values. Exact-boundary links pass. Never compute distance in WGS84 degrees.
6. Stable link ID is `cap-link/<min-endpoint-id>/<max-endpoint-id>`. Order links lexicographically by endpoint IDs. Root and fixture IDs must remain different, self-links are forbidden, roots cannot have parents, and cycle validation operates over the directed topology before persistence.

This graph is a distance graph, not an RF connectivity graph. Obstruction, terrain, antenna, propagation, and interference are not modeled.

### 8.2 Candidate feasibility and ranking

For every feasible candidate, compute a deterministic capacity-constrained breadth-first tree using the project design limits. Parent expansion order is `(hop, projected_distance_m, parent_id)` and child consideration order is `(projected_distance_m, node_sequence_index, node_id)`. Locked parent/assignment constraints are applied first and a contradiction is a 422 error.

Rank candidates by this objective tuple, ascending unless stated:

1. locked-selected first;
2. larger count of currently unassigned serviceable nodes (descending);
3. fewer unresolved mandatory constraints;
4. lower maximum hop;
5. lower total tree-edge length in metres;
6. lower sum of node hops;
7. explicit user priority;
8. existing-pole before manual non-pole only as a final policy tie-break;
9. stable candidate ID.

Every score component and exclusion reason must be returned. No random seed, wall-clock time, insertion-order dependence, or floating tie ambiguity is allowed.

### 8.3 Recommend-from-approved-pool heuristic

1. Validate all inputs and apply selected-CAP locks/exclusions.
2. Start with locked selected CAPs, sorted canonically.
3. Rebuild the global constrained forest. Assign locked nodes/parents first.
4. While eligible nodes remain unresolved, rank unselected feasible candidates by marginal serviceable nodes using section 8.2. Select the best positive-gain candidate.
5. Rebuild the complete forest after each selection so earlier greedy local assignments do not become hidden state.
6. Stop when all eligible nodes are assigned, the approved CAP-count safety limit is reached, or no positive-gain candidate remains.
7. Perform a deterministic reassignment improvement pass in node order: choose the feasible CAP/path tuple `(locked first, hop, path total metres, CAP user priority, CAP ID, parent ID)` while respecting all capacity/children/hop limits. Cap the pass count and stop at the first unchanged pass.
8. Run the approved redundancy validation. Report unresolved nodes and every failed constraint.

The heuristic must be labelled non-optimal. It may recommend only candidate IDs from the user-approved pool. It must never generate or shift a coordinate.

### 8.4 Validate mode

Validate mode uses user-selected CAPs and locked/manual assignments without adding a candidate. It constructs the same deterministic forest, checks every constraint, and reports errors/warnings. A validation result may be `invalid`; it must never silently repair a user lock. An unlocked node may be assigned deterministically only if the user has enabled `auto_assign_unlocked_nodes`; otherwise it remains unresolved.

### 8.5 Manual edits and revalidation

- CAP lock: force a candidate selected; failure to make it feasible is an error, not an override of site facts.
- candidate exclusion: candidate cannot be selected or used as an alternate.
- node exclusion: node is retained in user data but absent from topology, with reason/provenance.
- primary reassignment lock: fixes the selected CAP for a node; invalid/unreachable/capacity-conflicting locks return 422 atomically.
- parent lock: fixes the immediate parent; cycles, self-parenting, missing edges, excess children, or excess hops return 422 atomically.
- any accepted edit clears stale calculated/recommended outputs unless their exact fingerprint still matches; undo/redo must revalidate before exposing a restored result.

## 9. Safety and performance caps

Recommended application safety caps, not product design values:

| Item | Cap | Failure behavior |
|---|---:|---|
| participating nodes | 2,000 | 422 before graph construction |
| candidate sites total | 500 | 422 before graph construction |
| selected CAPs | 64 | 422; never truncate |
| graph vertices | 2,500 | 422 |
| spatial-index candidate distance evaluations | 250,000 | 422 |
| accepted undirected graph edges | 250,000 | 422 |
| persisted primary topology links | 2,000 | 422 |
| deterministic improvement passes | 8 | End with warning if still changing; never claim optimum |
| N+1 CAP-removal scenarios | 64 | 422 if the selected-CAP cap is exceeded |
| serialized CAP planning payload | 25 MiB | 422 before persistence |
| user text fields | 2,000 characters each | model validation 422 |

Use a spatial index; do not materialize an unbounded all-pairs matrix. Count every candidate evaluation consistently and include the counts/limits in provenance. Exceeding a cap must identify the exact cap, return no partial result, and preserve the previously stored project byte-for-byte. The 74-pole production workflow must remain far below these caps.

## 10. Fingerprint, provenance, and stale-result lifecycle

Use canonical JSON with sorted keys, compact separators, `allow_nan=false`, and SHA-256. The calculation and recommendation must share an input fingerprint containing:

- model/contract versions and every safety limit that can change output;
- projected/source CRS;
- product mapping, variant, band, jurisdiction, gateway/node-count convention, every design constraint and its status/source/applicability/conflict state;
- node-type policy and every participating source pole's ID, sequence, exact source/effective coordinate, type, active state, and relevant explicit exclusion;
- every candidate's stable ID, type/reference/coordinate, site-feasibility fields, preference/prohibition, priority, revision, and selected/excluded locks;
- every assignment/parent lock and redundancy/operating-mode setting;
- deterministic tolerance, ordering, ranking, and algorithm identifiers.

Exclude purely presentational layer visibility. Include names only when copied into results. Notes and survey text that do not affect feasibility may be excluded, but the result must display them live from user data rather than copy stale text into provenance.

Invalidate both `cap_calculations` and `cap_recommendations` on any significant change. Revalidate on frontend mutations, undo/redo, backend PUT, open, GET, candidate/manual-control endpoints, and before calculate/recommend/validate. A stale result must be removed or marked unavailable, never displayed as current. Layer toggles alone do not invalidate.

Every result must record source file/document revision, frozen constraint catalog version/hash, project input approvals, exact design limits/units, algorithm/model version, projected CRS, calculated timestamp, fingerprint, operation counts, assumption/warning/error lists, and disclaimer.

Warning/error semantics:

- **error/blocking**: required input unknown; illegal model value; infeasible locked constraint; unreachable required node; hard/project limit exceeded; corrupt/missing reference; failed required redundancy; missing projected-metre CRS.
- **warning/non-blocking only when policy allows**: single-CAP single point of failure; no approved traffic/latency model; field survey incomplete under a warning-allowed policy; manual non-pole site; manufacturer ambiguity; graph-only/RF exclusions.
- **info**: excluded nodes/sites, exact tie-break rationale, unused feasible candidates.

## 11. API and atomic-preservation contract

Recommended endpoints, following the existing complete-project response pattern:

| Method/path | Purpose |
|---|---|
| `PUT /api/projects/{project_id}` | Save strict Phase 6 user inputs, invalidate stale CAP outputs, and return the complete project. |
| `POST /api/projects/open` | Losslessly migrate/validate, verify embedded source, invalidate stale CAP output, and save atomically. |
| `PUT /api/projects/{project_id}/cap-planning/profile` | Replace the complete project CAP profile with revision precondition. |
| `POST /api/projects/{project_id}/cap-planning/candidates` | Add an explicit existing-pole or manual non-pole candidate. |
| `PUT /api/projects/{project_id}/cap-planning/candidates/{candidate_id}` | Validate replacement before mutation. |
| `DELETE /api/projects/{project_id}/cap-planning/candidates/{candidate_id}` | Delete user candidate only; never delete a source pole. |
| `PUT /api/projects/{project_id}/cap-planning/manual-constraints` | Atomically replace locks/exclusions/reassignments after full reference/cycle validation. |
| `POST /api/projects/{project_id}/cap-planning/calculate` | Build calculated graph/rank diagnostics without selecting new CAPs. |
| `POST /api/projects/{project_id}/cap-planning/validate` | Validate the explicit user design. |
| `POST /api/projects/{project_id}/cap-planning/recommend` | Run the approved bounded heuristic from the approved pool. |

HTTP semantics:

- `404`: project, pole, candidate, or referenced node ID does not exist;
- `409`: path/body ID mismatch, stale input revision/optimistic concurrency conflict, or operation mode conflicts with the approved profile;
- `422`: invalid engineering input, unresolved blocker, constraint contradiction, invalid CRS/coordinate/topology, hard/safety limit breach, or corrupt stored payload.

Every mutation must validate a deep copy, calculate on the copy, and call the atomic store only after complete success. A 404/409/422 response must leave the saved project bytes, immutable source archive, prior valid user inputs, and prior current result unchanged. No endpoint may edit source bytes or source poles.

## 12. UI, layers, and workflow

Use a clearly labelled `Phase 6 - CAP / JNET1 graph planning` panel with this order:

1. resolve product mapping, variant/band/jurisdiction, and display source facts/discrepancies;
2. map LITE/WIFI/SMART node participation explicitly;
3. enter project design limits with manufacturer ceilings shown in a separate column;
4. choose redundancy and mode;
5. create/import explicit candidates, complete power/backhaul/enclosure/mounting/survey dispositions, and mark preferred/prohibited;
6. run preflight; blockers are actionable and no recommendation button is enabled until complete;
7. calculate/rank, validate, or recommend;
8. inspect candidate score trace, assignments, parent tree, hops, distance, capacity, violations, redundancy scenarios, and permanent disclaimer;
9. lock/exclude/reassign, revalidate, undo/redo, save, and reopen.

Map layers:

- retain existing `cap_locations` and `cap_connections` keys but rename visible labels to avoid claiming every candidate is recommended;
- add separate candidate-site, selected-CAP, primary-tree, alternate/redundancy diagnostic, and CAP-warning sources if needed;
- use CAP green for CAP locations/connections (current seams `#34d399` and `#10b981`), while prohibited/error sites use an accessible non-fixture warning treatment;
- preserve LITE red `#ef4444`, WIFI yellow `#facc15`, and SMART blue `#3b82f6` exactly;
- keep camera, lighting, Wi-Fi, CAP, and warning layers independent;
- a manual non-pole site must have a distinct gateway/site symbol and must never render as a pole fixture.

Candidate popups show kind, coordinate provenance, site feasibility, band/variant, selection/lock status, score components, and disclaimer. Connection popups show parent/child IDs, projected distance in metres, hop, and the text `distance-qualified conceptual link; not RF-predicted`.

Undo/redo must cover CAP profile changes, candidates, feasibility, locks, exclusions, and reassignments. Restoring a user state must not resurrect a mismatched result. Save/reopen must preserve exact user data and only current fingerprint-matched outputs.

## 13. Migration and export boundaries

Migration target is additive project schema `2.6.0` and software/API `0.6.0` after explicit approval.

- Accept `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, `2.3.0`, `2.4.0`, and `2.5.0` through the existing chain.
- Add empty `cap_planning_inputs`, `cap_calculations`, and `cap_recommendations`; keep CAP layers false.
- Do not infer product mapping, nodes, candidates, band, constraints, topology, or recommendations.
- Preserve source Base64 bytes, source records/raw coordinate text/coordinates/IDs, edits, catalogs/revision pins, camera data, lighting data, Wi-Fi data, `calculated_layers`, and `recommended_layers` losslessly.
- Preserve unknown legacy `recommended_layers` content exactly.
- Migration must be idempotent: migrating a canonical `2.6.0` payload is a semantic no-op and must not revise timestamps.
- Unsupported versions and corrupt CAP records return 422 and do not overwrite a saved project.

Portable project JSON is the only Phase 6 export. Existing updated KML remains limited to its accepted pole/fixture-edit contract and must contain no CAP candidates, manual sites, graph links, or recommendations. Explicit CAP schedules/layers and all PDF/XLSX reporting remain Phase 7.

## 14. Implementation architecture and ordered work packages

Likely authorized implementation files are bounded to:

- backend: `backend/app/models.py`, `backend/app/main.py`, `backend/app/services/store.py` only if atomic behavior requires a focused correction, new `backend/app/services/cap_planning.py`, and focused configuration/recalculation hooks;
- backend tests: new `backend/tests/test_phase6_cap_planning.py` plus focused model/API/migration regressions;
- frontend: `frontend/app/lib/types.ts`, `api.ts`, new `phase6-cap-workflows.mjs`, `EngineeringWorkspace.tsx`, `EngineeringMap.tsx`, `PoleInspector.tsx` only if node controls are placed there, and `globals.css`;
- generated contracts: `schemas/project.schema.json`, `schemas/openapi.json`;
- version metadata: `backend/pyproject.toml`, `frontend/package.json`;
- governance/handoff documentation explicitly authorized by the later implementation task.

Ordered work packages:

1. verify implementation authorization and record all section 16 approvals;
2. add strict models/constants/migration with no inferred data;
3. implement pure projected graph, fingerprints, validation, bounded ranking/selection, locks, and redundancy checks;
4. add atomic API endpoints and stale-result hooks;
5. regenerate and freshness-check project schema/OpenAPI;
6. add typed frontend transport and pure workflow helpers;
7. add preflight/profile/candidate/manual-edit/result UI and independent map layers;
8. add exhaustive backend/frontend/migration/API tests;
9. run full regression and genuine production-rendered 74-pole QA;
10. write an implementation completion report and commit only authorized Phase 6 files;
11. request independent QA; do not mark Phase 6 closed from the implementation task.

## 15. Executable acceptance matrix

| ID | Type | Objective pass/fail condition |
|---|---|---|
| P6-DM-01 | model | Strict models reject unknown fields/non-finite values; user, calculated, and recommended collections remain distinct; source/recommended placeholder data are unchanged. |
| P6-DM-02 | model | Unknown CAP identity, node policy, band, range, limits, gateway/node-count convention, redundancy, or candidate feasibility is valid storable runtime state but blocks only the dependent operation with the exact field ID. |
| P6-DM-03 | model | Manufacturer maxima and project design limits are stored/displayed separately with explicit units/status/source; project node/child/hop values above 1,000/16/64 are rejected. |
| P6-DM-04 | precedence | Applicable legal/AHJ/regulatory requirements and exact-product manufacturer hard constraints bound all project values; a stricter user limit passes, a more permissive user value fails 422, and an unresolved applicability/conflict blocks without choosing a permissive source. |
| P6-CT-01 | counting/topology | Synthetic existing-pole CAP with a node-eligible co-located fixture creates distinct root/fixture IDs, counts the fixture exactly once, assigns it at `0.000000 m` and hop 1, excludes the appliance under the recommended convention, and rejects self-parent/root-parent/cycles; switching only appliance counting to `included` consumes exactly one additional nodes/CAP unit and exercises the exact capacity boundary. `merged_not_separate` omits the fixture node only when explicitly selected with provenance. A manual non-pole CAP creates no implicit node. Either convention field `unknown` is storable but blocks calculate/validate/recommend. |
| P6-GR-01 | geometry | Exact-distance synthetic edge passes at `limit + 1e-9 m`; an edge above tolerance fails; WGS84 degree distance is never used. |
| P6-GR-02 | geometry | Existing-pole candidate uses unchanged effective/source provenance; manual non-pole site remains separate and creates no source pole/edit. |
| P6-GR-03 | graph | Disconnected node, chain, star, branching-limit, exact-hop-boundary, and cycle-lock cases yield deterministic expected topology/errors. |
| P6-AL-01 | algorithm | Repeated runs and shuffled input order produce byte-identical canonical selected IDs, assignments, links, scores, and fingerprint apart from timestamps. |
| P6-AL-02 | algorithm | Candidate ties exercise every documented tie-break in order; no random/insertion-order result occurs. |
| P6-AL-03 | algorithm | Greedy selection only chooses approved candidates, honors locked CAPs/exclusions, never creates a coordinate, and labels output non-optimal. |
| P6-AL-04 | algorithm | Child limit, node-per-CAP limit, hop limit, and link distance are simultaneously enforced after every rebuild and improvement pass. |
| P6-MN-01 | manual | Valid CAP locks, exclusions, reassignment, and parent locks persist/revalidate; missing references, self-parent, cycle, unreachable parent, over-capacity, and contradictory locks return 404/422 atomically. |
| P6-RD-01 | redundancy | `single_allowed_with_warning` permits one CAP only with exact single-point-of-failure warning; no failover claim appears. |
| P6-RD-02 | redundancy | N+1 synthetic case passes only if every single selected-CAP removal can reassign all required nodes under the same constraints; a capacity-stranded case fails. |
| P6-RD-03 | redundancy | `user_supplied_only` reports diagnostics without presenting a redundancy pass or recommendation. |
| P6-SF-01 | safety | Each 2,000-node, 500-candidate, 64-selected-CAP, 2,500-vertex, 250,000-evaluation, 250,000-edge, 2,000-link, 8-pass, 64-scenario, 25-MiB, and text cap has boundary-pass and boundary+1 atomic-fail tests. |
| P6-SF-02 | safety | Missing/invalid/non-metre CRS, invalid coordinate, NaN/Infinity, invalid range, and spatial/topology errors return controlled 422 with no partial stored mutation. |
| P6-FP-01 | fingerprint | Every listed significant input invalidates both calculated/recommended output; notes/layer visibility do not; GET/save/open/undo/redo cannot expose stale output. |
| P6-PR-01 | provenance | Result includes exact catalog hash/version, datasheet revision, constraints/units/status/source, CRS, algorithm/limits/operation counts, fingerprint, warnings, and exact disclaimer. |
| P6-AP-01 | API | Successful endpoints return the complete strict project; missing IDs are 404, revision/mode/path conflicts 409, invalid engineering data 422. |
| P6-AP-02 | API | Every failed candidate/profile/manual/calculate/validate/recommend operation preserves exact prior `project.json`, source archive bytes, and prior current result. |
| P6-MG-01 | migration | Every supported version migrates to 2.6.0 without inferred CAP data and with exact source Base64/raw coordinates/coordinates/IDs and Phase 1-5 collections. Second migration is a no-op. |
| P6-EX-01 | export | Portable JSON saves/reopens CAP user/calculated/recommended data; updated KML contains 74 original placemarks and no CAP/manual-site/link geometry. |
| P6-UI-01 | rendered | Required inputs and blockers are visible; Recommend is disabled until preflight passes; maxima/design limits/assumptions are visibly distinct. |
| P6-UI-02 | rendered | Candidate CRUD, preference/prohibition, locks/exclusions/reassignment, undo/redo, revalidation, save/reopen, and stale invalidation work through genuine UI controls. |
| P6-UI-03 | rendered | CAP green layers are independent and accessible; manual sites are not pole symbols; LITE/WIFI/SMART remain exact red/yellow/blue. |
| P6-UI-04 | rendered | Every result/link shows graph-only disclaimer and no RF, throughput, latency, availability, legal, professional, or standards-compliance claim. |
| P6-REG-01 | regression | Full existing backend, engineering validator, rendered suite, TypeScript, ESLint, production build, generated-contract freshness, and browser-console checks pass. |
| P6-PRD-01 | production workflow | Genuine production UI imports the supplied 74-pole KML, first proves unknown runtime inputs persist and block operations, then configures conspicuously labelled test-only node/candidate/counting inputs, runs validate and recommend, edits/locks/revalidates, undo/redoes, saves/reopens, and preserves exact source SHA/coordinates with zero console errors. |

The production workflow must record exact inputs and outputs; it may use clearly labelled test-only planning assumptions but cannot claim those assumptions are approved for the real site.

## 16. Approved implementation-policy decisions

The user explicitly approved every recommended implementation-policy decision below on 2026-08-27. These decisions define what the software may support, which fields and states it must model, how it behaves, and how it is accepted. They are binding for the future Terra task, but they do not authorize implementation.

They do **not** require the user to supply or approve actual Miracle Mile operational values before implementation. Unless the user separately records a real-site value as locked project input, product/variant mapping, fixture node dispositions, band/jurisdiction, link distance, node/child/hop limits, gateway/node counting convention, candidate inventory/feasibility, and redundancy selection may remain `unknown` during implementation. Unknown values must round-trip losslessly with provenance fields available and must block only the dependent runtime calculate/validate/recommend operation.

### Decision 1 - Product identity and terminology

**Recommended:** Approve support for the supplied Juganu `JNET1 Gateway (Group Controller)`, model family `JGW-JNET1`, as the provisional initial product record, while displaying `CAP / JNET1 Gateway` and retaining Rev 1.2 provenance. Require a runtime product-mapping field that may remain `unknown`; do not hardcode that Miracle Mile CAP definitively uses this product.

**Alternatives:** Treat CAP as a different/abstract gateway and supply its authoritative specification; or defer Phase 6.

**Tradeoff:** Approval gives the model a concrete product ceiling set, but it does not confirm hardware revision or project suitability.

**If implementation policy is unresolved:** Stop before implementing product-specific constraints. **If only the runtime Miracle Mile mapping is unresolved:** store `unknown` and block CAP calculate/validate/recommend at preflight.

### Decision 2 - Network-node membership

**Recommended:** Approve the `node/non_node/unknown` field contract for LITE, WIFI, and SMART; block runtime operations only when an active fixture type present in that project remains unknown. Do not infer node status from Wi-Fi or camera capability. Do not lock the Miracle Mile type values during implementation unless separately directed.

**Alternatives:** Approve a fixed type matrix now; or require per-pole node flags only.

**Tradeoff:** Type policy is efficient but depends on BOM truth; per-pole flags are precise but burdensome.

**If implementation policy is unresolved:** Stop before implementing node membership. **If only runtime values are unresolved:** preserve `unknown`; no runtime node graph can be built.

### Decision 3 - Candidate-site scope and hosting

**Recommended:** Approve both explicit existing-pole candidates and user-placed manual non-pole equipment sites as allowed schema/workflow kinds. At runtime, hosting passes only with confirmed mounting, power, backhaul, enclosure, and non-prohibited status. Manual sites remain separate user data and never become poles; implementation does not require a real Miracle Mile candidate inventory.

**Alternatives:** Existing customer poles only; or manual non-pole sites only.

**Tradeoff:** Mixed sites reflect indoor/wall/pole forms but add coordinate/site-data UI. Existing-pole-only is simpler and may exclude feasible backhaul locations.

**If implementation policy is unresolved:** Stop before implementing candidate-site workflows. **If only runtime candidate facts are unresolved:** persist the incomplete inventory and block/exclude candidates according to preflight.

### Decision 4 - Engine authority

**Recommended:** Support Validate mode plus an explicit `recommend_from_approved_pool` mode. The engine may rank/select only approved candidate IDs and never generate coordinates.

**Alternatives:** Validation/ranking only with no selection; or user-selected CAPs only.

**Tradeoff:** Bounded selection is useful and explainable but heuristic/non-optimal. Validation-only carries less recommendation risk.

**If unresolved:** Implement no recommendation endpoint; at most model scaffolding could proceed under a separately narrowed authorization.

### Decision 5 - Required band and jurisdiction input

**Recommended:** Approve required runtime fields for exact `433` or `915` family, ordered variant, jurisdiction, and approval source before an operational run; store 915 with its exact 902-928 MHz datasheet range. These fields may remain `unknown` during implementation.

**Alternatives:** Allow unknown band with warning because distance graph is band-agnostic.

**Tradeoff:** Required provenance prevents a misleading deployable-looking result; it does not itself establish legality.

**If implementation policy is unresolved:** Stop before implementing band preflight. **If only runtime values are unresolved:** block validate/recommend at preflight.

### Decision 6 - Project link distance

**Recommended:** Approve a nullable runtime field that requires a positive finite user-approved design link distance in metres with source/status before graph construction. Do not supply an implementation default from 10 km open-air or 8 km dense-urban claims and do not infer a hidden margin.

**Alternatives:** Provide a user-approved temporary planning assumption; or operate without distance edges, which makes topology impossible.

**Tradeoff:** An assumption enables conceptual work but carries high RF risk and must remain prominent/editable.

**If implementation policy is unresolved:** Stop before implementing distance semantics. **If only the runtime distance is unresolved:** store `unknown` and block graph construction.

### Decision 7 - Conservative capacity, child, and hop limits

**Recommended:** Approve nullable runtime fields and bound validation for project values `<= 1,000 nodes/CAP`, `<= 16 children/parent`, and `<= 64 hops`, each with source/approval. Do not supply automatic conservative defaults or require actual Miracle Mile values during implementation.

**Alternatives:** User approves temporary lower planning assumptions; or use manufacturer maxima directly as project limits with a strong warning.

**Tradeoff:** Maxima maximize apparent feasibility but provide no engineering margin. Lower assumptions are safer but need an owner.

**If implementation policy is unresolved:** Stop before implementing capacity/hop semantics. **If only runtime values are unresolved:** preserve `unknown` and block topology validation/recommendation.

### Decision 8 - Gateway appliance and co-located fixture counting

**Recommended:** Approve the required provenance-bearing runtime convention object with separate `gateway_appliance_counting` and `colocated_fixture_counting` fields and `unknown` support. Recommend `excluded` for the appliance because the datasheet says nodes per gateway, and `distinct_managed_node_once` for an approved node-eligible fixture on the same existing pole. The fixture is assigned to the distinct gateway root at `0.000000 m` and hop 1. Self-parenting/root-parenting/cycles are forbidden. A manual non-pole gateway creates no implicit fixture node. Label both selections as project planning assumptions pending manufacturer confirmation, not facts. Do not hardcode them for Miracle Mile unless separately approved as real-site input.

**Alternatives:** Count the gateway appliance within the 1,000 total; treat a co-located fixture as part of the appliance and not a separate node; or defer capacity/topology validation pending manufacturer confirmation.

**Tradeoff:** The recommended convention follows the document's “nodes per gateway” wording and preserves the fixture as a real managed endpoint, but the manufacturer has not confirmed the accounting. Counting the appliance is more conservative by one; merging the fixture risks undercounting a managed endpoint.

**If implementation policy is unresolved:** Stop before implementing node accounting/topology capacity. **If only the runtime convention is unresolved:** store `unknown` and block dependent capacity/topology calculate/validate/recommend operations.

### Decision 9 - Load, goodput, and latency

**Recommended:** Exclude them from MVP enforcement/optimization; display manufacturer values and persistent `not evaluated` warnings. Require a later approved traffic/message model and manufacturer clarification before operational use.

**Alternatives:** User supplies a complete approved message/load/latency model now; or derive latency from 300 ms/hop, which is not recommended.

**Tradeoff:** Exclusion keeps claims honest but cannot assess network performance.

**If unresolved:** Treat as out of scope, not silently passed.

### Decision 10 - RF/environmental model boundary

**Recommended:** Approve Phase 6 as projected-distance graph planning only. Antenna, mounting height, LOS/obstruction, terrain, propagation, and interference remain field inputs/warnings and are not simulated.

**Alternatives:** Defer Phase 6 until an RF model and required inputs are approved.

**Tradeoff:** Graph planning is useful for organization/constraint screening but cannot validate links.

**If unresolved:** Do not implement graph links or recommendations.

### Decision 11 - Site feasibility and field survey policy

**Recommended:** Approve runtime feasibility fields and preflight rules requiring confirmed power, backhaul, enclosure, mounting, prohibited/preferred disposition, and exact indoor/outdoor variant for a candidate to be recommended. Require field survey `confirmed` for a passing final validation; allow `pending` only in exploratory results with a warning. Actual Miracle Mile site records may remain absent/unknown during implementation.

**Alternatives:** Permit unknown site facts with warnings; or omit manual sites.

**Tradeoff:** Confirmation reduces uninstallable recommendations but requires field data.

**If implementation policy is unresolved:** Stop before implementing candidate-feasibility acceptance. **If only runtime site facts are unresolved:** candidates remain excluded and may leave no feasible result.

### Decision 12 - Redundancy and single-CAP policy

**Recommended:** Approve a required nullable runtime policy field with `single_allowed_with_warning`, `n_plus_one_validation`, or `user_supplied_only`; never infer a Miracle Mile selection. N+1 recomputes full constrained assignment after each single CAP removal and remains graph-only.

**Alternatives:** Require N+1 for every project; or permit one CAP without a warning, which is not recommended.

**Tradeoff:** Policy flexibility supports conceptual work while keeping single-point-of-failure truth visible. N+1 adds compute and still cannot guarantee real failover.

**If implementation policy is unresolved:** Stop before implementing redundancy acceptance. **If only the runtime selection is unresolved:** preflight blocks a redundancy/design verdict; do not infer a policy.

### Decision 13 - Deterministic algorithm and tie-breaks

**Recommended:** Approve sections 8.1-8.4: capacity-constrained BFS, greedy marginal candidate selection, bounded deterministic improvement, explicit objective tuple, and non-optimal label.

**Alternatives:** Validate-only; or adopt an approved optimization solver/objective in a later phase.

**Tradeoff:** The heuristic is dependency-light and explainable but does not prove minimum CAP count or globally optimal topology.

**If unresolved:** No selection algorithm may be implemented.

### Decision 14 - Manual locks, reassignment, exclusions, and atomic rejection

**Recommended:** Approve all four manual control types and reject contradictions atomically without auto-repair.

**Alternatives:** Omit parent locks or reassignment from MVP; allow the engine to override locks, which is not recommended.

**Tradeoff:** Controls improve engineer authority but increase validation/UI/tests.

**If unresolved:** Implement no ambiguous partial subset; narrow the scope explicitly first.

### Decision 15 - Data/version/migration target

**Recommended:** Project `2.6.0`, software/API `0.6.0`, model `jnet1-graph-planning-1.0.0`; add strict first-class user/calculated/recommended collections and retain the generic `recommended_layers` losslessly.

**Alternatives:** A different reviewed additive version/model shape.

**Tradeoff:** First-class strict models are auditable but require full migration/generated-contract review.

**If unresolved:** Stop before model/schema changes.

### Decision 16 - API, errors, undo/redo, and stale policy

**Recommended:** Approve sections 10-12, including complete-project responses, 404/409/422 semantics, atomic failure preservation, fingerprint invalidation, and no stale-result resurrection through undo/redo/open.

**Alternatives:** Fewer endpoints using only full-project PUT; or no optimistic revision conflicts.

**Tradeoff:** Focused endpoints are clearer and safer but expand OpenAPI/test surface.

**If unresolved:** Stop before API/frontend implementation.

### Decision 17 - Safety caps

**Recommended:** Approve all section 9 caps as application protections, visibly separate from product design constraints.

**Alternatives:** Supply reviewed different caps with performance evidence.

**Tradeoff:** Caps make failure deterministic and keep pathological inputs bounded; they limit unusually large projects.

**If unresolved:** Stop before graph/recommendation implementation.

### Decision 18 - UI terminology, colors, disclaimers, and warning/error semantics

**Recommended:** Approve sections 3, 10, and 12, including CAP green, exact fixture-color preservation, explicit graph-only language, and blocking-versus-warning rules.

**Alternatives:** Supply an approved product vocabulary/color system/disclaimer.

**Tradeoff:** Proposed wording minimizes overclaiming and matches existing UI seams.

**If unresolved:** Stop before rendered UI work.

### Decision 19 - Export and reporting boundary

**Recommended:** Persist Phase 6 only in portable JSON; keep updated KML free of CAP data; defer CAP schedules, KML layers, spreadsheets, PDFs, and presentations to Phase 7.

**Alternatives:** Separately authorize a specifically defined CAP export contract.

**Tradeoff:** JSON-only prevents conceptual recommendations being mistaken for customer/source or construction data.

**If unresolved:** Do not add exports.

### Decision 20 - Acceptance matrix and independent gate

**Recommended:** Make every row in section 15 mandatory and require a separate independent QA PASS before Phase 6 closure or Phase 7 planning.

**Alternatives:** Approve a documented narrowed matrix before implementation.

**Tradeoff:** The full matrix is substantial but directly tests safety, determinism, migration, source preservation, and rendered behavior.

**If unresolved:** The implementation cannot be accepted or Phase 6 closed.
