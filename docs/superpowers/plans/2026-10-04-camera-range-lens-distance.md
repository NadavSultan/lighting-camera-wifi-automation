# Camera Range, Lens Details, and Distance Measurement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Execute sequentially in the existing worktree; do not delegate or run parallel implementation. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Deliver the approved bounded camera preview, pinned specification cards, and transient projected-distance tool through verified implementation-readiness handoff.

**Architecture:** Render the existing BL-016 projection envelopes beneath the continuous heat map using the same freshness/visibility gate. Resolve specification cards from exact catalog revisions. A read-only FastAPI endpoint uses the shared PyProj metre-CRS utilities; frontend session state owns measurement interactions and drawing.

**Tech Stack:** Existing Python 3.12, FastAPI/Pydantic/PyProj, React/TypeScript, MapLibre, Node test runner, pytest, Corepack/pnpm; no new dependencies.

**Spec:** `docs/superpowers/specs/2026-10-04-camera-range-lens-distance-design.md`, approved by the user in this chat on 2026-10-04. The user separately approved this plan and authorized implementation on 2026-10-04.

## Global Constraints

- The existing project-level **Maximum visible distance (m)** in the Camera pixel-density panel is the only range control. Its default remains 50 m.
- The stored `camera_geometry` footprints, overlap metrics, provenance, and Phase 3 calculation remain unchanged.
- BL-016 pixel density keeps its approved maximum-contributor overlap rule, 0.16 m reference face, fixed legend, and informational disclaimer.
- Current catalog values must not silently replace pinned historical revision values.
- The result is session-only UI state and is not written into the project, exports, or calculation layers.
- Customer poles and immutable input files remain unchanged.
- No merge, push, phase seal, Phase 8, or product acceptance claim; independent QA and scoped master review remain separate gates.

## Review Focus

- Late measurement responses after Clear, Esc, project replacement, or CRS change must not restore an obsolete line or distance (Task 4).
- Explicit camera/lens override IDs must use their own revision pins; missing pins must not fall through to template revisions or latest catalog entries (Task 3).
- A current envelope with no density bands must still render its subdued preview without inventing a density colour (Task 2).
- Measurement interaction must suppress delegated pole/area/CAP/density clicks and the draggable azimuth marker, not only the general map click (Task 4).
- Invalid coordinates, transform failures, and unavailable/non-metre CRS must yield a readable error and leave project bytes unchanged (Task 1).

## Execution Identity and File Boundary

Worktree: `C:\Users\NadavSultan\Desktop\Nadav\lighting-camera-wifi-automation\.worktrees\bl016-heatmap-correction`.
Branch: `codex/bl016-heatmap-correction`; inspected design checkpoint: `98ac861e5eb9bc1587604f3f43be61908baabfb2`; starting tracked/untracked status and diff were empty. The spec's `47f4e18` base is historical chronology, not the implementation starting HEAD. Record the new exact HEAD after plan approval in the work record.

Product/test boundary:

- Create `backend/app/services/map_distance.py`, `backend/tests/test_map_distance.py`.
- Modify `backend/app/main.py`; generated `schemas/openapi.json`.
- Modify `frontend/app/components/EngineeringMap.tsx`, `EngineeringWorkspace.tsx`, `PoleInspector.tsx`, and `frontend/app/globals.css`.
- Create `frontend/app/components/MapDistanceControl.tsx`, `frontend/app/lib/map-distance-workflow.mjs`, `map-distance-workflow.d.mts`, `camera-slot-specifications.mjs`, and `camera-slot-specifications.d.mts`.
- Modify `frontend/app/lib/api.ts`, `camera-pixel-density-map.mjs`, and `camera-pixel-density-map.d.mts`.
- Modify `frontend/tests/camera-pixel-density-map.test.mjs`, `camera-pixel-density-view.test.mjs`, `camera-projection-legend.test.mjs`, and `rendered-html.test.mjs` only for affected assertions.
- Create `frontend/tests/map-distance-workflow.test.mjs` and `camera-slot-specifications.test.mjs`; extend `backend/tests/test_bl016_camera_pixel_density.py` for preview-bound and Phase 3 preservation regressions.

