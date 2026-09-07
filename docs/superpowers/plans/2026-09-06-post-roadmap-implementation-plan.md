# Post-roadmap implementation plan for Cursor

**Prepared:** 2026-09-06. **Status:** proposed execution plan; no implementation performed or authorized by this document alone.

**Goal:** Make existing engineering workflows easier to draw, configure, inspect and understand, then add an optional satellite background.

**Architecture:** Deliver eight independent backlog items in sequence. Reuse the accepted calculation, catalog and persistence services. Keep new presentation state out of saved engineering data; introduce a narrowly scoped read-only direction-preview API only where projected-coordinate correctness requires it.

**Stack:** Python 3.12, FastAPI, Pydantic, PyProj; React/TypeScript, MapLibre, Node 24 and the existing locked pnpm dependencies.

**Requirements:** `docs/post-roadmap-backlog.md`. **Observed evidence:** `harness/verify/2026-09-06-backlog-live-reproduction.md` and its companion observations JSON. Paths in this document are relative to the repository root, regardless of computer or operating system.

**Agent instructions:** Follow this repository's `AGENTS.md` and execution records. This plan is self-contained and does not require Codex, a Codex plugin, or an external skill to run in Cursor. Work one authorized item at a time, using the checkboxes below. Proposed helper names and new files are design specifications, not claims that they already exist.

## 1. Start here on another computer

Repository: https://github.com/NadavSultan/lighting-camera-wifi-automation

Reviewed application baseline: `8751714003bf09f39c217a5f26b9fd6056d2927b` on `main`. The prior computer happened to have two nested repositories; that nesting is not required. On the new computer, use a normal checkout with `AGENTS.md`, `backend`, `frontend`, `docs` and `harness` at its root.

1. Clone or update the repository from its configured remote. Preserve any existing uncommitted work. Never reset, clean, or stash another person's changes automatically.
2. Use the plan, backlog and evidence files already present in the updated repository. If using the optional offline handoff ZIP instead, copy its documentation into the matching repository-relative paths. If a destination already exists with different contents, compare versions and preserve both before reconciling; do not overwrite newer work blindly.
3. Read the ten startup documents in the order required by `AGENTS.md`, then the backlog, reproduction report, and this plan. Dated gate records control accepted scope; historical reports contain wording that was true when written.
4. Inspect `git status --short --branch`, `git rev-parse HEAD`, `git diff`, and the fetched remote. Verify the reviewed baseline is an ancestor. If newer product commits exist, inspect their changes and update the affected task assumptions before execution. Do not roll back newer accepted work.
5. Confirm which backlog IDs the user authorized Cursor to implement. Preparing or copying this plan is not blanket implementation approval.
6. If the handoff documents are already committed, use that documentation commit as part of the starting history. Otherwise preserve/import them in a documentation-only commit. Then create an isolated `codex/bl-003-polygon-feedback` branch/worktree for the first authorized task. For later tasks, use corresponding `codex/bl-006-ies-associations`, `codex/bl-002-wifi-visibility`, `codex/bl-008-cap-workflow`, `codex/bl-007-lux-labels`, `codex/bl-004-lighting-window`, `codex/bl-005-fixture-arrows`, and `codex/bl-001-satellite-background` branches. Start each from the accepted predecessor, not from an unreviewed parallel modification of the same map file.

### Suggested instruction to give Cursor

The following is a reusable user instruction. It only becomes authorization when the user actually sends it to the executing agent:

> Read AGENTS.md and its startup documents, then docs/post-roadmap-backlog.md and docs/superpowers/plans/2026-09-06-post-roadmap-implementation-plan.md. I authorize BL-003, BL-006, BL-002, BL-008, BL-007, BL-004 and BL-005 within the proposed designs and file boundaries in that plan, in that order. Execute one item at a time and record its verification before proceeding. Preserve source data and all accepted phase contracts. Do not implement BL-001 until I select and authorize an imagery provider, and do not fix the separate OBS-01 finding without separate authorization. Do not create Phase 8. Do not merge or claim acceptance without the required review decisions.

The user may authorize only BL-003 instead. Do not infer approval of the other items from approval of the first.

## 2. Recommended order and independent scope

| Order | ID | Deliverable | Why here | Main dependency |
|---|---|---|---|---|
| 1 | BL-003 | Visible polygon vertices, outline and drawing guidance | Reproduced defect affects basic input | None |
| 2 | BL-006 | Per-file multi-model IES associations | Makes lighting configuration understandable | Existing many-to-many API |
| 3 | BL-002 | Obvious action to show conceptual Wi-Fi | Small improvement to a working calculation | Current Wi-Fi results |
| 4 | BL-008 | Clear CAP entry, prerequisites, count and sites | High-priority workflow confusion | Existing CAP engine; no algorithm change |
| 5 | BL-007 | Lux values beside calculation points | Makes lighting output readable | Current maintained-lux results |
| 6 | BL-004 | Compact draggable lighting-results card | Builds on readable lighting output and drawing lifecycle | BL-003 integration; existing result statistics |
| 7 | BL-005 | Direction arrow for each configured fixture | Requires careful grid-north/display conversion | Projected metre CRS; explicit fixture azimuth |
| 8 | BL-001 | Standard/Satellite background selector | External-provider decision; verify every overlay over imagery | Provider authorization and all prior map checks |

This order is a recommendation, not a new numbered phase. Each item must remain independently reviewable. Do not bundle unrelated refactoring or OBS-01 into these changes.

