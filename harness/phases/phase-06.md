# Phase 6 execution contract — CAP / JNET1 graph-and-constraint planning

Contract prepared: 2026-08-30

Status: ready for execution; implementation not started in this checkout

Phase gate: authorized, active, open, and unaccepted

This execution contract organizes the approved Phase 6 work. It does not replace, narrow, expand, or reinterpret the controlling product contract, and it does not approve any real-site operational value.

## Objective

Implement the approved Phase 6 CAP / JNET1 Gateway graph-and-constraint planning MVP described by `docs/phase-6-cap-planning-and-implementation-contract.md` and `docs/phase-6-master-implementation-prompt.md`. The implementation must preserve existing-pole mode, immutable source data, and all accepted Phase 1-5 behavior while adding strict unknown-aware CAP inputs, deterministic projected-distance graph planning, bounded recommendation from explicit candidate sites, validation/manual-control workflows, atomic APIs, typed UI/map layers, and complete verification evidence.

Phase 6 remains conceptual graph-and-constraint planning. It is not RF prediction, a deployable network design, a compliance determination, or Phase 7 reporting.

## Authority and controlling records

- Implementation-policy authority: all 20 decisions in `docs/phase-6-cap-planning-and-implementation-contract.md`, section 16, approved on 2026-08-27.
- Separate implementation authority: `docs/decision-log.md` DL-016 and the authorization banner in `docs/phase-6-master-implementation-prompt.md`.
- Controlling acceptance criteria: every row in the Phase 6 contract section 15, `P6-DM-01` through `P6-PRD-01`.
- Controlling architecture and invariants: `AGENTS.md`, `PROJECT_CONTEXT.md`, `docs/current-status.md`, `docs/implementation-plan.md`, `docs/architecture.md`, `docs/data-model.md`, and prior accepted phase gate records.
- Frozen CAP evidence: `Input/CAP/CAP datasheet.pdf`, `data/network/cap-constraints.json`, `schemas/cap-constraints.schema.json`, and the linked engineering evidence documents. These are read-only inputs, not project defaults.

Where this file and a controlling record differ, the controlling record wins and execution stops until the discrepancy is recorded and resolved.

## Current verified state

- Current branch/commit at contract preparation: `main` at `72441d2c5bdc3f44f4fa13e7d4e494dde50d07d7` (`docs: authorize Phase 6 implementation`). This commit includes the authorization history after the planning contract's earlier recorded baseline `100d458a`.
- Current application baseline: project schema `2.5.0`, software/API `0.5.0`, and Phase 5 conceptual Wi-Fi. `backend/app/services/cap_planning.py`, `backend/tests/test_phase6_cap_planning.py`, and `frontend/app/lib/phase6-cap-workflows.mjs` do not exist in this checkout; no Phase 6 application implementation is integrated here.
- Phases 1-5 are accepted and closed. Phase 6 is authorized but has no implementation, independent-QA, master-acceptance, or seal evidence in this checkout. Phase 7 is unauthorized.
- Current Phase 5 seams include strict Pydantic models, additive migrations through `2.5.0`, complete-project API responses, atomic filesystem replacement, immutable source checks, projected-CRS services, calculation fingerprints/invalidation, typed frontend transport, undo/redo, CAP-gated UI controls, and existing `cap_locations` / `cap_connections` layer keys.
- Current-worktree baseline evidence recorded in `harness/verify/2026-08-30-workflow-review.md`: backend full suite PASS with 137 tests and one known deprecation warning; engineering/source validator PASS; project-schema/OpenAPI in-memory freshness PASS; `git diff --check` PASS. Frontend test/typecheck/lint/build were not run because dependencies are absent in this checkout, so no current frontend PASS is claimed.
- The working tree already contains the user-authorized workflow/bootstrap documentation changes listed by `git status`. They are pre-existing to Phase 6 implementation and must be preserved. This contract is the only file added by its preparation task.
- Work reported in any separate worktree or session is not current-repository evidence until its exact commits and diff are deliberately reconciled into the execution worktree and all affected verification is rerun.

## Dependencies

### Approved implementation dependencies

