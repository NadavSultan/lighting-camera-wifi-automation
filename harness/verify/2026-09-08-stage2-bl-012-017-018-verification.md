# Verification summary — 2026-09-08 — Stage 2 BL-012 / BL-017 / BL-018

Status: **implementer PASS** for BL-012, BL-017, and BL-018. Not independent QA. Merge to `main` not authorized. Stage 3 not started.

Worktree: `codex/bl-006-ies-associations` at base `2f0f4a9c42a3a7bdbb51971591aaced5c57a8d38`. Product and harness changes are uncommitted at this record (commit not requested).

Durable goal: Cursor CreateGoal activated this session — complete the three items with recorded verification on this checkout. Stopping condition met.

## Commands

| Check | Result | Notes |
|---|---|---|
| `corepack pnpm run typecheck` | PASS | exit 0 |
| `corepack pnpm run lint` | PASS | exit 0 |
| `corepack pnpm run test` | PASS, 78 tests, 0 failed | includes new card-offset, lux-policy, and left-panel tests |
| `corepack pnpm run build` | PASS | existing MapLibre chunk-size advisory; unclassified-route note |
| Miracle Mile KML SHA-256 | PASS | `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` |
| Live Playwright (reused production UI `127.0.0.1:3012`, API `127.0.0.1:8000`) | PASS | import 74 poles; switcher; overflowX; card-to-vertex offset |

Exact live JSON: `harness/verify/2026-09-08-stage2-bl-012-017-018-live.json`. Runner: `harness/verify/run_stage2_bl012_017_018_live.py`.

## Lux display policy (BL-017)

Applied everywhere illuminance is shown (lighting card, map labels, left-panel area summaries):

| Stored value | Display |
|---|---|
| exact `0` | `0.00` on labels; `0.00 lx` on card and area summaries |
| `null` / non-finite / negative | `—` (no unit) |
| `0 < x < 0.01` | `<0.01` on labels; `<0.01 lx` on card and area summaries |
| `x >= 0.01` | two-decimal `toFixed(2)`; card/summaries append ` lx` |

Uniformity ratios still use stored numbers (`toFixed(3)`), never formatted lux strings. Stored lux is not rewritten. Card `title` attributes expose the full stored number. Map labels omit the unit suffix to keep point density; the numeric threshold policy is the same.

## Item evidence

### BL-012 / WA-05 — PASS

Coordinate chain was measured against the 2026-09-08 review numbers before patching. MapLibre `project()` is container-relative; the card is `position:absolute` in `.map-stage`, which shares origin with the map container (`inset: 0`). Subtracting `container.left/top` reconstructs the recorded card at viewport `(286, 459)` after clamp. The repair uses `cardOffsetFromProjected` (projected + 12 px) and does not subtract the viewport origin.

Live (map stage origin `(278, 58)`, not page `(0,0)`): finish-vertex click `(873.8, 487.5)`; card `(885, 499)`; offset **11.2 / 11.5 px**; `cssLeft` 607 not clamped to the 8 px margin. Reset returned to the same anchored position. Dragged position remains session overlay state, not project JSON.

### BL-017 / WA-10 — PASS

`formatLux` / `formatLuxWithUnit` implement the policy above. Tests cover exact 0, WA-10 tiny positives (`0.0000359329` → `<0.01 lx`), ordinary values, and null. Card and left-panel summaries call `formatLuxWithUnit`; labels use `formatLux` on stored `maintained_horizontal_illuminance_lux`. Live calculation without IES showed exact **`0.00 lx`** and null ratios as **`—`**. A live tiny-positive grid was not produced in this polygon (no IES contribution); the WA-10 numeric case is covered by tests.

### BL-018 / WA-11 — PASS

Left panel has a Lighting / Camera / Wi-Fi / CAP switcher. New/open/import sets Lighting. CAP Planning toolbar switches to the CAP pane; Report Package remains a toolbar action and still opens `#report-package-panel` without a shell rewrite. CAP blockers and required inputs remain in the CAP pane (`<details open>` for required profile fields). Discipline panes stay mounted (`hidden`) so polygon drafts are not discarded by switching. Live: after open, Lighting selected and lighting areas visible; CAP pane showed `#cap-planning-panel`; `panelOverflowX` false at **1920 and 1024**; `overflow-x: hidden` on `.panel-scroll`; collapse rail still works.

Residual: inner `scrollWidth` can still exceed client width for long report/layer labels; horizontal scrolling is disabled. That does not reverse overflowX false.

## Out of scope (gated)

BL-013, BL-014, BL-016, BL-019, BL-020, OBS-01, merge, push, Phase 8, Stage 3, engines/schemas/`Input/`/catalogs/lockfiles.

## Warnings

- Vinext production build MapLibre chunk-size advisory (existing).
- Unclassified-route note from vinext (existing).
- Live UI reused an already-running production server on port 3012 that contained the Stage 2 switcher build; API was the existing `127.0.0.1:8000` health `phase 7` / `0.7.0`.
