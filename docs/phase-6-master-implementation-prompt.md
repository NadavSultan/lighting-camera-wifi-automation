# Phase 6 master implementation prompt for GPT-5.6 Terra

> **NOT EXECUTABLE YET.** The user approved every implementation-policy decision in `docs/phase-6-cap-planning-and-implementation-contract.md`, section 16, on 2026-08-27, but has not separately authorized Phase 6 implementation. Planning authorization and approval of planning decisions are not implementation authorization. Do not use this prompt until that separate authorization is recorded; if governance later becomes unresolved, stop without editing implementation files.

Actual Miracle Mile operational inputs are not prerequisites to implement the approved model and workflow. Product/variant mapping, fixture node dispositions, band/jurisdiction, link distance, project node/child/hop limits, gateway/node-count convention, site inventory/feasibility, and redundancy selection may remain `unknown`. Implement those states without defaults; runtime preflight must block only the dependent calculate/validate/recommend operation. Test and rendered-QA inputs must be conspicuously labelled test-only and must never be recorded as real-project approval.

## Mission

Implement only the approved Phase 6 CAP / JNET1 Gateway graph-and-constraint planning MVP. Use existing customer poles without generating, moving, redistributing, optimizing, or deleting any lighting pole. Preserve all uploaded source bytes and Phases 1-5 behavior. Do not implement Phase 7 reporting or any verified RF/performance/compliance claim.

## 1. Mandatory startup and gate

Read completely, in this exact order:

1. `AGENTS.md`
2. `PROJECT_CONTEXT.md`
3. `docs/current-status.md`
4. `docs/implementation-plan.md`
5. `docs/architecture.md`
6. `docs/data-model.md`
7. `docs/phase-1-completion-report.md`
8. `docs/phase-5-master-gate-decision-2026-08-27.md`
9. `docs/phase-6-cap-planning-and-implementation-contract.md`
10. this prompt

Then inspect `git status --short --branch`, exact `git rev-parse HEAD`, and recent history. Start from the exact user-approved Phase 6 base commit. Preserve unrelated/user-owned changes. Read the decision-approval record supplied by the user.

Stop immediately without code changes if any of these is true:

- Phase 6 implementation was not separately and explicitly authorized;
- any required section 16 implementation-policy decision is missing, conditional, or different from the contract without a recorded replacement;
- the supported product/reference-product policy, allowed candidate-site kinds and operation modes, unknown/blocking field semantics, source precedence, counting schema, algorithm/tie-breaks, version target, safety caps, wording/export boundary, or acceptance matrix is not approved;
- the repository base differs from the approved base and the difference is not explicitly authorized;
- implementation would require editing an `Input/` file, a frozen engineering catalog/schema, or accepted Phase 1-5 behavior outside an approved compatibility correction.

Do **not** stop merely because real-site values are absent. Implement their explicit `unknown` state, provenance fields, UI blockers, persistence, migration, and runtime preflight. If the user separately directs that a real-site value be locked into the implementation contract, require an explicit project-input decision and record it separately from implementation-policy approval.

## 2. Read-only evidence before coding

Read:

- `docs/cap-datasheet-extraction.md`
- `docs/reference-input-inventory.md`
- `docs/engineering-open-questions.md`
- `docs/engineering-assumptions.md`
- `docs/engineering-data-completion-report.md`
- `docs/schema-contracts.md`
- `data/network/cap-constraints.json`
- `schemas/cap-constraints.schema.json`
- Phase 5 planning, implementation, rendered-QA, independent-review, focused-retest, and master-gate documents

Inspect the current models, migrations, atomic store, API response/error patterns, fingerprints/invalidation, frontend types/API/workflow helpers, CAP gates/layers/colors, `recommended_layers`, generated contracts, and relevant backend/frontend tests. Treat documents as claims to verify against code.

Do not edit `Input/CAP/CAP datasheet.pdf`. If reinspection is necessary, read the PDF skill first, render all relevant pages, and compare visual/text evidence. Do not use general web sources. Any new research must use primary manufacturer, regulator, or standards sources and must be cited.