## 3. Proposed design decisions

These decisions make the plan concrete. They become binding for execution only when the user approves the applicable item/design.

| Topic | Proposed choice | Contract consequence |
|---|---|---|
| Wi-Fi visibility | Show a prominent explicit “Show coverage on map” action after calculation; preserve default-off until clicked | Preserves Phase 5 toggle rule |
| IES assignments | Show all models per file, grouped by family, with independent association controls; no automatic assignment | Preserves supplied-file family restrictions and pins |
| Polygon drawing | Visible first point, open committed line, separate dashed cursor preview, fill after three points, map-local finish/cancel guidance | Retains existing validation and separate area collections |
| CAP presentation | Dedicated accessible panel with result summary first and inputs grouped beneath; explicit “Show selected sites on map” action | Preserves blockers, permissions, candidate pool and map-toggle semantics |
| Lux labels | Non-interactive canvas labels, all visible points eligible, values in lx; no hover-only substitute or silent thinning | No calculation/schema changes |
| Lighting card | One open card for the selected result, per-area session position, anchored near last placed vertex until first drag | No persisted window fields or schema migration |
| Direction arrows | Read-only display; use a metre-CRS direction segment transformed back to display coordinates | Adds an API display preview; does not change azimuth conventions |
| Satellite | Session-only choice; Standard remains available; provider configuration is separate from project JSON | Provider-specific authority remains required |

Alternative choices that are deliberately not included: auto-enabling Wi-Fi, inferring IES compatibility, replacing CAP algorithms, persistent window positions, hiding point labels by zoom, or using an unverified public imagery endpoint. If requested later, record the new decision and revise the relevant boundary before implementing it.

## 4. Invariants and execution records

- Existing-pole mode remains mandatory. No customer pole generation, movement, redistribution, optimization or deletion. Display endpoints and cursors are transient graphics, never source poles.
- Preserve original uploads byte-for-byte, exact source coordinates/raw text, immutable catalog revisions and frozen Phase 1 catalogs at `1.0.0`.
- Keep source, edits, calculations and recommendations separate. Do not mutate backend results to make the UI convenient.
- WGS84 is display/interchange only. Grid-north fixture azimuth is clockwise from the project projected CRS north; do not substitute geographic north or a camera-slot direction.
- Preserve LITE red, WIFI yellow, SMART blue, and distinct CAP/priority-area colors.
- No new RF, compliance, professional-validation, installation, capacity or optimality claims. Do not change lighting equations, Wi-Fi geometry or CAP objectives.
- No Phase 8, no reissued phase seal, and no edits to historical QA evidence to conceal changes.
- No dependency upgrades or lockfile edits. `frontend/package.json` may change only its test command as described below until separately authorized. New third-party services/dependencies need a concrete decision.
- Evidence files are added, never substituted for historical checks. Every recorded pass needs command, exit status, tested commit/worktree, output/warnings and acceptance IDs.

### Item records and gates

Before product edits, create `harness/phases/YYYY-MM-DD-bl-003-work-record.md` (or the current item ID) from the existing work-record template. Link this task section and the backlog; record scope, non-goals, exact base, starting diff, file boundary, environment preflight, milestones and acceptance IDs. A suggested objective is “Deliver BL-003 criteria BL003-01 through BL003-04, verified on a recorded implementation commit and ready for independent review.”

If the execution environment has a durable goal mechanism and the authorized workflow requires it, activate it and record its actual identity; do not pretend Cursor has a Codex tool. If that mechanism is unavailable, state that fact and use the repository's durable work record and execution log without falsely claiming a platform goal exists.

Use `harness/logs/YYYY-MM-DD-bl-003-execution.md` for exact commands and results, and `harness/verify/YYYY-MM-DD-bl-003-verification.md` for acceptance evidence. Repeat with the applicable ID. Independent review uses the repository QA-review template and is separate from the implementer's self-checks. Obtain a scoped master decision before merging/accepting an item; follow explicit user authorization on who may make that decision.

**Readiness-verifier limitation discovered during planning:** `harness/verify/verify_phase_readiness.py` requires a numeric phase and rejects a present phase seal. It cannot truthfully validate `BL-003` as written. Do not supply “08”, repurpose a closed phase, delete a seal, or edit the verifier as a workaround. The proposed post-roadmap process is the item acceptance matrix, recorded commands, clean implementation handoff, independent QA and scoped master decision. Approval of this plan must explicitly adopt that item process; if the user's controlling instructions require the old phase verifier for these items, resolve a separately authorized harness adaptation before product implementation.

## 5. Preflight and verification commands

Run from the actual checked-out repository; do not reuse the old computer's absolute paths. On Windows use the commands below. On other operating systems use `.venv/bin/python` in place of `.venv/Scripts/python.exe` and the local shell's environment syntax.

```powershell
git status --short --branch
git rev-parse HEAD
git diff
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r backend/requirements.lock
Set-Location frontend
pnpm install --frozen-lockfile
pnpm run typecheck
pnpm run lint
pnpm run build
pnpm run test
Set-Location ..
.venv/Scripts/python.exe scripts/validate_engineering_data.py
```

Create the virtual environment only if absent; do not replace a working environment. Discover Python/Node/pnpm first and use the approved package-manager setup if a command is unavailable. Record lock hashes before/after materialization. `frontend/pnpm-workspace.yaml` already permits esbuild and denies sharp/workerd builds; preserve its current policy. Do not run database generation.