Execution/evidence boundary: this plan; the approved spec's status line; dated `2026-10-04-camera-range-lens-distance` work/log/verification/readiness/completion/QA-handoff records under `harness/phases/`, `harness/logs/`, and `harness/verify/`; `GOALS.md`, `PLANS.md`, `OPERATIONS.md`, `docs/current-status.md` for truthful scoped execution-state reconciliation. A new isolated live harness may be created at `harness/verify/run_camera_range_lens_distance_live.py`.

Supporting configurations to inspect in preflight: `backend/pyproject.toml`, `backend/requirements.lock`, `frontend/package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `vite.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `postcss.config.mjs`, `.openai/hosting.json`, `build/sites-vite-plugin.ts`, and worker configuration. Do not change these tracked configurations or dependencies for this feature. Dependency materialization, pytest temp files, frontend `dist`, `.wrangler`, Vite caches, runtime project/catalog data, and browser logs use ignored worktree-local or temporary paths only.

The exporter legitimately rewrites five files: `schemas/project.schema.json`, `openapi.json`, `fixture-model-catalog.schema.json`, `ies-library.schema.json`, `camera-equipment-catalog.schema.json`. Only OpenAPI is expected to differ; verify the other four stay byte-identical. No persisted schema/version migration is planned. All other product files, `Input/`, `data/`, locks, and existing seals are excluded. Resolve a required tracked configuration defect before expanding the boundary.

## Task 0 / M0: Activate execution and verify the environment

- [x] After plan approval, read the goal and executing-plans skills; create one durable goal for this approved scope. Its stopping condition is clean implementation-readiness PASS plus the independent-QA handoff, not a progress update or commit.
- [x] Reinspect exact HEAD/status/diff; create `harness/phases/2026-10-04-camera-range-lens-distance.md` from the work-record template and the paired log from the execution-log template. Record approval, goal state, scope boundary, base, milestones M0–M5, and acceptance IDs UX-01–UX-09 below.
- [x] Discover the worktree's Python 3.12/Node/Corepack/browser runtimes. Use `load_workspace_dependencies` if needed; record exact resolved executable paths. Materialize `backend/requirements.lock` into the worktree environment and run `pip check`; run `corepack pnpm install --frozen-lockfile` in `frontend` without lock/workspace changes.
- [x] Run and record the baseline commands listed under Final verification, including a production build before the rendered frontend tests. Verify the five schema outputs remain unchanged at baseline; record legitimate ignored write locations, available browser access, and free isolated ports (start with 8070/3070). Do not terminate another session's listeners.
- [x] Record each preflight row before touching product files. Commit only the explicit scoped execution documents once the preflight passes.

## Task 1 / M1: Read-only projected-distance service and API

**Files:** new backend service/test, `backend/app/main.py`, `schemas/openapi.json`, `frontend/app/lib/api.ts`.

**Interfaces:** define strict `MapDistanceRequest(projected_crs: str, start_wgs84: tuple[float, float], end_wgs84: tuple[float, float])` and `MapDistanceResponse(projected_crs: str, distance_m: float)` in `map_distance.py`; export `measure_map_distance(request: MapDistanceRequest) -> MapDistanceResponse`. Add `POST /api/map/distance` with those request/response models. The client wrapper is `measureMapDistance(projectedCrs: string, start: [number, number], end: [number, number], init?: RequestInit): Promise<{ projected_crs: string; distance_m: number }>`; it may carry an AbortSignal and never saves a project.

- [x] Write tests `test_known_projected_distance`, `test_zero_distance`, `test_invalid_coordinate_or_crs`, and `test_distance_api_does_not_persist`. Generate WGS84 endpoints by inverse-transforming points 30 m east/40 m north apart in EPSG:32617; assert 50 m within `1e-6 m`. Test longitude/latitude bounds, non-finite input, extra fields, missing CRS, geographic CRS, projected-foot CRS, transform errors/non-finite output, and readable 422. Snapshot project/catalog bytes before/after successful and rejected requests.
- [x] Run from `backend`: `..\.venv\Scripts\python.exe -m pytest tests/test_map_distance.py -q -p no:cacheprovider`; record RED due to absent feature.
- [x] Implement the strict models, existing `validate_projected_metre_crs` / `project_transformers` reuse, `errcheck=True` transformations and finite-result checks, and `math.hypot` distance. Return validated CRS identity; map controlled transform/validation errors to 422. Do not read/write project stores or catalogs. Implement the typed client wrapper.
- [x] Rerun the focused tests to PASS; run schema export using `-m scripts.export_schema`; assert only OpenAPI changes. Commit the service, endpoint, wrapper, tests, and generated OpenAPI together.

