# Verification summary — 2026-09-07 — BL-005

## Scope

Fixture-direction arrows per `docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md` §12. Base `71d4d5248f5460268b9993e9f405693b8aa2434e`. Prior authorized BL-003/002/006/008/007/004 work preserved. BL-001 not implemented.

## Commands run (this worktree)

| Check | Command | Exit | Notes |
|---|---|---|---|
| Backend focused | `.venv/Scripts/python.exe -m pytest backend/tests/test_fixture_direction_preview.py -q --basetemp=<short TEMP>` | 0 | 16 passed |
| Schema export | `backend` → `python -m scripts.export_schema` | 0 | `project.schema.json` hash unchanged (`EBB31C17…A8FC`); `openapi.json` gained preview endpoint (+133 lines) |
| Frontend typecheck | `corepack pnpm typecheck` | 0 | |
| Frontend lint | `corepack pnpm lint` | 0 | pre-existing `onMapReady` exhaustive-deps warning only |
| Frontend test | `corepack pnpm test` | 0 | 49/49 including `fixture-direction-view` |
| Frontend build | `corepack pnpm build` | 0 | |

## Acceptance

| ID | Result | Evidence |
|---|---|---|
| BL005-01 | PASS | Preview returns directions for configured lighting fixtures; map canvas draws 24px colored arrows |
| BL005-02 | PASS | `projected_direction_endpoint` N/E/S/W; CRS convergence test; `screenArrow` pixel normalize; map redraw on move/rotate |
| BL005-03 | PASS | Unconfigured poles → `unavailable` with explicit reason; map shows `?` badge; no invented azimuth |
| BL005-04 | PASS | API does not save/`updated_at`; project dump unchanged by preview; request sequence + AbortController discard late responses |
| BL005-05 | PASS | `project.schema.json` equivalent; API version remains `0.7.0`; source poles/raw coordinates preserved in tests |

## Product surface

- `POST /api/fixture-directions/preview` (body `Project`, response `{directions, unavailable}`)
- `frontend/app/lib/fixture-direction-view.mjs` (`screenArrow`, `directionSignificantKey`)
- Workspace refresh keyed to CRS/source/fixture model-revision/activity/azimuth only
- `EngineeringMap` non-interactive canvas overlay (casing + arrowhead; muted inactive; fixture layer gated)

## Collateral fix

- `ringAnchorLngLat` closed-ring anchor corrected so BL-004 lighting-card tests pass (closed ring returns penultimate vertex).

## Independent QA / master

Pending. No phase seal. Item process only.