The existing frontend rendered tests import `dist/server/index.js`; build **before** the full test suite. For new helper tests, BL-003 changes the test script to `node --test tests/*.test.mjs`, retaining the existing rendered suite. Focused helper tests can run directly before a production build.

For backend tests, run from `backend` with an isolated, newly named pytest temp directory. Pytest may clear its basetemp directory: use a unique run name, never a customer-data directory or a reused directory containing evidence.

```powershell
Set-Location backend
$backlogRun = [guid]::NewGuid().ToString('N')
../.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp "../harness/tmp/pytest-$backlogRun"
Set-Location ..
git diff --check
```

For an API/model change (BL-005), regenerate from `backend` with `../.venv/Scripts/python.exe -m scripts.export_schema`, inspect the exact generated diff, then run the backend suite again with another unique temp directory. Project schema must remain unchanged for the proposed read-only preview; OpenAPI may gain the new endpoint and response definitions. Record the software/API version decision before changing metadata; do not invent a project schema bump for a display-only endpoint.

### Browser verification

Run a production frontend built with an isolated API URL. Example environment setup, in two terminals, after confirming ports are free:

```powershell
# Terminal A, repository root
$env:LCWA_DATA_DIR = Join-Path (Get-Location) 'harness/tmp/item-browser/projects'
$env:LCWA_CATALOG_DIR = Join-Path (Get-Location) 'harness/tmp/item-browser/catalogs'
Set-Location backend
../.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8048
```

```powershell
# Terminal B, repository root
$env:NEXT_PUBLIC_API_URL = 'http://127.0.0.1:8048'
Set-Location frontend
pnpm run build
pnpm run start --port 3048
```

Use the address actually reported by the frontend; in the diagnostic session `localhost:3048` worked while `127.0.0.1:3048` did not. Do not stop an unrelated process or change firewall settings to free a port. Choose unused ports and rebuild the frontend with the matching API URL when necessary.

Import the supplied KML into isolated storage, configure explicit test fixture models/height/IES, and perform the real UI interactions below. Inspect screenshots, console and actual saved/API data; source-string tests alone are not sufficient. Record the runtime, viewport, input hashes, expected/observed behavior and screenshots in an item-specific evidence directory. Stop only the servers started for the check.

## 6. Task 1 — BL-003: visible polygon feedback

**Current finding:** first/second lighting clicks increment the count without visible geometry; fill appears after the third. Other draft tools use the same fill-only approach but were not live-tested.

**Files:** Modify `frontend/app/components/EngineeringMap.tsx`, `EngineeringWorkspace.tsx`, `frontend/app/globals.css`, and `frontend/package.json` test script only. Create `frontend/app/lib/polygon-draft.mjs`, `polygon-draft.d.mts`, and `frontend/tests/polygon-draft.test.mjs`. No backend or saved-model changes.

**Interface:** `buildPolygonDraft(points, cursor)` consumes arrays of `[longitude, latitude]` and an optional cursor coordinate. It returns `{ vertices, edges, fill, preview }`, each a GeoJSON FeatureCollection. The helper must never mutate its inputs. One Point feature per placed vertex; edges are an open LineString only from two points; fill is a closed Polygon only from three; preview is only the segment from the last vertex to a distinct cursor. Preview must not be included in the saved ring.