## Task 2 / M2: Bounded camera preview and one visualization control

**Files:** density map helper/declaration, `EngineeringMap.tsx`, `EngineeringWorkspace.tsx`, affected frontend tests, BL-016 backend regression tests.

**Interfaces:** `densityPreviewFeatures(project)` returns GeoJSON polygon features from valid enabled camera results' `projection_envelope.wgs84_rings`, with footprint/slot identifiers and holes preserved. Use the existing `visibleResult` matching-current-visible gate. Add a `camera-density-preview` source with subdued fill/outline beneath `camera-density-heatmap`.

- [x] Write failing frontend tests asserting unchanged envelope coordinates/holes, visibility for an envelope with zero bands, and empty results for hidden/stale/invalid/not-calculated/mismatched fingerprints. Keep overlap inspection tests asserting the persisted winner/contributors and multiplicity. Add backend tests that default 50 m and requested 25 m/75 m bound every projected envelope vertex relative to its origin (within existing geometry tolerance), and that density calculation/profile changes leave Phase 3 footprints/metrics byte-equivalent.
- [x] Run focused backend tests and `node --test tests/camera-pixel-density-map.test.mjs tests/camera-pixel-density-view.test.mjs tests/camera-projection-legend.test.mjs` from `frontend`; preserve RED evidence for newly missing preview behavior.
- [x] Implement preview features and map source/layers. Remove raw Phase 3 FOV and overlap fills/sources from the map, and their obsolete primary layer controls/profile entries; retain their persisted fields and metric/report workflows. Make Camera pixel density control the preview/raster/inspection layers together. Explain calculate/recalculate state near the existing range control; retain the default, fingerprint lifecycle, legend, and existing calculate action.
- [x] Rerun focused tests to PASS, typecheck and lint; verify no source changes to accepted Phase 3 geometry or the density engine/heatmap mathematics. Commit the preview/control changes and regression tests.

## Task 3 / M3: Pinned camera/lens specification cards

**Files:** new `camera-slot-specifications` helper/declaration/test, `PoleInspector.tsx`, scoped CSS.

**Interfaces:** `resolveCameraSlotSpecifications(catalog: CameraEquipmentCatalog | null, slot: CameraMountingSlot, override?: PoleCameraOverride)` returns `{ camera: CameraModel | null, lens: LensConfiguration | null, warnings: string[] }`; use these existing exported types in the `.d.mts` declaration without adding persisted fields.

- [x] Write failing tests with current revision 2 and historical revision 1 values; assert historical names, focal length, H/V FOV and resolution come from revision 1. Test explicit replacement IDs with missing revisions, inherited template assignments, null/unassigned IDs, absent catalog/history, incompatibility, and nullable specification fields. Assert resolver/viewing does not mutate catalog, slot, overrides or project.
- [x] Run `node --test tests/camera-slot-specifications.test.mjs`; preserve RED evidence.
- [x] Implement exact `(id, revision)` resolution across current/history arrays, using the corresponding template pin only for an inherited assignment. Resolve compatibility from the pinned lens's authoritative camera relation. Render a read-only card per slot with names/IDs/revisions, mm/degree/px units, and explicit unavailable/unassigned/incompatible notices. Display unknown numeric fields as unavailable, never guessed or derived from old footprints. Keep existing selectors as assignment controls.
- [x] Rerun tests to PASS, typecheck/lint; verify both slots before calculation and with historical revisions. Commit the helper, card, CSS and tests.

## Task 4 / M4: Exclusive transient two-click measurement

**Files:** new `MapDistanceControl.tsx`, `map-distance-workflow` helper/declaration/test; `EngineeringMap.tsx`, `EngineeringWorkspace.tsx`, CSS; Task 1 API wrapper.

