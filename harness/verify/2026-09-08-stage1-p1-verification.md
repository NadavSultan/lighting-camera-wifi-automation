# Verification summary — 2026-09-08 — Stage 1 P1 display reliability

Status: **implementer PASS** for BL-009, BL-005 follow-up, BL-010, BL-011. Not independent QA. Merge to `main` not authorized.

Worktree: `codex/bl-006-ies-associations` descendant of review SHA `bc45b63da41092175f7fbda97bc4c24f1f39bfe9`. Starting HEAD was that SHA. Product changes are uncommitted at this record.

## Commands

| Check | Result | Notes |
|---|---|---|
| `corepack pnpm run test` (frontend) | PASS, 70 tests | after `vinext build` for SSR fixture |
| `corepack pnpm run typecheck` | PASS | |
| `corepack pnpm run lint` | PASS | |
| `corepack pnpm run build` | PASS | existing MapLibre chunk-size advisory |
| Miracle Mile KML SHA-256 | PASS | file and imported `source.file.sha256` = `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` |
| Fixture-direction preview (TestClient, one SMART pole) | PASS | 1 direction, 73 unavailable; source not mutated by preview |
| Live Playwright viewports 1920×855, 1440×855, 1366×768, 1024×768 | PASS | workspace/inspector/shell right edge = innerWidth; no document overflow-x |
| Live card computed `max-height` | PASS | `min(420px, 100% - 24px)`; 220px clip gone |
| Live arrow pixel sample after bulk UI apply | inconclusive | overlay canvases sized to the map; 2D pixel sample remained empty in headless Chromium. Scheduler unit tests prove canceled frames can draw again. Residual live MapLibre paint confirmation. |

Exact live JSON: `harness/verify/2026-09-08-stage1-p1-live.json`. Runner: `harness/verify/run_stage1_p1_live.py`.

## Item evidence

### BL-009 / WA-01

Constrained `.app-shell` / `.workspace` / `.topbar` to the viewport with `minmax(0, …)` columns and shrinking toolbar. Inspector remains in-panel scrollable. Live: 1920/1440/1366/1024 inspectorRight equals innerWidth (Codex had ~126 px overflow at 1920×855).

### BL-005 follow-up / WA-02

Source inspection confirmed `cancelAnimationFrame` without nulling the stored id. `frontend/tests/map-frame-scheduler.test.mjs` reproduces that leak and the `cancelMapFrame` repair. `EngineeringMap.tsx` now uses the shared scheduler, including `idle` after CAP easeTo. Colors and unavailable `?` drawing paths unchanged. Preview contract unchanged.

### BL-010 / WA-03

`LightingPointLabels.tsx` uses the same scheduler. Labels still use stored lux; calculation grid is not thinned. Live: label canvas width/height follow the map at every tested viewport.

### BL-011 / WA-04

Core metrics (Eavg, Emin, Emax, Emin/Eavg, Emin/Emax) sit in `.lighting-result-card-body` without the 220 px clip. Assumptions/disclaimers are in a collapsed `<details>` block.

## Out of scope (gated)

BL-012, BL-013, BL-014, BL-015, BL-016, BL-017, BL-018, BL-019, BL-020, BL-001 merge, `main` merge, Phase 8.

## Warnings

- Starlette/httpx TestClient deprecation warning (existing).
- Vinext production build MapLibre chunk-size advisory (existing).
- Playwright was installed into the local `.venv` for this live run only; it is not a product lockfile change.