- Python 3.12 with the repository's FastAPI, Pydantic, PyProj, Shapely, defusedxml, pytest, httpx, and jsonschema constraints.
- Node.js `>=22.13.0`, pnpm, and the exact frontend dependency graph already recorded by the repository lockfile/package metadata.
- A projected CRS with metre axes for every graph/distance operation; WGS84 remains display/interchange only.
- Read-only access to the frozen CAP constraint catalog/datasheet evidence and the supplied 74-pole KML.
- An isolated project store and production frontend/backend processes for rendered QA.

No new dependency, optimizer, RF library, database, migration framework, or external service is approved by this contract. If an existing environment is unavailable, record the missing dependency and request authority before installing or changing dependencies.

### Runtime dependencies that remain explicitly unknown

The following Miracle Mile values are not approved decisions or implementation defaults: CAP-to-product/variant mapping, LITE/WIFI/SMART node dispositions, band/jurisdiction, planning link distance, project node/child/hop limits, gateway/co-located-fixture counting selections, candidate inventory and feasibility, and redundancy selection.

Their absence does not block implementation of the approved models, persistence, UI, preflight, algorithms, and tests. They must remain storable unknowns with provenance fields and must block only the dependent runtime calculate/validate/recommend operation. Tests and rendered QA may use conspicuously labelled test-only records; those records are never Miracle Mile approvals.

## Authorized file boundary

Future Phase 6 implementation may change only the boundary in `docs/phase-6-master-implementation-prompt.md`, section 4:

- `backend/app/models.py`, `backend/app/main.py`, new `backend/app/services/cap_planning.py`, and the smallest necessary service invalidation hooks;
- `backend/app/services/store.py` only for a focused, tested atomic-preservation correction;
- focused backend tests, including new `backend/tests/test_phase6_cap_planning.py`;
- `frontend/app/lib/types.ts`, `frontend/app/lib/api.ts`, new `frontend/app/lib/phase6-cap-workflows.mjs`;
- `frontend/app/components/EngineeringWorkspace.tsx`, `EngineeringMap.tsx`, `globals.css`, and `PoleInspector.tsx` only if approved node controls require it;
- `frontend/tests/rendered-html.test.mjs`;
- `frontend/pnpm-workspace.yaml` only to materialize the approved locked-dependency build-script policy (`esbuild: true`, `sharp: false`, `workerd: false`); this does not authorize a dependency addition, removal, upgrade, or unrelated workspace-policy change;
- generated `schemas/project.schema.json` and `schemas/openapi.json`;
- `backend/pyproject.toml` and `frontend/package.json` for the approved `0.6.0` metadata only;
- explicitly required Phase 6 decision, completion, rendered-QA, execution-log, and verification documents.

Any additional file requires explicit scope review before it changes. The `frontend/pnpm-workspace.yaml` exception above is the explicit 2026-08-30 boundary amendment recorded in `docs/decision-log.md` DL-017; it resolves the preflight contract defect and is not a new dependency authorization. `Input/`, the seven frozen engineering catalogs/schemas, prior-phase reports, runtime projects, caches, build output, dependency directories, and Phase 7 files are outside the boundary.

## In-scope work

- Strict, finite, unknown-aware Phase 6 models and additive `2.6.0` migration with separate user, calculated, and recommended CAP collections.
- Project/software/model versions `2.6.0`, `0.6.0`, and `jnet1-graph-planning-1.0.0` exactly as approved.
- Explicit product/band/jurisdiction/design-limit/counting/redundancy provenance and conflict states with the approved source precedence.
- Existing-pole and manual non-pole candidate records, explicit node policy, site feasibility, locks, exclusions, reassignment, and parent constraints.
- Pure deterministic projected-metre graph construction, candidate ranking, Validate mode, recommend-from-approved-pool mode, bounded improvement, constraint checks, and approved redundancy diagnostics.
- Exact safety caps, canonical fingerprints, result provenance, invalidation, no-stale-result behavior, and controlled atomic failure.
- Approved complete-project API endpoints and 404/409/422 behavior.
- Generated project schema/OpenAPI, typed frontend API/workflow helpers, undo/redo, preflight, CAP UI, and independent map layers.
- Full acceptance-matrix tests and production-rendered supplied 74-pole QA.
- Implementation completion evidence and handoff to independent QA without claiming Phase 6 acceptance.

