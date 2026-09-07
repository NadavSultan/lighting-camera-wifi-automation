# Phase work record — 2026-09-07 — BL-001

Status: implementation complete awaiting QA

## Scope, authority, and non-goals

- Requested work: authorized BL-001 Standard/Satellite session-only background (plan Task 8).
- Controlling documents: `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md` Task 8; `docs/post-roadmap-bl-001-provider-authorization-2026-09-07.md`; `docs/post-roadmap-backlog.md` BL-001; `harness/phases/2026-09-07-stage-8-bl-001-gated.md`; `docs/post-roadmap-bl-1-7-scoped-master-decision-2026-09-07.md`.
- Acceptance IDs governed by those documents: `BL001-01`, `BL001-02`, `BL001-03`, `BL001-04`.
- Authorized file boundary: modify `frontend/app/components/EngineeringMap.tsx`, `frontend/app/components/EngineeringWorkspace.tsx`, `frontend/app/globals.css`, `frontend/README.md`; create `frontend/app/lib/map-background.mjs`, `frontend/app/lib/map-background.d.mts`, `frontend/tests/map-background.test.mjs`, `frontend/.env.example`. Harness work/execution/verification records for this item. Provider-specific additional product paths require an explicit boundary amendment.
- Base commit and starting worktree status: `1febc8768ffac3ef38b212028867dab34790bff9` on `codex/bl-006-ies-associations`; `git status --short --branch` was clean (`## codex/bl-006-ies-associations`).
- Non-goals and later-phase exclusions: no Phase 8; no merge; no OBS-01; no project-schema change; no provider identity in project JSON/source/edits/calculations/reports; no commercial EOX license or purchased mosaic; no BL-001 acceptance claim without independent QA and a scoped master decision.
- Durable goal identifier/state: Cursor goal created 2026-09-07 — implement authorized BL-001; stop at implementation-readiness handoff without seal/merge/acceptance.
- Verifiable implementation stopping condition: work record, execution log, and verification for `BL001-01`–`BL001-04` exist; independent-QA handoff recorded; no seal and no merge.

Do not copy requirements from the controlling contract. Link them and record only execution-specific interpretation or unresolved conflict.

## Environment and file-boundary preflight

| Preflight item | Evidence | Result | Required path/configuration | Authorized? |
|---|---|---|---|---|
| Runtime discovery | `python --version` 3.12.7; `node --version` v24.19.0; `corepack pnpm --version` 12.3.4; `.venv` Python 3.12.7 | recorded | `.venv/Scripts/python.exe`; Node/pnpm | yes |
| Locked dependency materialization | existing `.venv` and `frontend/node_modules` from prior stages | historical present; not reinstalled this session | `backend/requirements.lock`; `frontend/pnpm-lock.yaml` (no lockfile edits) | yes — no lockfile change |
| Build/test/lint/typecheck commands | `OPERATIONS.md` frontend `pnpm run test/typecheck/lint/build`; backend pytest not required unless schema/API change | entry points exist | `frontend/package.json` | yes |
| Generated-artifact/validator commands | no schema/API change authorized | N/A this item | `schemas/` unchanged | yes — do not regenerate unless drift |
| Browser/rendered-QA runtime and ports | production SSR `rendered-html` suite; live MapLibre optional residual | helper + source tests first | ports 3000/8000 if live | yes |

Product changes must not begin until every required supporting path is either inside the authorized boundary or covered by an explicit recorded amendment.

`.env.example` is matched by existing `frontend/.gitignore` `.env*`. Creating the file is in-boundary; amending `.gitignore` is not. Commit opt-in remains `git add -f` if a later session authorizes a commit.

## Milestones

| Milestone | Contract reference | Expected evidence | Status |
|---|---|---|---|
| M0 provider verification | Task 8; provider authorization | Official EOX WMTS inspected at execution time | complete |
| M1 helper + tests | Task 8 interface; §16 fixtures | `map-background.test.mjs` red then green | complete |
| M2 map/workspace selector | Task 8 UI | satellite raster under engineering layers; session-only | complete |
| M3 verification/handoff | plan §14 item checklist | verification record; no seal/merge | complete |

## Acceptance criteria

| Acceptance ID / criterion | Verification method | Evidence location | Status |
|---|---|---|---|
| BL001-01 | helper + source wiring + frontend checks | `harness/verify/2026-09-07-bl-001-verification.md` | PASS (SSR/source; live MapLibre residual) |
| BL001-02 | helper visibility/session tests + source review (no `setStyle`) | same | PASS with residual live MapLibre |
| BL001-03 | helper fallback/attribution tests + UI copy | same | PASS |
| BL001-04 | helper secret/URL tests; schema hash; Input diff | same | PASS |

## Changes and evidence

- Changed files: Task 8 frontend paths plus item harness records; `frontend/.env.example` created (gitignored by existing `.env*`).
- Decisions applied: first satellite backend = free public EOX WMTS; product UI is Standard vs Satellite; config is environment-only.
- Commands and durable evidence: `harness/logs/2026-09-07-bl-001-execution.md`.

## Verification requirements

- Required deterministic commands: `pnpm run test` (focused `map-background` then full frontend), `typecheck`, `lint`, `build`; `git diff --exit-code -- Input`; project schema hash unchanged.
- Required generated-artifact freshness checks: OpenAPI/project schema not rewritten.
- Required source/hash preservation checks: `Input/` unchanged.
- Required rendered or manual workflows: production SSR/source wiring; live MapLibre residual if browser tools unavailable.
- Required regression scope: no engine/schema files.

## Definition of Done

- [x] All authorized milestones are complete.
- [x] Every required acceptance item has objective PASS evidence (live MapLibre residual recorded).
- [x] Every required deterministic command passed on the recorded worktree (uncommitted).
- [x] Source, prior-phase behavior, and file-boundary invariants are verified.
- [x] Completion and rendered evidence reports are present if required.
- [x] Independent QA handoff is recorded; QA itself remains pending.
- [x] No later phase has begun.
- [x] No harness seal created; no merge; no BL-001 acceptance claim.

## Unknowns, conflicts, and blockers

- Unknown runtime inputs: none for config names; live tile availability may rate-limit.
- Documentation conflicts: WMTS `ResourceURL` advertises `http://`; HTTPS tiles were verified and are the example values.
- Blocked work / required direction: none.

## Recovery protocol

Follow `AGENTS.md` and the work-record template. Preserve the worktree. Do not reset, clean, stash, or revert.

## Gate state

- Implementation: complete awaiting independent QA
- Durable goal: active
- Implementation-readiness verifier: not used as an item gate (would require inventing Phase 8)
- Independent QA: pending
- Master decision: pending
- Seal status: absent / not authorized
