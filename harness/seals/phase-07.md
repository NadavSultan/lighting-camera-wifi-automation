# Phase seal — Phase 7

Seal status: **VALID — ACCEPTED**

Seal date: 2026-09-05

## Scope and non-goals

- Sealed implementation: `e24b6a16add314393574257a08e539a27673a505`; evidence-only history reviewed through Independent QA packaging tip `dc9e1b57709ced30ba78799674331734af6cbc8c` (prior clean tip `a050007cd6fc847d77fa12beb5e25e7c02dcfbb3`).
- Controlling contract/phase record: `harness/phases/phase-07.md` (amended `P7-D08`); remediation design/plan dated 2026-09-05.
- Accepted scope: deterministic multi-format report packages (manifest, project JSON archive without embedded source upload bytes, derived engineering KMZ, CSV schedules, XLSX, PDF summary, presentation-model JSON) with conflict-safe APIs and Report Package UI.
- Non-goals and later-phase exclusions: no professional photometric validation claim, RF/compliance/installation approval, source-pole mutation, CAP operational-value invention, or any Phase 8 / post-roadmap work.

## Milestones and acceptance criteria

- Implementation milestones record: `harness/logs/2026-09-04-phase-7-execution.md`; `harness/verify/phase-07-readiness.json` — M0–M9 PASS.
- Complete acceptance-matrix record: `harness/verify/phase-07-readiness.json`; Independent QA `harness/verify/2026-09-05-phase-7-remediation-independent-qa-review.md`.
- Every acceptance ID disposition: all 18 IDs from `P7-DM-01` through `P7-PRD-01` have objective PASS evidence.

## Deterministic verification requirements

| Required check | Exact command/workflow | Sealed implementation/worktree | Evidence path | Result |
|---|---|---|---|---|
| Full backend tests | `.venv` Python `-m pytest -q -p no:cacheprovider` with isolated Windows `--basetemp`, before and after schema export | `e24b6a1`; evidence tip `dc9e1b5` | master gate decision; Independent QA review | PASS — 281 |
| Engineering/source validation | `.venv` Python `scripts/validate_engineering_data.py` | same | master gate decision; Independent QA review | PASS |
| Generated-contract freshness | `.venv` Python `-m scripts.export_schema`, then clean schemas status | same | master gate decision; Independent QA review | PASS |
| Frontend tests | `corepack pnpm run test` | same | master gate decision; Independent QA review | PASS — 20/20 |
| Strict typecheck | `corepack pnpm run typecheck` | same | master gate decision; Independent QA review | PASS |
| Lint | `corepack pnpm run lint` | same | master gate decision; Independent QA review | PASS |
| Production build | `corepack pnpm run build` | same | master gate decision; Independent QA review | PASS; non-failing chunk-size advisory |
| Contract-required rendered/manual workflow | production 74-pole M9 API+browser (`run_phase7_remediation_m9_complete.py`) | same | `harness/verify/2026-09-05-phase-7-independent-qa-m9-reproduction.json` | PASS; zero console errors |
| Diff/file-boundary/source-preservation checks | ancestry; protected `Input`/CAP schema diff; `git diff --check` worktree and `8a177b73..HEAD` after `P7-QA-10` cleanup | `e24b6a1`..`dc9e1b5` | master gate decision | PASS |

## Definition of Done

- [x] All authorized milestones complete.
- [x] All mandatory acceptance criteria have objective PASS evidence.
- [x] All deterministic verification rows pass on the exact unchanged implementation tree.
- [x] Required rendered/manual evidence passes on that implementation.
- [x] Source and prior-phase invariants pass; later phase remains untouched.
- [x] Independent QA decision is PASS: `harness/verify/2026-09-05-phase-7-remediation-independent-qa-review.md`.
- [x] Master gate decision is PASS: `docs/phase-7-master-gate-decision-2026-09-05.md`.

## Recovery protocol

If any cited evidence becomes stale, the implementation changes, or a correction is made, set this seal to INVALID, preserve it as historical evidence, rerun all affected verification, obtain new independent QA and master decisions for the changed implementation, and issue a new dated seal. Never edit evidence to conceal invalidation.

## Allowed stopping conditions

- Stop without sealing when any required evidence, check, or decision is missing, failed, skipped, stale, or blocked.
- Stop after this valid seal is recorded. This seal does not authorize preparation or implementation of Phase 8 or other post-roadmap work.

## Gate evidence

- Verification summary: `harness/verify/2026-09-05-phase-7-remediation-verification-summary.md`; master verification in `docs/phase-7-master-gate-decision-2026-09-05.md`.
- Independent QA PASS: `harness/verify/2026-09-05-phase-7-remediation-independent-qa-review.md`.
- Master gate PASS: `docs/phase-7-master-gate-decision-2026-09-05.md`.
- Seal author/date: master review, 2026-09-05.
- Exact next action authorized by a separate decision, if any: none. Post-roadmap work remains gated.