## Explicit non-goals

- No real-site operational value is selected, inferred, recommended as a default, or marked approved.
- No RF coverage, propagation, link budget, antenna, terrain/obstruction, interference, channel, throughput, latency, availability, or service-quality engine.
- No legal, regulatory, professional, standards-compliance, installation-feasibility, or performance guarantee.
- No automatic creation, movement, redistribution, optimization, or deletion of customer lighting poles; no free-space pole generation.
- No automatic candidate coordinates or inference of fixture/node participation, product identity, band, range, margins, capacity target, hop target, redundancy, or site utilities.
- No procurement/BOM approval, installation drawing, backhaul/power design, permitting, commissioning, or substitute for field survey.
- No CAP KML/KMZ, CSV/XLSX, PDF, presentation, or other Phase 7 reporting. Portable project JSON is the only Phase 6 export; updated KML remains free of CAP geometry/data.
- No modification of accepted Phase 1-5 contracts or behavior except an explicitly approved, focused compatibility correction proven by regression tests.
- No dependency additions or upgrades.

## Implementation milestones

Phase 6 implementation must run as one durable goal created through the environment's actual goal mechanism. Its normal stopping condition is a passing Phase 6 implementation-readiness manifest plus the independent-QA handoff. A progress report, ordinary response boundary, partial pass, milestone completion, commit, or completion report does not end the goal.

Before product changes, M0 must also complete the environment/file-boundary preflight required by `AGENTS.md` and the work-record template. This includes the locked frontend install, bundled runtime paths, build/test/lint/typecheck entry points, schema/validator commands, local production servers/browser access, runtime directories/ports, and every supporting repository configuration path. An omitted required configuration path must be resolved as a contract defect before implementation proceeds.

Every milestone begins by recording exact `HEAD`, worktree status, and changed files in a dated execution log under `harness/logs/`. A milestone is not complete unless its command succeeds against that recorded worktree and its acceptance evidence is linked. Completing one milestone is a checkpoint; continue immediately to the next incomplete milestone.

