# Work record — 2026-09-08 — Stage 1 P1 display reliability

Status: scoped master CONDITIONAL PASS 2026-09-08; bounded commit authorized, merge not authorized

## Scope, authority, and non-goals

- Requested work: Codex-staged Stage 0 + Stage 1 only: BL-009, BL-005 follow-up, BL-010, BL-011.
- Controlling documents: `docs/web-app-review-2026-09-08.md`; `docs/post-roadmap-backlog.md` 2026-09-08 intake; Cursor plan “Codex staged P1 plan”.
- Acceptance IDs governed by those documents: WA-01/BL-009, WA-02/BL-005 follow-up, WA-03/BL-010, WA-04/BL-011.
- Authorized file boundary: frontend CSS/components/lib/tests listed in the plan; harness work record, execution log, verification summary; backlog status notes only.
- Base commit and starting worktree status: `bc45b63da41092175f7fbda97bc4c24f1f39bfe9` on `codex/bl-006-ies-associations` (exact Codex review SHA; `merge-base --is-ancestor` exit 0). Unrelated uncommitted review docs preserved: `docs/post-roadmap-backlog.md` (modified), `docs/web-app-review-2026-09-08.md`, `harness/verify/2026-09-08-web-audit-observations.json`.
- Non-goals and later-phase exclusions: Stage 2+ (BL-012, BL-013, BL-014, BL-015, BL-016, BL-017, BL-018, BL-019, BL-020); BL-001 merge; merge to `main`; Phase 8; engine/schema/lockfile/Input changes; invented azimuths or CAP defaults.
- Durable goal identifier/state: Cursor `CreateGoal` activated 2026-09-08 — complete Stage 1 P1 items with recorded verification.
- Verifiable implementation stopping condition: `harness/verify/2026-09-08-stage1-p1-verification.md` records PASS for the four items on this checkout; frontend test/typecheck/lint/build pass.

Do not copy requirements from the controlling contract. Link them and record only execution-specific interpretation or unresolved conflict.

## Environment and file-boundary preflight

| Preflight item | Evidence | Result | Required path/configuration | Authorized? |
|---|---|---|---|---|
| Runtime discovery | Python 3.12.10 via `.venv`; Node v24.19.0 | pass | `.venv/Scripts/python.exe`; `frontend/package.json` engines | yes |
| Locked dependency materialization | `frontend/node_modules` present; backend venv present | pass | `frontend/pnpm-lock.yaml`; `backend/requirements.lock` | yes (no lockfile edits) |
| Build/test/lint/typecheck commands | `frontend/package.json` scripts test/typecheck/lint/build | pass | `frontend/package.json` | yes |
| Generated-artifact/validator commands | Stage 1 presentation only; no schema export | n/a | none | yes |
| Browser/rendered-QA runtime and ports | 3000/8000 free at Stage 0 | pass | local Vinext + FastAPI when live-checking | yes |

## Milestones

| Milestone | Contract reference | Expected evidence | Status |
|---|---|---|---|
| M0 identity and reproduce | Stage 0 | this record + execution log | complete |
| M1 BL-009 | WA-01 | CSS/shell fit; live widths | complete |
| M2 BL-005 follow-up | WA-02 | scheduler + arrows/? | complete |
| M3 BL-010 | WA-03 | labels track map | complete |
| M4 BL-011 | WA-04 | core stats unclipped | complete |
| M5 Stage 1 verify | plan verification | harness verify + frontend suite | complete |

## Acceptance criteria

| Acceptance ID / criterion | Verification method | Evidence location | Status |
|---|---|---|---|
| BL-009 viewport fit | CSS assertions + live layout | harness/verify/2026-09-08-stage1-p1-verification.md | PASS (implementer) |
| BL-005 follow-up arrows | scheduler tests + preview + live canvas size | same | PASS (implementer); live pixel sample residual |
| BL-010 label attach | scheduler tests + live pan/zoom canvas size | same | PASS (implementer) |
| BL-011 core stats | component/CSS + live card max-height | same | PASS (implementer) |

## Gate state

- Implementation: complete on dirty HEAD `bc45b63`
- Durable goal: complete
- Implementation-readiness verifier: not used as item gate
- Independent QA: PASS (`harness/verify/2026-09-08-stage1-p1-independent-qa-review.md`)
- Master decision: CONDITIONAL PASS `docs/post-roadmap-stage1-p1-scoped-master-decision-2026-09-08.md`
- Commit: authorized (bounded list); merge, push, Stage 2+, and any seal: not authorized
- Seal status: N/A (no Phase 8)
