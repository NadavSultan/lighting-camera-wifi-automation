# Execution log — 2026-09-08 — Stage 1 P1 display reliability

## Scope and non-goals

- Phase work record: `harness/phases/2026-09-08-stage1-p1-display.md`
- Controlling contract and acceptance IDs: `docs/web-app-review-2026-09-08.md` WA-01..WA-04 / BL-009, BL-005 follow-up, BL-010, BL-011
- Authorized work/milestone: Stage 0 then Stage 1 only
- Non-goals and excluded phases: Stage 2+; merge to `main`; Phase 8
- Exact starting commit/worktree: `bc45b63da41092175f7fbda97bc4c24f1f39bfe9` on `codex/bl-006-ies-associations`; review docs uncommitted and preserved
- Durable goal identifier/state: Cursor CreateGoal 2026-09-08 Stage 1 P1, active
- Implementation-readiness manifest: not used as item gate

## Environment and file-boundary preflight

| Check | Exact command/inspection | Result | Repository paths affected or required | Boundary disposition |
|---|---|---|---|---|
| Runtime discovery | `.venv\Scripts\python.exe --version`; `node --version` | Python 3.12.10; Node v24.19.0 | `.venv/`; Node 24 | inside |
| Locked dependency materialization | `Test-Path frontend\node_modules` | True | `frontend/node_modules` | inside; no lock edits |
| Build/test/lint/typecheck entry points | inspect `frontend/package.json` | test/typecheck/lint/build present | `frontend/package.json` | inside |
| Generated-artifact/validator entry points | Stage 1 presentation only | n/a | none | n/a |
| Browser/local-server/port requirements | `Get-NetTCPConnection` ports 3000,8000 | free | local UI/API | inside |

## Milestone and acceptance criteria

- Milestone being executed: M0 identity and reproduce
- Objective completion condition: HEAD is review SHA; four P1 code signatures confirmed on this checkout
- Evidence required: git identity + source inspection of clipping, rAF leak, card max-height

## Execution entries

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-08 Asia/Jerusalem | `git status --short --branch`; `git rev-parse HEAD`; `git merge-base --is-ancestor bc45b63da41092175f7fbda97bc4c24f1f39bfe9 HEAD` | `bc45b63` | branch `codex/bl-006-ies-associations`; HEAD equals review SHA; ancestor exit 0 | this log | preserved uncommitted review docs |
| 2026-09-08 Asia/Jerusalem | Source inspection of WA-01/02/03/04 | `bc45b63` | reproduced as code defects on this SHA (see below) | this log | Codex live measurements remain historical for the same SHA |

### M0 reproduction on this checkout

This HEAD **is** Codex’s reviewed commit. Live measurements in `harness/verify/2026-09-08-web-audit-observations.json` therefore apply to this tree. Current source still contains:

- WA-01: `.workspace` grid `278px minmax(320px, 1fr) 318px` without `width: 100%` / `minmax(0, …)` on columns; `html, body { overflow: hidden }` clips overflow. Toolbar `.brand { min-width: 252px }` with nowrap buttons.
- WA-02: `EngineeringMap.tsx` cleanup `cancelAnimationFrame(directionFrameRef.current)` without setting the ref to `null`; `schedule()` returns if the id is still stored. Same SHA previously showed 1 valid direction + 73 unavailable with no arrows/`?`.
- WA-03: `LightingPointLabels.tsx` identical cancel-without-null pattern.
- WA-04: `.lighting-result-card { max-height: min(220px, calc(100% - 24px)); overflow: auto }` and `LightingResultCard.tsx` never uses `.lighting-result-card-body`; disclaimers sit in the same clipped box.

Hypotheses treated as confirmed for the rAF leak (source) and card clipping (source+CSS). Layout overflow remains a CSS-constraint defect matching Codex’s 1920×855 measurement.

## Verification requirements

- Deterministic checks required for this milestone: identity + source inspection (complete)
- Source/hash/generated-artifact checks: no Input mutation
- Rendered/manual checks: live after patches
- Checks not run and reason: live browser at M0 deferred until servers started for post-fix verification on the same SHA’s defects

| 2026-09-08 Asia/Jerusalem | `corepack pnpm run test` after `vinext build` | dirty Stage 1 tree | 70 passed | terminal | SSR required dist |
| 2026-09-08 Asia/Jerusalem | `corepack pnpm run typecheck` | dirty Stage 1 tree | exit 0 | terminal | |
| 2026-09-08 Asia/Jerusalem | `corepack pnpm run lint` | dirty Stage 1 tree | exit 0 | terminal | |
| 2026-09-08 Asia/Jerusalem | `corepack pnpm run build` | dirty Stage 1 tree | exit 0 | terminal | MapLibre chunk-size advisory |
| 2026-09-08 Asia/Jerusalem | `.venv\Scripts\python.exe harness\verify\run_stage1_p1_live.py` | dirty Stage 1 tree | exit 0; hash_ok layout_ok card_ok | `harness/verify/2026-09-08-stage1-p1-live.json` | Starlette/httpx deprecation; arrow pixel sample inconclusive |
| 2026-09-08 Asia/Jerusalem | M1–M4 product patches | dirty Stage 1 tree | complete | CSS, scheduler, map/labels/card | Input/ unchanged |

## Close state

- Last verified milestone/state: M5 Stage 1 verify (implementer)
- Open blockers: none
- Durable goal state: complete pending UpdateGoal
- Next authorized action: independent QA / item-specific merge authorization; Stage 2+ still gated