| ID | Milestone | Contract coverage | Required verification command | Completion evidence |
|---|---|---|---|---|
| M0 | Governance, durable goal, and execution baseline | Prompt WP1; authorization, decisions, base, boundary, unknowns | From repository root: `git status --short --branch`; `git rev-parse HEAD`; `git diff --name-only`; `git diff --check`; then run and record the work-record environment/file-boundary preflight | Execution log identifies the active durable goal, exact authorized base, pre-existing changes, all 20 decision references, runtime unknowns, verified toolchain/runtime requirements, and complete authorized file boundary. |
| M1 | Strict models, versions, and lossless migration | WP2; `P6-DM-01..04`, `P6-CT-01`, `P6-MG-01` | From `backend/`: `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase6_cap_planning.py -k "p6_dm or p6_ct or p6_mg"` | Strict model/unknown/conflict/counting/migration tests pass; source and every Phase 1-5 collection remain lossless and migration is idempotent. |
| M2 | Pure graph construction and deterministic ranking | WP3 graph/ranking; `P6-GR-01..03`, `P6-AL-01..02` | From `backend/`: `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase6_cap_planning.py -k "p6_gr or p6_al_01 or p6_al_02"` | Projected-distance boundary, topology fixtures, shuffled input, repeated run, canonical IDs/order, and every tie-break pass. |
| M3 | Selection, manual controls, redundancy, safety, fingerprint, and provenance | WP3 remaining scope; `P6-AL-03..04`, `P6-MN-01`, `P6-RD-01..03`, `P6-SF-01..02`, `P6-FP-01`, `P6-PR-01` | From `backend/`: `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_phase6_cap_planning.py -k "p6_al_03 or p6_al_04 or p6_mn or p6_rd or p6_sf or p6_fp or p6_pr"` | Recommendation uses only approved candidates, all constraints/caps are deterministic and atomic, redundancy policies are exact, and fingerprint/provenance/disclaimer evidence passes. |
| M4 | Atomic API and persistence lifecycle | WP4; `P6-AP-01..02`, `P6-FP-01`, `P6-EX-01` | From `backend/`: `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_api.py tests/test_phase6_cap_planning.py -k "p6_ap or p6_fp or p6_ex or import_save_reopen"` | Approved endpoints return complete projects; 404/409/422 and failed mutations preserve exact saved/source/result bytes; JSON round-trip and KML exclusion pass. |
| M5 | Generated contracts and version metadata | WP5; `P6-DM-01`, `P6-MG-01`, `P6-AP-01`, `P6-REG-01` | From `backend/`: `..\.venv\Scripts\python.exe .\scripts\export_schema.py`; then `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider -k "schema or openapi or p6_mg or p6_ap"`; from root: `git diff --check -- schemas/project.schema.json schemas/openapi.json backend/pyproject.toml frontend/package.json` | Generated files are derived from authoritative models/OpenAPI, freshness tests pass, and only approved version/generated files change. |
| M6 | Typed frontend transport and pure workflow helpers | WP6; `P6-FP-01`, `P6-UI-01..02` | From `frontend/`: `pnpm run build`; `pnpm run test`; `pnpm run typecheck`; `pnpm run lint` | Strict Phase 6 types/API compile; helper tests prove preflight, revision, invalid draft, contradiction, stale invalidation, and undo/redo preservation behavior. |
| M7 | Rendered CAP panel, controls, and independent map layers | WP7; `P6-UI-01..04` | From `frontend/`: `pnpm run build`; `pnpm run test`; `pnpm run typecheck`; `pnpm run lint` | Production-rendered test suite proves required UI copy/gates, candidate/manual workflows, colors/layers, manual-site symbol, disclaimers, and no later-phase controls. |
| M8 | Complete automated regression and engineering/source validation | WP8; all automated rows plus `P6-REG-01` | Run the complete final verification block in the next section, excluding only the interactive server processes while they are not needed | All backend/frontend/schema/engineering/source/diff checks pass on one exact implementation commit with warnings recorded. |
| M9 | Genuine production-rendered 74-pole QA and implementation handoff | Prompt sections 7-8; `P6-PRD-01`, `P6-UI-01..04`, `P6-EX-01` | Backend terminal: `$env:LCWA_DATA_DIR = Join-Path $env:TEMP "lcwa-phase6-qa"`; `Set-Location .\backend`; `..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8026`. Frontend terminal after production build: `$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:8026"`; `Set-Location .\frontend`; `pnpm run start -- --host 127.0.0.1 --port 3026` | Durable rendered evidence covers all 15 prompt section-7 steps, zero new console errors, exact source hash/coordinates, JSON reopen, KML exclusion, unknown-state blockers, test-only scenario, controls, topology, redundancy, and disclaimers. Completion report requests independent QA and does not close Phase 6. |

If the configured runtime path differs, use the repository-approved equivalent and record the exact replacement command. Do not claim a milestone PASS when its command or required rendered evidence was skipped.

## Acceptance criteria

The following groups are mandatory exactly as written in the controlling contract section 15. This table is an execution index, not a replacement acceptance matrix.

| Acceptance group | Mandatory IDs | Required disposition |
|---|---|---|
| Strict data, unknowns, precedence, counting | `P6-DM-01..04`, `P6-CT-01` | Every row independently evidenced as PASS; unresolved real-site values remain storable/blocking, not defaults. |
| Geometry and deterministic algorithms | `P6-GR-01..03`, `P6-AL-01..04` | Every synthetic boundary/topology/order/tie/selection case passes deterministically. |
| Manual controls and redundancy | `P6-MN-01`, `P6-RD-01..03` | Valid controls persist/revalidate; contradictions fail atomically; each approved redundancy mode has exact evidence. |
| Safety, fingerprints, and provenance | `P6-SF-01..02`, `P6-FP-01`, `P6-PR-01` | Every safety boundary and boundary+1 case passes/fails as specified; no stale results; complete provenance/disclaimer. |
| API, migration, and export | `P6-AP-01..02`, `P6-MG-01`, `P6-EX-01` | Complete-project API/error semantics, exact failure preservation, lossless migration/idempotence, JSON round-trip, and CAP-free KML pass. |
| Rendered UI | `P6-UI-01..04` | Required blockers, controls, layers/colors/symbols, and exact non-RF wording pass through genuine UI behavior. |
| Regression and production workflow | `P6-REG-01`, `P6-PRD-01` | Full regression, generated freshness, browser-console health, and supplied 74-pole workflow pass on the exact final commit. |