## 3. Non-negotiable invariants

- `mode` remains `existing-poles`; `proposed_layout_authorized` remains false.
- Never create, move, optimize, redistribute, or delete a customer lighting pole.
- Preserve uploaded source files byte-for-byte, including embedded Base64, filename, size, and SHA-256.
- Preserve source pole IDs, order, raw coordinate text, WGS84 coordinates, metadata, and folder hierarchy exactly.
- `Input/` is read-only.
- WGS84 is display/interchange only. All distances and graph geometry use the validated projected CRS with metre axes.
- Manual non-pole sites, if approved, are separate user records and never source poles or pole edits.
- Do not infer product identity, fixture/node participation, candidate feasibility, band, range, margins, capacity targets, hop target, load, latency, redundancy, or compliance.
- Applicable law/regulator/AHJ/adopted-standard requirements have first precedence; exact-product authoritative manufacturer hard constraints bound all project values next. User-approved project limits/policies and assumptions may be stricter but can never override or enlarge those bounds. Preserve conflicts visibly and block when applicability/precedence is unresolved.
- Keep regulatory requirements, manufacturer hard constraints/guidance, project design limits, approved assumptions, derived values, conflicts, and unknowns visibly/status-separated with explicit units, applicability, revision, and provenance.
- The 10 km/8 km claims are not a design range. The 1,000-node, 16-child, and 64-hop values are ceilings, not defaults or targets.
- Gateway/node accounting is a required runtime convention object, not a manufacturer fact or implementation default. Model `gateway_appliance_counting` (`excluded/included/unknown`) separately from `colocated_fixture_counting` (`distinct_managed_node_once/merged_not_separate/unknown`), each with provenance. Under the recommended selectable convention, the appliance is excluded and a node-eligible co-located fixture is a distinct node counted once at `0.000000 m` and hop 1. Roots and fixtures have distinct IDs; self-parent/root-parent/cycles are forbidden; manual non-pole gateways create no implicit fixture node.
- Do not implement RF prediction, link budgets, terrain/obstruction/antenna/interference models, throughput/latency/availability guarantees, or standards/legal conclusions.
- Keep CAP user inputs, calculated graph facts, and recommended topology separate. Retain legacy/generic `recommended_layers` losslessly.
- Preserve fixture colors exactly: LITE `#ef4444`, WIFI `#facc15`, SMART `#3b82f6`. CAP uses its distinct approved green treatment.
- Existing updated KML export must contain no CAP candidate, manual-site, link, calculation, or recommendation geometry.
- A failed operation must not mutate stored project bytes, source archive, prior valid input, or prior current result.
- No stale result may be displayed after save/open/GET/undo/redo or a significant edit.
- Always display the approved exact graph-only disclaimer. Never use “coverage,” “optimal,” “compliant,” “guaranteed,” or similar language without the limiting qualifier defined by the approved contract.

## 4. Authorized file boundary

Unless the explicit implementation authorization narrows or expands this list, implementation may change only:

- `backend/app/models.py`
- `backend/app/main.py`
- new `backend/app/services/cap_planning.py`
- the smallest necessary invalidation/recalculation hook files under `backend/app/services/`
- `backend/app/services/store.py` only for a focused, tested atomic-preservation correction
- focused backend tests, including new `backend/tests/test_phase6_cap_planning.py`
- `frontend/app/lib/types.ts`
- `frontend/app/lib/api.ts`
- new `frontend/app/lib/phase6-cap-workflows.mjs`
- `frontend/app/components/EngineeringWorkspace.tsx`
- `frontend/app/components/EngineeringMap.tsx`
- `frontend/app/components/PoleInspector.tsx` only if approved node controls require it
- `frontend/app/globals.css`
- `frontend/tests/rendered-html.test.mjs`
- generated `schemas/project.schema.json` and `schemas/openapi.json`
- `backend/pyproject.toml` and `frontend/package.json` for approved `0.6.0` metadata
- Phase 6 decision, implementation-completion, and rendered-QA documents explicitly required by the implementation authorization