- [ ] Add the helper test and execute `node --test tests/polygon-draft.test.mjs` from `frontend`, recording the expected pre-implementation failure. Representative required test:

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { buildPolygonDraft } from '../app/lib/polygon-draft.mjs';
test('one placed point is visible without inventing a saved edge', () => {
  const input = [[-80.26, 25.75]];
  const draft = buildPolygonDraft(input, [-80.259, 25.751]);
  assert.equal(draft.vertices.features.length, 1);
  assert.equal(draft.edges.features.length, 0);
  assert.equal(draft.fill.features.length, 0);
  assert.equal(draft.preview.features.length, 1);
  assert.deepEqual(input, [[-80.26, 25.75]]);
});
```

- [ ] Implement the GeoJSON transformation and declaration. Add cases for zero, two and three points, duplicate cursor/last point, unchanged input, and preview disappearance on cancel. Reuse existing coordinate validity rules; do not replace polygon validation.
- [ ] Replace draft fill-only registration with vertices, line, fill and preview sources/layers for each active tool. Use 4 px colored edges over a 6 px contrasting casing, 5 px vertex circles, a distinct larger last vertex, 2 px dashed preview and low-opacity fill. Keep current tool color distinctions. Clean up listeners and sources through the existing map lifecycle.
- [ ] Track cursor coordinates transiently on map movement while drawing; clear on leave/cancel/finish. Add a map-local panel saying “Click to add the first point”, then “Click to add the next point”, then “Add another point or finish polygon”. Show vertex count and Finish/Cancel; Finish calls the existing validation/save handler and is disabled below three points. Do not bypass fields already required by each tool. Use pointer isolation so clicking the panel cannot append a map vertex.
- [ ] Preserve original saved geometry until a valid replacement is committed. Clear only the active draft on cancel. A map click during drawing must not also select an unrelated area/fixture.
- [ ] Run helper tests and frontend checks, then perform the browser matrix and commit the bounded implementation/evidence separately.

**Acceptance:** BL003-01: visible feedback at 0/1/2/3 points in all three tools. BL003-02: cursor segment and finish/cancel guidance are visible on the map. BL003-03: cancel/invalid redraw never replaces saved rings or source data. BL003-04: pan/zoom/selection and successful save/reopen remain usable.

**Browser matrix:** Each tool: first click, second click, third click, mouse movement, invalid crossing, cancel, redraw-existing, valid save and reopen. Test bright/dark map regions and narrow viewport. Verify point clicks use original map coordinates; no snapping or new closure semantics.

## 7. Task 2 — BL-006: clear IES assignments

**Current finding:** the supplied Phoenix 100 W file retained three associations; the UI only exposes one pair at a time.

**Files:** Modify `frontend/app/components/CatalogManager.tsx`, `frontend/app/globals.css`; create `frontend/app/components/IesAssociations.tsx`, `frontend/app/lib/ies-association-view.mjs`, its `.d.mts`, and `frontend/tests/ies-association-view.test.mjs`. Existing `frontend/app/lib/api.ts` changes only if needed for readable per-control errors. Backend catalog policy stays unchanged.

**Interface:** `associationRows(fileId, fixtureModels, associations)` returns one row per explicit model, preserving model ID/family/type/display name and an `associated` boolean from active pair records. It does not compute compatibility or create defaults. The component receives these rows and async add/remove callbacks to the existing endpoints.

- [ ] Write a test that supplies one file with three active Phoenix pair records and asserts three checked rows; adding/removing a different file's association must not affect them. Include absent/inactive pairs and duplicate-safe model IDs.

```javascript
const models = ['lite', 'wifi', 'smart'].map(variant => ({
  id: `phoenix-1-${variant}`, fixture_family: 'Phoenix 1', capability_variant: variant.toUpperCase(),
  display_name: `Phoenix 1 ${variant.toUpperCase()}`
}));
const pairs = models.map(model => ({
  ies_file_id: 'ies-a', fixture_model_id: model.id, active: true
}));
assert.deepEqual(
  associationRows('ies-a', models, pairs).filter(r => r.associated).map(r => r.id).sort(),
  ['phoenix-1-lite', 'phoenix-1-smart', 'phoenix-1-wifi']
);
```

These fixtures contain the fields consumed by the view helper. The helper must not infer associations from family/type labels. Do not mock an API that silently drops prior pairs.

- [ ] Render a visible “Assigned models” section inside each IES row, grouped by model family. Show all LITE/WIFI/SMART model choices with full labels. A checkbox change performs one explicit existing association API operation; disable that control while pending and refresh authoritative catalog state after success or failure.
- [ ] Display saved associations from API responses, not optimistic guesses. A rejected cross-family action keeps the previous checkbox state and shows the backend's readable error. Do not duplicate the supplied-file hash allowlist in the frontend. Invalid/inactive files cannot gain active associations.
- [ ] Keep “Set default” separate and explicit. Never adopt a new IES revision into an already configured pole automatically. Remove the misleading single-pair presentation only after all its actions have equivalents.
- [ ] Run new helper tests, frontend checks and `backend/tests/test_phase2_catalogs.py` plus `backend/tests/test_phase4_lighting_calculation.py` for unchanged compatibility policy. Browser-test three additions, remove one, reload, pole selection for all three variants, rejected supplied cross-family association, and invalid file.

**Acceptance:** BL006-01: one file shows three simultaneously saved compatible assignments. BL006-02: one removal preserves the others. BL006-03: invalid/family restrictions and source hashes remain intact. BL006-04: defaults/pins change only through their separate explicit actions.

## 8. Task 3 — BL-002: make Wi-Fi visible by an obvious action

**Current finding:** calculation succeeds while the coverage layer stays off; enabling the checkbox displays the circle.

**Files:** Modify `EngineeringWorkspace.tsx`, `EngineeringMap.tsx`, `frontend/app/globals.css`; create `frontend/app/components/WifiMapSummary.tsx`, `frontend/app/lib/wifi-map-state.mjs`, its `.d.mts`, and `frontend/tests/wifi-map-state.test.mjs`.

**Interface:** `wifiMapState(result, visible)` returns a presentation state `not-calculated`, `empty`, `hidden`, or `visible`; classification uses the presence of current result data and its circle count. Existing invalidation removes stale results; do not recreate them in a UI helper.

- [ ] Test null result, zero circles, one hidden circle and one visible circle as four distinct states. A null result with an old visibility flag must remain `not-calculated`.
- [ ] After successful calculation show a compact map-adjacent summary: “1 conceptual coverage circle calculated — hidden on map” plus “Show coverage on map”. Clicking it sets the existing `layer_state.wifi_coverage` to true through the normal edit/history path; retain the existing checkbox in sync. Do not enable automatically.
- [ ] Add a dedicated cyan circle outline with contrasting casing so coverage extents are clear. Keep the fill low enough to see fixtures and existing colors. Do not change the stored circles, radius, overlap calculations or eligibility.
- [ ] Keep covered-area statistics available in an expandable section beneath the visual summary; retain all accepted values and the explicit no-analysis-area message. Zero results explain that no eligible enabled WIFI/SMART fixtures produced circles; don't show a useless Show action.
- [ ] Run helper/frontend checks and the Phase 5 backend tests. Browser-test no analysis polygon, overlapping circles, layer off/on, zero/ineligible fixtures, changed radius, stale invalidation, undo/redo and save/reopen.

**Acceptance:** BL002-01: calculation offers a clear explicit display action. BL002-02: all current circles appear at their recorded extents. BL002-03: no-area/empty/stale states are clear. BL002-04: statistics, disclaimers, source data and default-off contract remain intact.

## 9. Task 4 — BL-008: CAP workflow and result clarity

**Current finding:** recommendation executes, but prerequisites are a dense raw-name list, the count is below a long form and site layers remain hidden. OBS-01 duplicate-key console messages are separate; do not silently include their correction.

**Files:** Modify `EngineeringWorkspace.tsx`, `EngineeringMap.tsx`, `frontend/app/globals.css`; create `frontend/app/components/CapPlanningPanel.tsx`, `frontend/app/lib/cap-workflow-view.mjs`, its `.d.mts`, and `frontend/tests/cap-workflow-view.test.mjs`. Reuse `phase6-cap-workflows.mjs` blocker/permission functions. No CAP-service/model/schema changes.

**Interfaces:** `capResultSummary(project)` returns `{ state, selectedIds, unresolvedIds }` where state is `not-calculated`, `current`, `current-with-unresolved`, or `error`; it uses `cap_calculations.status`, current result identity and `cap_recommendations.selected_candidate_ids`. The panel receives existing action callbacks and `onFocusCandidate(candidateId)`; the map resolves that ID to the already stored candidate location and pans without changing it.

- [ ] Test initial, successful, unresolved and error states. Ensure selection length comes from selected IDs, not candidate-pool size; unresolved IDs come from `result.unresolved_node_ids`. A removed/invalidated result must not keep its prior count labeled current.
- [ ] Add a visible “CAP Planning” entry near existing toolbar actions which opens/focuses a dedicated panel. Keep a clearly labeled Recommend action within it. Structure the panel as current result summary, prerequisites, candidates/locks, and advanced topology/provenance. Reuse current input controls/handlers by extracting their CAP block only; do not rewrite the entire workspace.
- [ ] Map blocker keys to readable labels and focus targets: product, variant, band/jurisdiction, link distance, node/child/hop limits, appliance/fixture counting, redundancy, each fixture-type node policy, mode permission and candidate feasibility. Keep unknown values unknown; a “Review input” action focuses the relevant existing control. Do not convert missing engineering authority into an assumed default.
- [ ] Explain actions beside their buttons: “Calculate / rank: inspect candidate ranking”, “Validate: check your explicit selection”, “Recommend: choose from the approved candidate pool”. Preserve all current operation-mode/permission checks and surface backend errors without mutating input provenance.
- [ ] On success bring the summary into view: “Recommended CAP units: N”, selected-site rows with candidate ID, human-readable pole name or manual-site label, and unresolved-node count. Offer “Show selected sites on map”; clicking enables the existing CAP layers and focuses their bounds. Individual “Locate” actions highlight the selected ID and pan to its location. Do not label an incomplete result an installation-ready answer.
- [ ] Handle no result, no candidate, prohibited pool, unresolved nodes, rejected operation, stale change, and current zero selection distinctly. Retain warnings and conceptual limitations next to the summary, with detailed provenance expandable.
- [ ] Run helper/frontend checks and Phase 6 tests. Production browser-test fresh unknown state and explicit test-only profile, multiple candidates, locks/prohibition, recommend, validation, map/list navigation, changed inputs, undo/redo and reopen. Compare rendered counts/IDs to API responses.

**Acceptance:** BL008-01: entry and next step discoverable. BL008-02: blockers explain both reason and input location. BL008-03: count/list/map agree with the current result. BL008-04: operations, constraints, provenance and invalidation remain unchanged. BL008-05: no fixture movement, inferred candidates or operational approvals.

If OBS-01 recurs, retain exact console evidence. A new visual regression introduced by this task must be fixed within scope; an unrelated pre-existing warning requires separate disposition, not an unsupported zero-error pass or a covert scope expansion.

## 10. Task 5 — BL-007: numeric illuminance labels

**Files:** Modify `EngineeringMap.tsx`, `frontend/app/globals.css`; create `frontend/app/lib/lighting-labels.mjs`, its `.d.mts`, `frontend/app/components/LightingPointLabels.tsx`, and `frontend/tests/lighting-labels.test.mjs`.

**Interface:** `formatLux(value)` consumes a nonnegative finite maintained-lux value; returns two decimals for zero or values at least 0.01, two significant digits for smaller positive values, and `—` for missing/invalid values. `LightingPointLabels` receives current result points and the live map reference, renders a pointer-transparent high-DPI canvas aligned with the map, and never writes project data.

- [ ] Write and run numerical-format tests before implementation:

```javascript
assert.equal(formatLux(0), '0.00');
assert.equal(formatLux(12.345), '12.35');
assert.equal(formatLux(0.00123), '0.0012');
assert.equal(formatLux(null), '—');
assert.equal(formatLux(Number.NaN), '—');
```

- [ ] Format only `maintained_horizontal_illuminance_lux`. Retain exact values in persisted results. Include a map legend “Point values: maintained illuminance (lx)”; don't confuse direct/initial and maintained values.
- [ ] Draw numeric labels adjacent to every point in the viewport while its calculation-point layer is enabled. Use a contrasting text halo and device-pixel-ratio scaling. Composite area ID and point ID for identity. Use the same map projection as the points. Listen to map move/resize/data changes, coalesce drawing with requestAnimationFrame and unsubscribe on unmount. Avoid thousands of DOM markers and any external font dependency.
- [ ] Retain color visualization; pointer events pass through to the map. No collision-based omission, hidden-at-low-zoom policy, sampling or tooltip-only replacement. Dense labels may overlap at overview scale: provide “Zoom in to separate point values” without hiding values. If the approved maximum dataset cannot remain usable, record measured results and request a scoped product decision rather than silently reducing point count.
- [ ] Test helper/frontend checks; browser-test one known grid, two overlapping areas, zero and small positive lux, 25,000-point supported-area limit, zoom/rotation/resize, layer toggles and invalidation. Compare the small known-grid labels one-for-one with API results; record timing/interaction observations for the large case.

**Acceptance:** BL007-01: each displayed point has a value, not just color. BL007-02: values/units match maintained results and preserve precision in storage. BL007-03: labels track map motion without blocking interaction. BL007-04: stale/deleted points and labels disappear together.

## 11. Task 6 — BL-004: draggable lighting-results card

**Files:** Modify `EngineeringWorkspace.tsx`, `EngineeringMap.tsx`, `frontend/app/globals.css`; create `frontend/app/components/LightingResultCard.tsx`, `frontend/app/lib/lighting-card-position.mjs`, its `.d.mts`, and `frontend/tests/lighting-card-position.test.mjs`.

**Interfaces:** `clampCard({x,y,width,height}, viewport, margin=8)` returns a position fully inside the viewport where possible. Card props consume the selected area's existing result and callbacks for close/position changes. Workspace holds session-only `{areaId: {anchorLngLat, draggedPosition}}` and the open result area ID.

- [ ] Test offscreen placement and small viewport behavior, e.g. a 280×180 card requested at `(900,700)` in an 800×600 viewport clamps to `(512,412)` with an 8 px margin. Test resize and negative coordinates; the component uses `max-width`/`max-height` and internal scrolling when the available viewport is smaller than the card.
- [ ] When a valid drawing is saved, capture the last placed vertex before the draft array is cleared, keyed to the saved area ID. This is the proposed interpretation of “where I finish drawing”. For a reopened area with no session history, use the final non-closing vertex of its stored ring. Never change the saved ring to preserve a UI anchor.
- [ ] After a successful Calculate Lighting response, open one compact card for that area near its anchor plus a 12 px offset. Show area name, Eavg/Emin/Emax in lx, Emin/Eavg and Emin/Emax explicitly, current-result state and accessible limitations. Use existing server statistics; null ratios show `—`, never division by zero.
- [ ] Before the first drag the card follows its geographic anchor on pan/zoom. Dragging the header switches it to a session screen position; use pointer capture, stop propagation and clamp to map bounds. Provide accessible Close and Reset position controls. A new selected area shows its own card state, not a mixture of area statistics.
- [ ] A subsequent successful calculation updates the card; failure does not make old data current. Clear or explicitly mark the card unavailable when the result is invalidated/area deleted. Undo/redo follows the authoritative project's result presence. Do not persist position or anchor metadata into project JSON.
- [ ] Run helper/frontend checks; production browser-test calculate, drag, resize, reset, pan/zoom, close/reopen, another area, redraw, invalidation, failed response and save/reopen fallback. Confirm card events do not add polygon vertices or move source poles.

**Acceptance:** BL004-01: success opens correct-area results beside drawing endpoint. BL004-02: freely movable, recoverable card with correct units/ratios. BL004-03: current/stale/failed state is truthful. BL004-04: no schema, export, source or calculation mutation.

## 12. Task 7 — BL-005: fixture-direction arrows

**Important:** DL-011 defines grid-north azimuth. Simply rotating a screen icon by the stored degree number ignores projection convergence and map bearing. The selected SMART camera handle is not an authoritative all-fixture solution.

**Files:** Create `backend/app/services/fixture_direction_preview.py`, `backend/tests/test_fixture_direction_preview.py`, `frontend/app/lib/fixture-direction-view.mjs`, its `.d.mts`, and `frontend/tests/fixture-direction-view.test.mjs`. Modify `backend/app/main.py`, `frontend/app/lib/api.ts`, `EngineeringMap.tsx`, `EngineeringWorkspace.tsx`. New strict request/response definitions may live in the preview service module; reuse `Project` as the request. Regenerate `schemas/openapi.json`; `schemas/project.schema.json` must remain equivalent. Version metadata only after the recorded API-version decision. No dependency change.

**API contract proposed:** `POST /api/fixture-directions/preview`, body the current `Project` (including unsaved edits), response `{directions: [...], unavailable: [...]}`. Each direction is `{pole_id, origin_wgs84, endpoint_wgs84, fixture_azimuth_deg, active}`; each unavailable row is `{pole_id, reason}`. This operation does not save a project, update timestamps, calculate lighting or mutate catalogs. Use existing request size/validation discipline and reject invalid projected CRS with controlled errors.

**Geometry interface:** `projected_direction_endpoint(x, y, azimuth_deg, length_m=1.0)` returns `(x + length_m*sin(angle), y + length_m*cos(angle))`. The service resolves existing source origin and explicit pinned fixture configuration with existing catalog validation, transforms origin to project metres, computes the one-metre display segment, and transforms both endpoints back to WGS84 with `app/crs.py`. The metre is a display-direction sample only, not beam range. Preserve the authoritative calculation-origin convention; do not introduce coordinate edits.

- [ ] Write backend tests for N/E/S/W, near-zero/360, project CRS with measurable convergence, no CRS, missing configuration, pinned revisions, invalid input and non-mutation. Example mathematical assertion:

```python
assert projected_direction_endpoint(100.0, 200.0, 90.0) == pytest.approx((101.0, 200.0))
```

- [ ] Implement the pure preview service and route with explicit unavailable reasons. Include every configured lighting-capable LITE/WIFI/SMART fixture; inactive ones may display muted when their existing fixture layer is visible. Unconfigured fixtures get a clearly labeled “direction unavailable” indicator, not a fabricated north arrow.
- [ ] Implement the typed client call using a cancelable/request-sequenced refresh keyed only to direction-significant inputs: project CRS, source IDs/origins, effective fixture model/revision, activity and azimuth. Ignore late responses after newer edits or project replacement. Do not send preview requests on every pan or pointer movement.
- [ ] Project each returned endpoint pair through the current map. A screen direction vector is `(end.x-start.x, end.y-start.y)`; normalize it to a 24 px arrow adjacent to the fixture, with a contrasting casing and an arrowhead, while retaining original fixture marker colors. Recompute screen positions on map motion. No arrow-drag editing is added by this task; existing selected SMART editing remains separate.
- [ ] Run preview/backend tests, generated-contract checks, frontend checks and prior orientation regressions. Browser-test all fixture variants, unconfigured/inactive cases, projected-grid north/east versus a rotated map, azimuth edits, undo/redo/reopen, and rapid changes during requests. Confirm arrows and labels agree with stored fixture azimuth, not camera offsets.

**Acceptance:** BL005-01: visible directions for every configured lighting fixture. BL005-02: correct projected-north/map-bearing conversion. BL005-03: absent direction is explicit and no angle is invented. BL005-04: preview is read-only and late responses cannot display obsolete directions. BL005-05: no project-schema migration or source/result mutation.

This item requires approval of its read-only API boundary. If execution proposes a frontend projection library instead, record that alternative and dependency decision before implementation; do not casually approximate metres with latitude/longitude degrees.

## 13. Task 8 — BL-001: satellite background, after provider approval

**External decision (recorded 2026-09-07):** User authorized the **free non-commercial EOX public WMTS** (no purchase). Standard = current OSM. Satellite = environment-configured public tiles with required attribution. Session-only. The satellite provider **may be replaced later**; do not bake EOX or any provider into saved projects. Controlling record: `docs/post-roadmap-bl-001-provider-authorization-2026-09-07.md`.

Still verify the current official EOX Maps/s2maps endpoint, 3857 XYZ template, tile size, zoom range, and attribution **at execution time**. Do not copy an unverified tile URL. Do not accept paid terms or purchase a mosaic in this task.

Earlier tasks do not wait for this decision. This is a real external dependency, not an invitation to invent a provider.

**Files after approval:** Modify `EngineeringMap.tsx`, `EngineeringWorkspace.tsx`, `frontend/app/globals.css`, `frontend/README.md`; create `frontend/app/lib/map-background.mjs`, its `.d.mts`, `frontend/tests/map-background.test.mjs`, and `frontend/.env.example` with documented configuration names and no live secrets. Provider-specific additional paths require an explicit boundary amendment.

**Interface:** `backgroundAvailability(config)` returns whether a validated satellite configuration is usable and its attribution. Config accepts a documented tile URL template, tile size and min/max zoom with provider-approved values. This config is deployment/local environment data, not project JSON. Any credential embedded in browser requests must be explicitly intended for public client use with provider restrictions; never embed a private server credential in `NEXT_PUBLIC_*`.

- [ ] Record the provider approval, exact configuration and permitted source. Test missing/invalid config, unavailable imagery and valid Standard/Satellite selection. The test fixtures use non-network example templates; browser verification uses the approved real service.
- [ ] Add a visible two-choice selector. Add a satellite raster source/layer beneath engineering layers and switch background visibility in place. Do not replace the whole MapLibre style and lose overlays/listeners. Standard remains the existing OSM layer with its attribution.
- [ ] Keep the selected choice session-only, resetting safely if provider configuration becomes unavailable. Show correct attribution for the selected background. If imagery fails, show an actionable error and “Use standard map”; do not remove drawings/results to recover.
- [ ] Verify repeated switching with active polygon draft, Wi-Fi/CAP layers, lighting labels/card, and direction arrows. Test failed tile load, max/min zoom, viewport resize, and no-secret source/config review. Preserve source coordinates and engineering results exactly.

**Acceptance:** BL001-01: Standard/Satellite choice works with approved provider. BL001-02: viewport, draft and all overlays survive switching. BL001-03: attribution/error/fallback are correct. BL001-04: no credential leakage, unapproved service use, project migration or source mutation.

## 14. Per-item completion and final handoff

For every item, complete this checklist in its own verification record:

- [ ] Authorized ID/design/file boundary recorded; current baseline and actual starting diff captured.
- [ ] Preflight succeeded and legitimate generated/config paths are within the approved boundary.
- [ ] All task acceptance IDs have objective results; no “done” based solely on a commit or screenshot.
- [ ] Focused tests and frontend typecheck/lint/build/full test passed against the recorded implementation tree; backend/source/generated checks run when required by the item and repository policy.
- [ ] Production UI walkthrough performed with isolated test data; browser warnings/errors preserved and dispositioned, not hidden.
- [ ] Source upload bytes, 74 source coordinates/raw text and frozen catalogs unchanged. No unintended API/schema/export drift.
- [ ] Implementation commit recorded, evidence-only follow-up commits identified, and worktree clean for independent handoff.
- [ ] Independent review and scoped master decision recorded before acceptance/merge. No new phase seal is created by the implementer.
- [ ] Backlog updated with implementation/review status and evidence links, without overwriting original reports.

At the end of the authorized sequence, run the full backend suite, engineering/source validator and frontend build/test/typecheck/lint on the integrated implementation, plus schema regeneration/freshness when the API changed. Repeat the combined 74-pole workflow: import, IES assignment, each polygon tool, lighting, Wi-Fi, CAP test-only recommendation, save/reopen and existing report generation. Cross-check numeric/map/list consistency and source preservation. This is regression verification, not permission to change Phase 7 reports.

Stop only the affected task for a genuine unresolved authority/provider/contract boundary; continue other separately authorized independent work where possible. Apply the repository's recovery/blocker protocol to ordinary environment or test failures. Never weaken a requirement or assert a pass to finish a task.

## 15. What this handoff does and does not contain

The handoff ZIP contains this plan, all eight backlog entries, the detailed reproduction report and machine-readable diagnostic observations. It contains no application code, dependencies, runtime projects, customer exports or credentials. Clone the repository separately and place these documents at their relative paths.

The prior live walkthrough used a development build and one eligible Wi-Fi fixture/one test CAP candidate. It confirmed polygon feedback failure, explicit-layer visibility behavior, three compatible IES associations, and the CAP control/result path. It did not prove production behavior, full CAP capacity/optimality, all IES files, or every polygon tool. This plan's verification requirements deliberately cover those gaps where relevant.

Implementation authorization is not included in the ZIP as an already granted decision. The user must send a concrete instruction to Cursor identifying the items/designs to execute. Once that is supplied, no additional design discovery is needed for the proposed first item; begin its preflight and recorded test cycle. Satellite remains conditional on its provider decision.

## 16. Additional executable test specifications

These small examples specify proposed helper behavior; they belong in the corresponding new tests, not in production files. Import `assert` from `node:assert/strict` and the named helper from its task's proposed `.mjs` module. Complete API models in integration tests with the real repository fixtures rather than coercing malformed partial objects.

```javascript
// frontend/tests/wifi-map-state.test.mjs
assert.equal(wifiMapState(null, true), 'not-calculated');
assert.equal(wifiMapState({global_statistics: {circle_count: 0}}, false), 'empty');
assert.equal(wifiMapState({global_statistics: {circle_count: 1}}, false), 'hidden');
assert.equal(wifiMapState({global_statistics: {circle_count: 1}}, true), 'visible');
```

```javascript
// frontend/tests/cap-workflow-view.test.mjs: focused view-contract fixture
const project = {
  cap_calculations: {
    status: 'calculated', calculation_input_sha256: 'input-a',
    result: {result_sha256: 'result-a', selected_candidate_ids: ['site-a'], unresolved_node_ids: []}
  },
  cap_recommendations: {selected_candidate_ids: ['site-a'], result_sha256: 'result-a'}
};
assert.deepEqual(capResultSummary(project), {
  state: 'current', selectedIds: ['site-a'], unresolvedIds: []
});
const stale = structuredClone(project);
stale.cap_calculations.status = 'not-calculated';
stale.cap_calculations.result = null;
assert.deepEqual(capResultSummary(stale), {
  state: 'not-calculated', selectedIds: [], unresolvedIds: []
});
```

```javascript
// frontend/tests/lighting-card-position.test.mjs
assert.deepEqual(clampCard({x: 900, y: 700, width: 280, height: 180},
  {width: 800, height: 600}), {x: 512, y: 412});