No criterion may be marked not-applicable, waived, or passed by historical evidence unless the controlling contract is explicitly amended by the user. Test-only planning records must remain labelled and cannot satisfy a missing real-site approval.

## Final verification command

Run from repository root using the configured runtimes. Every external command must exit successfully; stop and record the first failure rather than continuing to a completion claim.

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider

Set-Location ..
.\.venv\Scripts\python.exe .\scripts\validate_engineering_data.py

Set-Location .\backend
..\.venv\Scripts\python.exe .\scripts\export_schema.py
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider

Set-Location ..\frontend
pnpm run build
pnpm run test
pnpm run typecheck
pnpm run lint

Set-Location ..
git diff --check
git diff --check 72441d2c..HEAD
git diff --exit-code 72441d2c..HEAD -- Input
git status --short
```

After this block, run and record M9's production-rendered workflow on the same exact implementation commit. Inspect `git diff --name-only 72441d2c..HEAD` and the complete diff to confirm the authorized boundary, frozen catalogs/schemas, prior reports, runtime data, dependencies, and Phase 7 remain untouched. Schema regeneration must be byte-fresh on the second backend run. Known non-failing advisories may be reported but never hidden.

After committing the implementation and evidence, complete `harness/verify/phase-06-readiness.json` from the implementation-readiness template and run:

```powershell
python harness/verify/verify_phase_readiness.py --manifest harness/verify/phase-06-readiness.json
```

The readiness command must pass against a clean worktree. Its PASS authorizes only the independent-QA handoff; it does not accept or seal Phase 6.

## Definition of Done

Phase 6 implementation is ready for independent QA only when all items below are true:

- [ ] M0 through M9 are complete with dated execution logs and exact commit/worktree identity.
- [ ] Every contract acceptance row `P6-DM-01` through `P6-PRD-01` has objective PASS evidence.
- [ ] Project/software/model versions and all generated contracts match the approved values and are fresh.
- [ ] Unknown/conflicting real-site inputs round-trip without defaults and block only dependent runtime operations.
- [ ] Determinism, source precedence, counting alternatives, manual controls, redundancy modes, all safety boundaries, fingerprint invalidation, and provenance are proven.
- [ ] Every failed API/operation test preserves exact project/source/prior-result bytes; no partial result is persisted.
- [ ] All supported migrations preserve exact embedded source, raw/numeric coordinates, pole IDs/order, every Phase 1-5 collection, and unknown `recommended_layers`; second migration is a no-op.
- [ ] Updated KML contains the 74 original placemarks and no CAP/manual-site/link/recommendation geometry; portable JSON saves/reopens Phase 6 state.
- [ ] Full backend, engineering/source validation, generated freshness, frontend test/typecheck/lint/build, production-rendered workflow, and zero-new-console-error checks pass on the exact final commit.
- [ ] Complete diff review proves only authorized files changed; no `Input/`, frozen catalog/schema, dependency, runtime project, cache/build output, prior-phase report, or Phase 7 change exists.
- [ ] A Phase 6 implementation completion report records commits, changed files, algorithms/caps, migration/source preservation, API/atomic behavior, fingerprint matrix, every acceptance ID, rendered evidence, warnings/limitations, and independent-QA status.
- [ ] The durable goal remains active through M9 and reaches its verifiable stopping condition rather than ending at a progress checkpoint.
- [ ] `harness/verify/phase-06-readiness.json` exactly lists M0-M9 and every acceptance ID, and the readiness verifier passes on a clean worktree.
- [ ] The implementation task requests independent QA and does not mark Phase 6 accepted, sealed, or closed.

Independent QA PASS and master gate PASS are required for phase acceptance and sealing, but they occur after implementation Definition of Done and cannot be self-issued by the implementation task.

## Recovery protocol

1. Preserve the worktree, execution log, failing output, and last verified commit. Do not reset, discard, auto-resolve, or overwrite evidence.
2. Record the interrupted/failed milestone, exact command and exit state, partial artifacts, affected acceptance IDs, and whether generated files or runtime stores may be stale.
3. Reinspect `git status --short --branch`, `git rev-parse HEAD`, `git diff --name-only`, and the complete affected diff before resuming.
4. If a write-producing command failed, treat all artifacts it could touch as unverified. Regenerate/revalidate them from their authoritative source before continuing.
5. If implementation changes after a milestone PASS, invalidate and rerun every affected milestone, final verification item, rendered workflow, and QA result.
6. Resume only from the last evidence that remains applicable and only within the authorized file boundary. Preserve unrelated/user-owned workflow changes.
7. If work exists in another worktree, identify its exact base/HEAD/commits and inspect its complete diff before integration. Do not equate a handoff or completion report with repository evidence.
8. Treat failing/missing tests, incomplete coverage/milestones, build/lint/typecheck/compiler failures, generated drift, runtime paths, ports, temporary process/cache/file locks, dependency materialization, dirty implementation files, missing reports, and response-turn boundaries as repair work; log, repair, rerun, and continue.
9. Before claiming a blocker, create a blocker record and make at least three materially different safe recovery attempts. Continue other meaningful in-scope work while one command is recoverably unavailable.
10. Stop for user direction only when the completed blocker record proves no meaningful in-scope progress remains and identifies the exact new authority, product decision, external-state change, or prohibited scope expansion required. Do not invent a decision or transform an unknown into an assumption/default.

## Allowed stopping conditions

Execution may stop early and request direction only when a valid blocker record proves three materially different safe recovery attempts failed, no meaningful in-scope work can continue, and one of the following requires new authority or external change:

- implementation authorization or any approved policy decision becomes contradictory, missing, or replaced without a recorded decision;
- the actual implementation base/diff cannot be reconciled with the authorized repository state;
- required behavior is not defined and cannot be represented by the already-approved runtime unknown state;
- applicable legal/AHJ/regulatory or exact-product manufacturer precedence/applicability conflicts cannot be resolved without choosing a permissive value;
- implementation requires a new dependency, optimizer, RF model, external service, database, schema-major change, export, extra file boundary, Phase 1-5 behavior change, destructive action, or Phase 7 work;
- source-byte, pole/coordinate, migration, atomic-preservation, deterministic-order, safety-cap, or no-stale-result invariants cannot be maintained;
- the approved algorithm cannot satisfy locks/constraints deterministically;
- a required automated or production-rendered verification cannot be run or cannot pass truthfully after safe in-scope recovery is exhausted;
- wording or behavior would overstate RF, performance, redundancy, legal, professional, standards, or installation claims.

Missing Miracle Mile runtime band/jurisdiction, distance, node/child/hop limits, counting convention, candidate facts, or redundancy selection is not an allowed implementation stop by itself. Preserve the unknown, prove persistence and preflight blocking, and continue the approved implementation.

Implementation may stop normally only after its Definition of Done is satisfied, the implementation-readiness verifier passes, and the independent-QA handoff is recorded. It still must not seal or close the phase.

## Expected phase seals

- During implementation: **no phase seal**. Milestone logs, verification summaries, completion reports, and rendered evidence are not seals.
- After implementation: independent QA must review the exact implementation commit and record PASS against every mandatory acceptance item; a correction invalidates affected evidence and requires retest.
- After independent QA: the master gate must record PASS and formally accept Phase 6.
- Only then may `harness/seals/phase-06.md` be created from `harness/templates/phase-seal-template.md` with status `VALID — ACCEPTED`, citing the exact sealed commit, complete deterministic/rendered verification, independent QA PASS, and master PASS.
- Any missing, failed, skipped, stale, historical-only, or unrecorded required check keeps the Phase 6 seal invalid. A valid Phase 6 seal does not authorize Phase 7.

## Gate state at contract preparation

- Implementation: authorized; not integrated or verified in this checkout.
- Independent QA: not started for a current integrated implementation commit.
- Master decision: pending.
- Seal status: absent and not eligible.
- Exact next action: begin M0 in the authorized Phase 6 implementation worktree, record the exact base/diff and reconcile any separate worktree evidence before changing application files.