Do not edit the seven frozen catalogs/schemas, `Input/`, prior-phase reports, or runtime project data. Do not commit caches, build output, virtual environments, `node_modules`, ad-hoc uploads, or generated runtime exports.

## 5. Ordered work packages

### WP1 - Governance and exact contracts

Record the approved section 16 implementation-policy decisions without rewriting them as if they were always approved. Confirm the approved target versions, terminology, exact disclaimer, allowed modes/site kinds, field/unknown semantics, source precedence, counting schema, algorithm, caps, export boundary, and acceptance IDs. Do not require real Miracle Mile values to be populated. Add no behavior yet if an implementation-policy decision is missing.

### WP2 - Strict data model and lossless migration

Implement the approved additive schema/software/model versions, expected to be project `2.6.0`, software/API `0.6.0`, and `jnet1-graph-planning-1.0.0`.

Add strict models for:

- `CapConstraintValue` with value/unit/classification/source/approver/date/applicability/revision/conflict state/notes and the approved legal/manufacturer/project precedence categories;
- `CapPlanningProfile` with nullable product mapping, exact variant, band/range, jurisdiction, mode, design limits, gateway/node-count convention, redundancy, and disclaimer;
- `CapCandidateSite` with `existing_pole` or `manual_non_pole` identity and complete site-feasibility fields;
- explicit LITE/WIFI/SMART node policy and per-node exclusions;
- selected-CAP, candidate/node exclusion, primary assignment, and parent locks;
- separate `cap_planning_inputs`, `cap_calculations`, and `cap_recommendations`.

All operational fields identified as runtime inputs must support an explicit `unknown` state without an invented default. All IDs are stable; all numbers are finite; all units are explicit; strict models reject unknown fields. Keep a narrowly named legacy metadata field only where required for lossless migration.

Migration must accept every currently supported version through `2.5.0`, add empty CAP collections/layers only, and infer nothing. Preserve exact source bytes/Base64/raw coordinates/coordinates/IDs and every Phase 1-5 collection, plus unknown existing `recommended_layers` content. Migration must be idempotent and must not change timestamps on a canonical new-version payload.

### WP3 - Pure deterministic CAP planning service

Create `backend/app/services/cap_planning.py`. Keep it pure over a validated project and the read-only frozen CAP evidence.

Implement exactly the approved contract:

1. preflight required inputs and candidate feasibility;
2. canonical projected node/candidate snapshots;
3. spatial-index adjacency using the approved distance/tolerance;
4. stable edge IDs and canonical order;
5. distinct gateway-root and fixture-node identities, approved runtime node-count convention, zero-distance/hop-1 co-location semantics, no implicit manual-site node, and self-parent/root-parent/cycle prevention;
6. capacity-constrained BFS with approved parent/child ordering;
7. candidate ranking with every score component and tie-break;
8. Validate mode;
9. recommend-from-approved-pool greedy selection and bounded improvement;
10. manual locks/exclusions/reassignment/parent handling with cycle and contradiction detection;
11. approved redundancy scenarios, including full N+1 reassignment if selected;
12. exact safety/operation caps and controlled failures;
13. canonical SHA-256 fingerprints, provenance, warnings/errors, and disclaimer;
14. stale-result invalidation.

Use unrounded projected values for comparisons/calculations; persist distances at the approved precision. Never calculate distance in degrees. Never invent a coordinate, candidate, node type, site fact, band, range, margin, or network target. Label the heuristic non-optimal.

### WP4 - Atomic API

Add only the approved endpoints from contract section 11. Follow existing complete-project response style.

- 404: missing project/pole/candidate/node reference.
- 409: path/body mismatch, stale revision/optimistic conflict, or profile/operation-mode conflict.
- 422: invalid/unresolved engineering input, contradictory lock, invalid geometry/CRS, hard/design/safety limit, or corrupt stored project.