**Interfaces:** `MeasurementState` is a discriminated union for `idle`, `first-point`, `second-point`, `pending`, `complete`, `error`, with session endpoints and optional distance/error. `MapDistanceControl` takes state, disabled reason, and start/clear/cancel callbacks. Keep state/controller in `EngineeringMap`; the workflow module supplies `initialMeasurementState()`, `startMeasurement(state)`, `addMeasurementPoint(state, coordinate)`, `clearMeasurement()`, `cancelMeasurement(state)`, and `measurementBlocksMapInteractions(state)`, with declared TypeScript equivalents. HTTP completion is guarded by a request generation and project-ID/CRS identity.

- [x] Write failing workflow/dispatcher tests for first/second click, one request, ignored third click while pending/complete, zero-length line, clear-to-new-measurement, Esc cancellation, and error/no fabricated value. Add fake deferred-request tests proving Clear/Esc/project replacement/CRS change discard late completion. Test all drawing modes block measure start; measurement blocks pole/area/CAP/density selection and azimuth dragging. Use shared dispatcher guards exercised by the map, not source-text assertions as behavioral evidence.
- [x] Run `node --test tests/map-distance-workflow.test.mjs`; preserve RED evidence.
- [x] Implement the state transitions and backend call on the second click. Clear aborts/invalidates the current request, removes all measurement artifacts, and starts a fresh first-point session; Esc cancels an unfinished session and invalidates pending work. Errors expose a readable message with no numeric result and offer Clear for retry. Reset on project replacement or CRS change.
- [x] Integrate one measurement source/line/endpoint layer and a safe text label; suppress competing handlers and remove/disable the draggable azimuth marker while measuring. Disable all area creation/redraw entry points during an unfinished measurement, and disable measure start while any area draft is active. Retain ordinary pole/area interaction after completion; third clicks cannot alter the measurement.
- [x] Render lower-left Measure distance / Clear measurement control with accessible state/error text, clear of attribution and controls; responsive CSS must fit the map at desktop and narrow widths. No measurement field enters Project, history, save payloads, exports, or calculation results.
- [x] Rerun focused tests to PASS, typecheck/lint, and density click-dispatch regression. Commit measurement integration and tests.

## Task 5 / M5: Full verification, production browser, and readiness

- [x] Run the final command sequence below on the exact committed implementation. Capture exit codes, output/warnings, HEAD and clean/dirty identity; repair failures and rerun affected checks, then the complete final sequence after any product changes.
- [x] Run the existing BL-016 isolated live regression runner using a new ignored output path. Create the scoped live runner only for additional API/non-persistence assertions and isolated server lifecycle; do not rewrite historical evidence. Record all generated results with their true HEAD.
- [x] Run a real production browser against the built app using preserved `Input/Miracle_Mile_Lighting_Poles.kml`. Import 74 poles in five folders; explicitly configure SMART camera/lens assignments. Verify default 50 m, shorter 25 m and longer 75 m with stale/recalculate behavior, bounded preview below 2 px/face, continuous heat colours, no uncapped FOV fill, hide/show and unchanged Phase 3 metrics. Verify both pinned specification cards, density overlap winner/contributor inspection, Standard/Satellite, and unchanged pole coordinates.
- [x] In that browser measure known projected endpoints (50 m expected, `0.1 m` allowance for click placement/display rounding); retain clicked WGS84 coordinates and compare backend output to an independent PyProj reference within `1e-6 m`. Verify Clear/new measurement, Esc, pole/azimuth/density click suppression, drawing conflicts, error state, save/export/reopen without measurement persistence, lower-left layout at desktop/narrow widths, and zero console/page errors. Preserve screenshots and console/network/interaction evidence; API-only runner evidence does not substitute for browser interaction.
- [x] Compare all protected paths to the recorded base; check original KML SHA-256 `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`. Final source/generated/dependency/boundary checks must pass with no unrelated changes.
- [x] Complete the scoped verification summary, completion report, browser evidence and QA-handoff records. Populate `harness/verify/2026-10-04-camera-range-lens-distance-readiness.json` from the readiness template, with M0–M5 and UX-01–UX-09, exact implementation commit, command evidence and pending QA/master. Update execution indexes truthfully; commit evidence separately with permitted evidence paths declared in the manifest.
- [x] Run the final readiness command on a clean worktree. After PASS and the recorded QA handoff, complete the durable goal; report implementation complete awaiting independent QA. Do not self-approve QA or acceptance, merge, push, or create a seal.