assert.deepEqual(clampCard({x: -20, y: -30, width: 280, height: 180},
  {width: 800, height: 600}), {x: 8, y: 8});
```

For BL-005, define the pure frontend helper `screenArrow(origin, endpoint, length=24)` with `{x,y}` pixel coordinates; it returns a normalized `{dx,dy}` vector or null for coincident/nonfinite points. Its implementation uses only display pixels, after the backend has already handled metre-CRS geometry.

```javascript
// frontend/tests/fixture-direction-view.test.mjs
assert.deepEqual(screenArrow({x: 10, y: 20}, {x: 10, y: 19}), {dx: 0, dy: -24});
assert.deepEqual(screenArrow({x: 10, y: 20}, {x: 11, y: 20}), {dx: 24, dy: 0});
assert.equal(screenArrow({x: 10, y: 20}, {x: 10, y: 20}), null);
```

For BL-001, `backgroundAvailability` returns `{available: false, reason: 'Satellite imagery is not configured'}` for null configuration. A valid config returns `{available: true, attribution: config.attribution}` only after URL-template/tile-size/zoom validation. The `.invalid` address below is deliberately a non-network test fixture, not an authorized provider endpoint.

```javascript
// frontend/tests/map-background.test.mjs
assert.deepEqual(backgroundAvailability(null), {
  available: false, reason: 'Satellite imagery is not configured'
});
assert.deepEqual(backgroundAvailability({
  tiles: ['https://imagery.invalid/{z}/{x}/{y}.png'],
  tileSize: 256, minZoom: 0, maxZoom: 18, attribution: 'Test attribution'
}), {available: true, attribution: 'Test attribution'});
```