Validate and calculate on a deep copy. Save atomically only after complete success. Extend PUT/open/GET and relevant mutation paths so stale CAP output cannot survive. Do not weaken immutable-source checks.

### WP5 - Generated contracts

Regenerate `schemas/project.schema.json` and `schemas/openapi.json` from authoritative backend models. Review the diff. Add/retain in-memory freshness tests. Do not hand-edit generated contracts and do not modify frozen engineering schemas.

### WP6 - Typed frontend and workflow helpers

Update TypeScript transport/types without `any` shortcuts. Put deterministic preflight, draft, revision, fingerprint-significance, undo/redo, and display-format helpers in `phase6-cap-workflows.mjs` where practical. Helper tests must prove invalid drafts/contradictions preserve current user data/result.

### WP7 - Rendered UI and map

Implement the approved workflow in contract section 12:

- product/band/jurisdiction and maxima-versus-design-limit panel;
- explicit fixture-type node membership;
- candidate creation/edit/delete and complete site-feasibility controls;
- mode/redundancy controls and visible blockers;
- calculate/rank, validate, and recommend actions gated by preflight;
- score trace, selected CAPs, assignments/tree, hops/distances/capacities, unresolved nodes, redundancy diagnostics, provenance, and permanent disclaimer;
- locks, exclusions, reassignments, parent locks, undo/redo, save/reopen;
- independent candidate/selected/tree/redundancy/warning map layers.

Existing-pole candidates reference poles. Manual sites use a distinct non-pole gateway symbol. Preserve all prior layer controls and exact fixture colors. Use CAP green only as approved. Show `distance-qualified conceptual link; not RF-predicted` for every connection.

### WP8 - Tests

Implement every stable acceptance row `P6-DM-01` through `P6-PRD-01`. At minimum include:

- synthetic disconnected, chain, star, tie, exact-distance, boundary+epsilon, child-cap, node-cap, hop-cap, locked, cycle, capacity-stranded, and N+1 cases;
- input-order permutation/repeated-run determinism;
- every documented ranking tie-break;
- source-precedence cases proving legal/AHJ and exact-product manufacturer hard bounds cannot be overridden by user approval, including unresolved-conflict blocking;
- gateway/node-count cases proving both convention fields, the recommended convention, the one-unit appliance delta when `included`, explicit merged-fixture behavior, distinct co-located root/fixture identities, count-once, zero-distance/hop-1 assignment, manual-site no-implicit-node behavior, self-parent/root-parent/cycle rejection, exact capacity boundaries, and runtime `unknown` blocking required by `P6-CT-01`;
- unknown/NaN/Infinity/invalid CRS/invalid coordinate/invalid variant and missing-runtime-input cases;
- boundary and boundary+1 tests for every safety cap;
- 404/409/422 and exact stored-byte atomic-preservation probes;
- significant/non-significant fingerprint invalidation and undo/redo stale-result probes;
- all supported migration versions, source byte/coordinate preservation, legacy `recommended_layers`, and idempotence;
- updated KML exclusion and portable JSON save/reopen;
- Phase 1-5 regressions and exact fixture colors/disclaimers/gates;
- a genuine production-rendered supplied 74-pole workflow.

Do not use the real project's missing engineering values as hidden defaults. For tests/rendered QA, use explicit records labelled `test-only approved assumption` and state that they are not real-site approval.

## 6. Acceptance commands

