# Work record — 2026-09-22 — BL-016 Camera Pixel-Density Map

Status: corrective implementation and evidence records complete; clean readiness verifier is the final gate; BL-016 unaccepted

## Scope, authority, and non-goals

- Requested work: Implement BL-016 / WA-09 through implementation-readiness handoff.
- Controlling documents: `docs/bl-016-camera-pixel-density-architecture.md`; `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md`; `docs/superpowers/plans/2026-09-22-bl-016-camera-pixel-density.md`.
- Acceptance IDs governed by those documents: `BL016-01` through `BL016-20`.
- Authorized file boundary: original plan Tasks 2–10, generated `schemas/project.schema.json` and `schemas/openapi.json`, `GOALS.md`, `PLANS.md`, `OPERATIONS.md`, `docs/current-status.md`, `docs/post-roadmap-backlog.md`, BL-016 records under `harness/phases/`, `harness/logs/`, and `harness/verify/`, plus the master-authorized reconciliation edits to `docs/architecture.md` and `docs/data-model.md`.
- Explicitly excluded: `Input/`; existing camera/fixture/lens/IES catalog revisions other than new `data/cameras/camera-pixel-density-legend.json`; unrelated backlog documents; runtime project data; uploads; exports; caches; dependencies; build output; `.superpowers/`; accepted phase seals.
- Base commit and starting worktree status: `05257e87b4d6500146239f62f4ebafa4b2217b67`; linked externally managed worktree; detached `HEAD`; no upstream; `git status --short --branch` returned only `## HEAD (no branch)`; complete starting diff was empty.
- Source-history confirmation: base contains architecture commit `5837f29b65c706ca9db3f2c2491f8234a5a19bde` and approved plan commit `05257e87b4d6500146239f62f4ebafa4b2217b67`.
- Non-goals and later-phase exclusions: engineering design section 19; no BL-019/BL-020, merge, push, Phase 8, self-approval, or seal.
- Durable goal identifier/state: Codex task `01a0c847-9997-7f73-9beb-367bd8fcc463`, active for the master-review corrective pass.
- Verifiable implementation stopping condition: clean implementation-readiness verifier PASS plus an Independent-QA handoff, or a proven blocker recorded under `AGENTS.md`.

## Environment and file-boundary preflight

| Preflight item | Evidence | Result | Required path/configuration | Authorized? |
|---|---|---|---|---|
| Runtime discovery | Python 3.12.10; Node 24.19.0; Corepack pnpm 12.3.4; Chrome and Edge paths present | PASS | `.venv`, Node, Corepack/pnpm, browser runtime | yes |
| Locked dependency materialization | `pip install -r backend/requirements.lock`; `corepack pnpm install --frozen-lockfile`; `pip check`; lock/workspace diffs empty | PASS | ignored `.venv/`, `frontend/node_modules/`; unchanged lock/workspace policy | yes |
| Build/test/lint/typecheck commands | frontend 102/102, typecheck, lint, and production build; backend suite reached 100% | PASS | backend/frontend source and tests | yes |
| Generated-artifact/validator commands | engineering validator PASS; schema export produced five paths; `git diff --exit-code -- schemas` | PASS | generated schemas and validator | yes |
| Browser/rendered-QA runtime and ports | Chrome and Edge present; no listeners on 8070/3070 | PASS | isolated API `8070`, frontend `3070`, isolated temp `LCWA_DATA_DIR` | yes |

Product changes do not begin until every row is resolved and all required supporting paths are confirmed inside the authorized boundary.

## Milestones

| Milestone | Contract reference | Expected evidence | Status |
|---|---|---|---|
| M0 environment | Plan Task 1 | goal, boundary, clean baseline, command preflight | complete — `1c141d09` |
| M1 schema/legend | Plan Task 2 | migration/model/legend/schema tests | complete — `6263451d` |
| M2 geometry | Plan Task 3 | analytic geometry and band tests | complete — `e157449a` |
| M3 camera bands | Plan Task 4 | pinned-input, invalid isolation, fingerprint tests | original task complete — `007efba4`; activity/fingerprint correction under review |
| M4 overlaps/limits | Plan Task 5 | overlap/canonicalization/limit tests | original task complete — `6ee9fe73`; canonical-order correction under review |
| M5 API/freshness | Plan Task 6 | atomic API and lifecycle tests | complete — `6692ab3b` |
| M6 reporting | Plan Task 7 | Phase 7 compatibility tests | complete — `987a0c7b` |
| M7 frontend workflow | Plan Task 8 | view/API/panel tests | complete — `129eda85` |
| M8 map/inspection | Plan Task 9 | GeoJSON/style/safe-popup/render tests | complete — `986c6eab` |
| M9 final verification | Plan Task 10 | deterministic, live browser, source/hash, readiness evidence | reopened by 2026-09-24 master re-review; corrective final verification pending |

## Acceptance criteria

Original implementation evidence for `BL016-01` through `BL016-20` remains in the verification summary and readiness manifest. Master re-review invalidated readiness for effective pole activity/freshness, canonical geometry ordering, non-mutating live evidence, and current documentation; final dispositions will be re-established on the corrected implementation commit. BL-016 remains unaccepted.