## Acceptance Coverage

- UX-01: single default-50-m range/calculate workflow and bounded 25/75-m previews — Task 2 and production browser.
- UX-02: shared stale/invalid/not-calculated/hidden gate, below-threshold preview without fabricated density colour — Task 2.
- UX-03: no raw FOV/overlap map fill; byte-equivalent persisted Phase 3 results — Task 2 and browser.
- UX-04: exact pinned per-slot camera/lens specs and explicit missing/incompatible states — Task 3 and browser.
- UX-05: validated metre-projected straight-line distance and read-only API — Task 1.
- UX-06: two clicks, clear/new measure, Esc, error and asynchronous lifecycle safety — Task 4 and browser.
- UX-07: exclusive map interactions and responsive accessible lower-left placement — Task 4 and browser.
- UX-08: no measurement persistence; unchanged source bytes/poles, catalogs, dependencies and density overlap semantics — Tasks 1–5.
- UX-09: full deterministic/generated/production-browser verification and clean readiness handoff — Task 5.

## Final Verification Commands

Use the actual preflight-resolved Python executable if `.venv` is absent; record that substitution without modifying source. The existing live runner requires a worktree-local `.venv`, so materialize that environment before running it. Run each command separately and retain output. The example `--basetemp` and live-output destinations below must be unused; suffix them with the run timestamp for reruns so pytest never deletes prior evidence or user-owned temp state.

From `backend/`:

```powershell
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp ..\harness\tmp\camera-ux-final-before-schema
```

From worktree root:

```powershell
.\.venv\Scripts\python.exe scripts\validate_engineering_data.py
```

From `backend/`:

```powershell
..\.venv\Scripts\python.exe -m scripts.export_schema
..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp ..\harness\tmp\camera-ux-final-after-schema
```

From `frontend/` (build precedes rendered tests because they import `dist/server/index.js`):

```powershell
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm run build
corepack pnpm run test
```

From root, after implementation commit, using fresh ignored output and no overwrite of historical evidence:

```powershell
.\.venv\Scripts\python.exe harness\verify\run_bl016_camera_pixel_density_live.py --output harness/tmp/camera-ux-final-bl016-live.json
git diff --exit-code -- schemas Input frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml
git diff --check
Get-FileHash -Algorithm SHA256 -LiteralPath Input/Miracle_Mile_Lighting_Poles.kml
git status --short --branch
.\.venv\Scripts\python.exe harness\verify\verify_phase_readiness.py --manifest harness/verify/2026-10-04-camera-range-lens-distance-readiness.json
```

The separate recorded base comparison must additionally show no changes to the four non-OpenAPI schemas, frozen catalogs, dependencies/configurations and accepted seals; the HEAD diff above proves generated freshness, not base preservation.

## Recovery and Approval Gates

Follow `AGENTS.md`'s proven-blocker rule once throughout execution: preserve status/diff and failed command evidence; make at least three materially different safe recovery attempts for a suspected blocker; request direction only if the same condition still prevents meaningful in-scope work and requires new authority, a product decision, external-state change or prohibited expansion. Never discard unrelated changes or kill user-owned processes. Use unique safe temp directories rather than deleting shared temp state to rerun verification.

This plan was separately approved on 2026-10-04. Execute natively and sequentially in this worktree. The implementation handoff requests independent QA using `harness/templates/qa-review-template.md`; independent QA/master approval is not performed by this plan.

## Execution disposition — 2026-10-04
Product `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`. Legacy live runner attempted but failed occupied3070 and incorrectly stopped that unknown listener; failure retained. Equivalent coverage completed using ownership-safe scoped runner (20 API assertions) and real production browser. Checkmarks describe implementation completion or that explicit recovery, never legacy-runner PASS. Clean readiness result recorded after evidence commit; independent QA/master not performed.