Use the repository's configured Python/Node runtimes. From the repository root, run the equivalent of:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
Set-Location ..
.\.venv\Scripts\python.exe .\scripts\validate_engineering_data.py
Set-Location .\backend
..\.venv\Scripts\python.exe .\scripts\export_schema.py
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
Set-Location ..\frontend
pnpm run test
pnpm run typecheck
pnpm run lint
pnpm run build
Set-Location ..
git diff --check
git status --short
```

If the actual virtual environment path differs, use the repository-approved runtime and report the exact command. Do not install or update dependencies unless explicitly necessary and authorized.

Generated schema/OpenAPI freshness, frozen engineering-data/source hashes, and the full backend suite must pass after regeneration. Known non-failing advisories may be reported but not hidden.

## 7. Genuine production-rendered QA

Run a production Vinext build against the exact implementation worktree and an isolated FastAPI project store. Through visible UI controls:

1. import `Input/Miracle_Mile_Lighting_Poles.kml` and confirm 74 poles, five folders, expected CRS, and unchanged locked source coordinate;
2. confirm absent real-site operational values persist as explicit unknowns and calculate/validate/recommend are blocked by exact preflight messages without preventing project save/reopen;
3. enter explicitly labelled test-only CAP identity/node/band/design-limit/counting/redundancy inputs;
4. create at least one existing-pole candidate whose co-located fixture is node-eligible and one manual non-pole candidate if that site kind was approved; complete feasibility fields;
5. confirm the co-located fixture/root count-once, `0.000000 m`, hop-1, distinct-ID behavior and manual-site no-implicit-node behavior;
6. confirm Recommend is disabled for each missing blocker and enabled only after preflight;
7. run candidate calculation/ranking, Validate mode, and recommendation mode;
8. inspect deterministic score/topology/provenance/disclaimer and layer separation;
9. exercise preferred/prohibited status, CAP lock, node exclusion, primary reassignment, parent lock, invalid contradiction, and atomic preservation;
10. exercise N+1 or the approved single-CAP warning policy;
11. undo/redo a significant input without resurrecting stale output;
12. save, export portable JSON and updated KML, reopen JSON, and confirm exact current state;
13. verify updated KML has 74 source placemarks and zero CAP/manual-site/link geometry;
14. verify exact input KML SHA-256/bytes and source pole IDs/raw coordinates/numeric coordinates;
15. inspect browser console and require zero new errors.

Record exact inputs, visible outcomes, screenshots or durable equivalent evidence, console result, servers/ports, and limitations. Do not call the test-only inputs real-site approvals.

## 8. Commit and handoff

Before committing:

- inspect the complete diff and `git status`;
- confirm only authorized files changed;
- confirm no `Input/`, frozen catalog/schema, runtime project, cache, build, dependency, or Phase 7 file changed;
- confirm every acceptance row has objective PASS evidence or explicitly stop without claiming completion;
- confirm source bytes and Phase 1-5 regressions.

Write a Phase 6 implementation completion report containing:

- exact base/HEAD and commits;
- approved decisions and versions;
- changed files grouped by work package;
- algorithm/tie-break/cap details;
- migrations and exact preservation evidence;
- API/error/atomic behavior;
- fingerprint invalidation matrix;
- every acceptance ID with command/evidence/result;
- production-rendered 74-pole workflow;
- limitations and unresolved field/manufacturer inputs;
- independent QA status.

Commit only authorized Phase 6 implementation/handoff files with a clear commit. Do not push or merge. Do not declare Phase 6 accepted or closed. Request a separate independent QA task and leave Phase 7 gated.

## 9. Mandatory stop conditions during implementation

Stop, preserve the worktree, and ask the user rather than guessing if:

- an implementation-policy value or behavior is required but was not explicitly approved, and the gap cannot be represented as an approved runtime `unknown` state;
- the approved algorithm cannot satisfy a lock/constraint contract deterministically;
- an applicable legal/AHJ/regulatory requirement or exact-product manufacturer hard constraint conflicts with a project value, or source applicability/precedence is unresolved; do not accept a user waiver or the more permissive value;
- a new dependency, optimizer, RF model, export, schema-major change, or Phase 1-5 behavior change is needed;
- exact source/migration preservation fails;
- any safety cap would be silently bypassed, truncated, or partially calculated;
- a required rendered workflow cannot be verified;
- implementation would overstate RF, performance, redundancy, legal, professional, or standards claims.

Missing real-site band/jurisdiction, distance, node/child/hop values, gateway/node-count convention, candidate inventory/feasibility, or redundancy selection is not an implementation stop condition. Preserve the value as `unknown`, prove persistence and preflight blocking, and continue implementing the approved architecture.