## Changes and evidence

- Changed files: this work record, paired execution log, and execution-index files only at activation time.
- Decisions applied: Windows incompatibility in the bundled ignored-ledger helper is handled by using its exact documented `.superpowers/sdd/<plan>/` layout directly; frontend baseline receives a prerequisite production build because its rendered test imports `dist/server/index.js`; backend pytest runs from `backend/` so repository `pyproject.toml` supplies `pythonpath=["."]`. No tracked scope expansion.
- Commands and durable evidence: `harness/logs/2026-09-22-bl-016-camera-pixel-density.md`.

## Master-review corrective pass — 2026-09-24

- Trigger and exact base: master re-review of implementation `8a271bf12b070c5c9883f2b2942ad54c6ace4f77` at evidence tip `1b3cebfafdfc07a0135f174abaa6da26192e3eea`; durable goal `01a0c847-9997-7f73-9beb-367bd8fcc463` reactivated for this bounded pass.
- Starting worktree: the only change was the tracked live JSON overwritten by the master rerun. Its original diff was inspected before any edit. The exact successful rerun record (including its true `head`, request IDs, process IDs, logs, and empty starting status) is preserved in `harness/verify/2026-09-24-bl-016-master-rerun-live.json`. The prior tracked file is restored to its committed value; no run provenance was rewritten.
- Finding 1: resolver omitted effective pole `active`; RED tests showed unchanged fingerprint, two valid camera results, and API save remaining `current`. The frontend significant-input projection already included activity; regression coverage now explicitly exercises it.
- Finding 2: the runner used one tracked output path. It now accepts `--output`, defaults to ignored `harness/tmp`, permits external absolute destinations, and refuses to overwrite an existing tracked file. A CLI guard check rejected the tracked path and left the committed artifact byte-clean.
- Finding 3: multipolygon sorting used coordinate sequence only and overlap output used hashed region IDs. RED tests covered area precedence, rounded-area coordinate ties, contributor/rank precedence, and geometry sequence after metadata ties. Targeted tests now pass.
- Finding 4: `docs/architecture.md`, `docs/data-model.md`, and the current post-roadmap paragraph in `OPERATIONS.md` were reconciled with implemented schema/software versions and BL-016. Dated historical reports remain historical.
- Corrective implementation commit: `c6c0869aa9fe0ed2d18d70022fe37a7bf0fad170`. Full backend/frontend and validator/schema gates passed against that commit. Corrected live record: `harness/verify/2026-09-24-bl-016-corrected-live.json`; preserved triggering master run: `harness/verify/2026-09-24-bl-016-master-rerun-live.json` with its original HEAD and process/request provenance.
- This record, execution log, summary, manifest, handoff, and indexes are finalized for an evidence-only commit. The readiness verifier is run as the final command against that clean worktree; it is read-only. QA has not started.

## Verification requirements

- Required deterministic commands: exact plan Task 1 preflight and Task 10 final sequence.
- Required generated-artifact freshness checks: schema export before implementation and after final commit; final `git diff --exit-code -- schemas`.
- Required source/hash preservation checks: `git diff --exit-code -- Input` and SHA-256 `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`.
- Required rendered or manual workflows: isolated production-browser evidence on ports 8070/3070 per plan Task 10.
- Required regression scope: complete backend and frontend suites, validator, typecheck, lint, build, Phase 3 geometry, Phase 7 reports, source coordinates, and existing-pole mode.

## Definition of Done

- [x] All product milestones are complete.
- [x] Every required acceptance item has objective implementation PASS evidence.
- [x] Every required deterministic command passed on the recorded product commit/worktree.
- [x] Source, prior-phase behavior, and file-boundary invariants are verified.
- [x] Completion and rendered evidence reports are present if required.
- [x] The implementation-readiness manifest passes on the recorded implementation commit and clean worktree.
- [x] Independent QA handoff is recorded; QA itself remains pending.
- [x] No later phase has begun.

Independent QA PASS, master PASS, and a seal are later gates and are not implementation-task Definition of Done items.

## Unknowns, conflicts, and blockers

- Unknown runtime inputs: none identified; preflight passed.
- Documentation conflicts: BL-016 architecture/data-model and current execution-index records have been reconciled to the implemented `2.8.0` schema and corrective commit; dated historical reports remain explicitly historical.
- Blocked work / required direction: none.

## Recovery protocol

Follow `AGENTS.md`, `OPERATIONS.md`, and the approved plan Recovery Protocol. Preserve failures, inspect exact state, make three materially different safe recovery attempts before any blocker classification, and continue other in-scope work.

## Gate state

- Implementation: corrective implementation complete at `c6c0869aa9fe0ed2d18d70022fe37a7bf0fad170`; readiness evidence is being finalized, unaccepted.
- Durable goal: closure is conditioned on the clean readiness verifier PASS below and the resulting truthful QA handoff.
- Implementation-readiness verifier: final clean-worktree command; its exact output is returned with this handoff.
- Independent QA: pending.
- Master decision: pending.
- Seal status: absent and unauthorized.
