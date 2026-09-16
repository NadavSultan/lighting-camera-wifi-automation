# Execution log — 2026-09-16 — Stage 2 independent QA

Reviewed tracked tree `a0cf9ceae6f5097a12a858592b2ec249d988587c`, whose product tree is implementation commit `eb3a606253d794bf8ef685eb69d6c885368823ea`; post-implementation changes are documentation only. Untracked `.superpowers/` was preserved.

| Command / workflow | Exit/result |
|---|---|
| `git status --short --branch`; `git rev-parse HEAD` | branch correct; HEAD `a0cf9ce`; only pre-existing `.superpowers/` plus QA evidence untracked |
| `git merge-base --is-ancestor eb3a606... HEAD` | 0 |
| `git merge-base --is-ancestor 2f0f4a9... HEAD` | 0 |
| `corepack pnpm run typecheck` | 0 |
| `corepack pnpm run lint` | 0 |
| `corepack pnpm run test` | 0; 78 passed, 0 failed |
| `corepack pnpm run build` | 0; chunk-size and route-classification advisories only |
| isolated build with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8039` | 0 |
| `git diff --exit-code -- Input` | 0 |
| Stage 2 changed-path forbidden-scope scan | no backend, schema, catalog, `Input/`, or lockfile matches |
| `Get-FileHash Input/Miracle_Mile_Lighting_Poles.kml -Algorithm SHA256` | `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` |
| `git diff --check 2f0f4a9..eb3a606` | 2; two trailing-space lines in the Stage 2 plan only |
| isolated FastAPI `:8039`, isolated production Vinext `:3039`, isolated temp project store | both health HTTP 200; direct browser imported 74 poles and showed Lighting selected by default |

## Live recovery record

The independent automation used installed Chrome after the bundled Playwright Chromium was absent. Four materially different drawing-input strategies were attempted (ordinary locator click, forced locator click, page mouse click, synthetic canvas event). The map drawing guide intercepted near-edge pointer input or the synthetic path did not produce a calculable result. Direct in-app browser control then independently confirmed the isolated build/store identity, 74-pole import, switcher, default Lighting pane, Report Package toolbar action, and visible panel structure. The mandatory five-position BL-012 browser measurement matrix was therefore not completed; no product code was changed.

## S2-QA-01 continuation and closure

The existing partial JSON was preserved. The QA runner was corrected only in `harness/verify/run_stage2_independent_qa_live.py`; no product file changed. A fresh isolated FastAPI store and production Vinext process used ports `8039` and `3039`. The final runner exited 0 with `errors: []` and every `bl012_matrix_pass` field true.

| Probe | Measured result |
|---|---|
| Map stage / non-page origin | left `278`, top `58`, size `1324 × 767` |
| Top-left finish vertex → card | `(383.92, 184.555)` → `(395, 196)`; offset `(11.08, 11.445)`; inside |
| Top-right finish vertex → card | `(1496.08, 184.555)` → `(1274, 196)`; right-clamped; inside |
| Bottom-left finish vertex → card | `(383.92, 767.475)` → `(395, 651.5)`; bottom-clamped; inside |
| Bottom-right finish vertex → card | `(1416.64, 706.115)` → `(1274, 651.5)`; right/bottom-clamped; inside |
| Center finish vertex → card | `(940, 476.015)` → `(952, 488)`; offset `(12, 11.985)`; inside |
| Drag | card moved from `(952, 488)` to `(1082, 558)` and remained inside |
| Reset | returned exactly to `(952, 488)` |
| Pan/zoom | anchored card moved from `(952, 488)` to `(819.594, 411.297)` |
| Collapse / restore | map left/width `278/1324` → `42/1560` → `278/1324`; card stayed inside and restored with the map |
| Session-only position | no `draggedPosition`, `dragged_position`, `cardPosition`, or `card_position` key in API project JSON; all project fields except unrelated asynchronous `camera_geometry` were equal before/after drag |

Screenshots: `top_left.png`, `top_right.png`, `bottom_left.png`, `bottom_right.png`, `center.png`, `center-interaction.png`, and `drag-reset.png` under ignored `harness/tmp/stage2-independent-qa/screenshots/`. Final evidence: `harness/verify/2026-09-16-stage2-bl-012-017-018-independent-qa-live.json`.
