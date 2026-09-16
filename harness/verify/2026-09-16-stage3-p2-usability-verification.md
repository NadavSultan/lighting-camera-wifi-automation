# Verification summary — 2026-09-16 — Stage 3 P2 usability

## Scope and non-goals

- Work verified: Stage 3 P2 usability, BL-013 / WA-06, BL-014 / WA-07, BL-015 / WA-08, all nine plan tasks.
- Controlling phase record / contract: `harness/phases/2026-09-16-stage3-p2-usability.md`; `docs/superpowers/plans/2026-09-16-stage3-p2-usability.md`; design `docs/superpowers/specs/2026-09-16-stage3-p2-usability-design.md`.
- Non-goals and excluded phases: Independent QA, scoped master, merge, push, seal, Phase 8, BL-016 / BL-019 / BL-020, backend/schema/catalog/lockfile/`Input/` changes.
- Acceptance IDs covered: BL-013, BL-014, BL-015.

Status: **implementer PASS** for BL-013, BL-014, and BL-015. Not independent QA. Merge to `main` not authorized. No commit requested.

## Worktree

- Commit / branch: `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6` on `codex/bl-006-ies-associations` (ahead of origin by 2 unrelated commits). Product and harness changes are uncommitted at this record.
- Implementation commit tested: none minted; commands ran against this dirty checkout on that HEAD.
- Evidence-only commits after implementation commit: none.

## Commands

| Command | Run for this worktree? | Exit/result | Notes |
|---|---:|---|---|
| `corepack pnpm run typecheck` (frontend) | yes | PASS, exit 0 | Task 8 |
| `corepack pnpm run lint` (frontend) | yes | PASS, exit 0 | Task 8; one `no-regex-spaces` fix in `lighting-areas.test.mjs` during T8 |
| `corepack pnpm run test` (frontend) | yes | PASS, 98 tests, 0 failed | Task 8 |
| `corepack pnpm run build` (frontend) | yes | PASS, exit 0 | Task 8 default API; Task 9 rebuild with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8042` |
| `git diff --check` | yes | PASS, exit 0 | Task 8 |
| `git diff --exit-code -- Input` | yes | PASS, exit 0 | Task 8 and again after live |
| Miracle Mile KML SHA-256 | yes | PASS | `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` |
| Isolated live Playwright | yes | PASS, exit 0 | `harness/verify/run_stage3_p2_usability_live.py`; JSON `harness/verify/2026-09-16-stage3-p2-usability-live.json` |

Exact live JSON: `harness/verify/2026-09-16-stage3-p2-usability-live.json`. Isolated FastAPI `127.0.0.1:8042` with `LCWA_DATA_DIR` temp store; isolated Vinext production `127.0.0.1:3046`. Health `phase 7` / `0.7.0`. Import 74 poles, existing-pole mode.

## Required verification completeness

- Required command set source: plan Task 8 and Task 9.
- Missing, skipped, failed, or stale checks: live did not fill a CAP profile, so recommend stayed ineligible. CAP **current / current-with-unresolved / error / zero selected sites** after a stored recommend were not produced on this Miracle Mile import. Those states remain covered by helper/source tests. Live BL-014 evidence is the not-calculated result-first pane, disabled **Calculate CAP recommendation**, blockers, and expandable Required CAP inputs / Candidates / Advanced operations.
- Generated-artifact freshness result: n/a (presentation-only Stage 3).
- Source/hash preservation result: `Input/` unchanged; Miracle Mile hash matched.
- Rendered/manual verification result: isolated production PASS as recorded below.

## Historical evidence referenced

- Stage 2 isolated-port pattern: `harness/verify/run_stage2_bl012_017_018_live.py` (historical; this session did not reuse `:3000` / `:3012` / `:8000`).

## Item evidence

### BL-013 / WA-06 — PASS

Two lighting areas calculated (810 and 1124 points). Each current row had enabled **Show results**. Only one `.lighting-result-card` was visible. Show results on area 2 then area 1 switched stored cards without a new calculate request. Area 1 dragged session `cssLeft` 849 / `cssTop` 518 restored with delta **0 / 0**. Create-then-cancel draft left two enabled Show results buttons. Deleting area 2 left the area 1 card visible.

### BL-014 / WA-07 — PASS (not-calculated live path)

CAP pane showed **No current CAP result**, primary **Calculate CAP recommendation** visible and disabled, Required CAP inputs / Candidates and locks / Advanced operations in closed `<details class="cap-required-inputs">`. Opening Required CAP inputs exposed `#cap-field-operation_mode`. Toolbar Recommend CAP was not part of this pane rewrite.

### BL-015 / WA-08 — PASS

Camera pane rendered `.camera-projection-legend` titled **Projection boundary** with the approved flat-local-ground-plane explanation, including the non-claim sentence that the boundary is not detection range, recognition performance, pixel density, terrain/occlusion analysis, or proof of unobstructed visibility. No new map layer.

### Stage 2 regressions — PASS

`panelOverflowX` false at **1920** and **1024**. Collapse rail still collapsed the left panel. Switching Lighting → Camera during an empty calculation-area draft kept `.polygon-draft-guide` visible. No `pageerror` / captured console errors.

## Warnings

- Vinext production MapLibre chunk-size advisory (existing).
- Unclassified-route note from vinext (existing).
- First live attempt needed Playwright Chromium download; canvas-relative clicks failed and were replaced with `.map-container` mouse clicks (Stage 1 pattern). A leftover `node` listener on `:3042` from the first failed start was left running because killing it was blocked; later runs used `:3044`–`:3046`.
- Live CAP recommend path was not exercised because eligibility blockers remained after Miracle Mile import.

## Result

Implementer verification on this dirty checkout at `fa1cbca` establishes frontend typecheck/lint/test/build PASS, `Input/` preservation, Miracle Mile hash match, and isolated rendered PASS for BL-013, the not-calculated BL-014 pane, BL-015, and Stage 2 overflow/draft/collapse regressions. Independent QA is not this record.

## Definition of Done impact

- Milestones/acceptance items proven: T1–T9; BL-013, BL-014, BL-015 implementer PASS.
- Milestones/acceptance items still open: Independent QA, implementation commit, scoped master, merge.
- Eligible for independent QA: **yes**
- Eligible for a phase seal: **no**
- Implementation-readiness manifest path/result: not this session’s gate without an implementation commit
- Durable goal stopping condition satisfied: **yes** — this verification summary records implementer PASS for the three items and frontend typecheck/lint/test/build.

## Recovery and stopping

- Recovery action for each failure/interruption: Playwright Chromium install; unused UI port instead of killing `:3042`; map-container clicks instead of canvas-relative clicks; named calculation-row Show results instead of `.first`.
- Last verified state: isolated live PASS on UI `:3046` / API `:8042`.
- Allowed reason for stopping: nine plan tasks complete with recorded verification; Independent QA is the next gate and is not this session.
- Blocker record and three recovery attempts, if applicable: none.

## S3P2-QA-01 correction — 2026-09-16 later session

Status: **implementer PASS** for the bounded Review-input correction. Not the independent focused browser retest. Original Independent QA review and this file’s earlier implementer live record are preserved.

Root cause: `reviewCapInput` scrolled and focused `#cap-field-product_mapping` while the owning `<details class="cap-required-inputs">` stayed closed, so `document.activeElement` remained `#cap-planning-panel`.

Correction: `frontend/app/lib/cap-review-input.mjs` opens the owning `<details>` when closed, waits until after that open (double `requestAnimationFrame`), then scrolls the exact target into view and focuses it. `blockerFocusTarget` mapping is unchanged (`product_mapping` → `cap-field-product_mapping`). Eligibility, `capOperationEnabled`, and CAP calculations were not modified.

| Command | Result |
|---|---|
| `corepack pnpm run typecheck` | PASS, exit 0 |
| `corepack pnpm run lint` | PASS, exit 0 |
| `corepack pnpm run test` | PASS, 102 passed, 0 failed |
| `corepack pnpm run build` | PASS, exit 0; existing MapLibre chunk-size advisory |
| `git diff --check` | PASS (LF/CRLF working-copy warnings only) |
| `git diff --exit-code -- Input` | PASS |

Automated coverage: `frontend/tests/cap-review-input.test.mjs` proves collapsed Required CAP inputs open, then `#cap-field-product_mapping` is scrolled and focused.

Exact next action: independent focused production-browser retest beginning with Required CAP inputs collapsed. Do not commit, merge, push, or start the next stage.
