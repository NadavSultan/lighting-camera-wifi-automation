# Phase 4 final corrective completion report

Date: 2026-08-17  
Role: dedicated final Phase 4 corrective implementation engineer  
Scope: P4-IR-05 only

## Completion boundary

The final corrective implementation is commit `828ca658fcdf9f5aea513b833b772975f05df487` (`fix final Phase 4 invalid CRS handling`). This report records implementation and verification evidence, not independent approval. Phase 4 remains unapproved pending one final independent focused P4-IR-05 retest and an explicit master gate decision. Phase 5 conceptual Wi-Fi and all later work remain unauthorized and were not implemented.

P4-IR-01, P4-IR-02, P4-IR-03, P4-IR-04, P4-IR-06, and P4-IR-07 passed the independent corrective retest and were not reopened or changed.

## Root cause and exception boundary

Shared project save, open, get, bulk, and recalculation flows call Phase 3 `calculate_camera_geometry()`. The service passed `project.projected_crs` directly to `CRS.from_user_input()` and built two transformers without translating expected pyproj construction failures. Consequently, `NOT-A-CRS` raised an uncaught `pyproj.exceptions.CRSError`, bypassed the existing endpoint `ValueError` handlers, and returned HTTP 500. The frontend correctly parses backend JSON validation details, but a 500 without a usable detail appeared as `Failed to fetch` in the rendered Open Project workflow.

The correction is deliberately limited to `backend/app/services/camera_geometry.py`:

- `CRS.from_user_input()` catches only `CRSError` and raises `ValueError("Invalid projected CRS for camera geometry: <value>")`.
- `Transformer.from_crs()` construction catches only `CRSError` and `ProjError` and raises a clear camera-geometry transformation `ValueError`.
- Missing CRS still returns the existing empty camera layer.
- Geographic and projected non-metre CRS still return the existing empty camera layer.
- Valid projected metre CRS follows the identical geometry path and equations.
- No broad exception handler masks unrelated programming defects.

## Minimal files changed

- `backend/app/services/camera_geometry.py`: expected pyproj CRS/transformer construction exception translation only.
- `backend/tests/test_phase3_camera_geometry.py`: focused service and shared-endpoint P4-IR-05 regressions.
- `docs/current-status.md`: current gate, final corrective state, and 118-test evidence.
- `docs/phase-4-corrective-retest-report.md`: independent retest evidence added to Git unchanged.

No model, schema, OpenAPI, catalog, frontend, lighting-calculation, equation, camera-footprint equation, or UI-design file changed.

## Endpoint and preservation results

Focused TestClient regressions produced these results:

- `PUT /api/projects/{id}` with `NOT-A-CRS`: `422` with `Invalid projected CRS for camera geometry: NOT-A-CRS`; the prior stored `EPSG:32617` project remained unchanged.
- `POST /api/projects/open` with a separate invalid project: `422` with the same readable detail; project count remained unchanged and no directory was created for the invalid project.
- `GET /api/projects/{id}` after deliberately placing an invalid-CRS project in isolated storage: `422` with `Stored project is invalid or corrupt: Invalid projected CRS for camera geometry: NOT-A-CRS`, not `404` or `500`.
- `PATCH /api/projects/{id}/poles/bulk` against that invalid stored project: `422`; the exact pre-request project bytes remained unchanged.
- `POST /api/projects/{id}/camera-geometry/recalculate` with invalid CRS: `422`; the prior valid stored project remained `EPSG:32617`.
- `POST /api/projects/{id}/lighting/calculate/{area_id}` with invalid CRS: remained controlled at `422`; the prior valid lighting result/project remained unchanged.
- KML import accepts source bytes rather than a caller-supplied CRS and continues selecting its valid projected CRS through the unchanged import path; the complete suite retained its import regressions.

Direct camera-service cases confirm that `EPSG:32617` still produces the expected two valid SMART-camera footprints, while `EPSG:4326` and projected non-metre `EPSG:2263` retain the approved empty-layer behavior.

## Test and regression evidence

- Focused P4-IR-05 run: PASS, 3 tests. It covered the camera service CRS matrix, shared save/open/get/bulk/camera-recalculate preservation paths, and the existing lighting invalid-CRS/unsafe-spacing test.
- Complete backend suite: PASS, 118 tests. The suite was run once after the focused correction and includes all existing Phase 1-4 regressions, the Phase 3 camera geometry suite, supported migrations, and in-memory schema/OpenAPI freshness assertions. One existing non-failing Starlette/httpx2 deprecation warning remains.
- `git diff --check`: PASS; CRLF conversion notices were advisory and no whitespace defect was reported.

No frontend source changed. Frontend tests, strict TypeScript, ESLint, and production build were therefore not rerun, as directed; their already-passing evidence from the prior corrective implementation remains applicable. No contract-generating file changed and no schema regeneration was required. The complete backend suite nevertheless retained the existing exact in-memory schema/OpenAPI checks.

## Rendered smoke evidence

The existing production build was served from an isolated temporary runtime copy whose embedded local API address was redirected only inside that disposable copy to an isolated current-code backend. Repository frontend assets were not modified or rebuilt.

- Opening a temporary no-source project with `projected_crs="NOT-A-CRS"` returned `POST /api/projects/open` status `422` and visibly displayed `Invalid projected CRS for camera geometry: NOT-A-CRS`; it did not display `Failed to fetch`.
- Opening a separate `EPSG:32617` project returned `200`, displayed `Reopened Valid CRS rendered smoke from project JSON`, and retained `CRS: EPSG:32617`.
- Saving that valid project returned `PUT /api/projects/{id}` status `200` and displayed `Saved Valid CRS rendered smoke locally`.
- Browser console inspection returned no errors.

The temporary backend, frontend, payloads, and storage were isolated from repository/runtime project data and were stopped after the smoke.

## Evidence and scope preservation

The corrective retest report SHA-256 was verified before implementation and after the implementation commit as exactly `0FE6167908A391F6699C45BA0C272197C4AB9870D024D310D27E380723B4989A`. It is tracked at `docs/phase-4-corrective-retest-report.md` without modification. Prior QA, retest, completion, and corrective reports remain unchanged.

Git comparison confirms no change under `Input/`, `data/`, or `frontend/`. Customer source coordinates and source/upload bytes, seven frozen Phase 1 catalogs, lighting calculation/result behavior, camera geometry equations, camera `priority_areas`, lighting `calculation_areas`, and Phase 5 gating remain unchanged. No other corrective finding was touched.

## Final handoff

This correction does not declare Phase 4 approved. Independent QA should perform one final focused P4-IR-05 retest against implementation commit `828ca658fcdf9f5aea513b833b772975f05df487`, covering the controlled invalid-CRS response and preservation behavior across the shared paths plus the valid `EPSG:32617` path. Only a later explicit master gate decision may close Phase 4 or consider separate Phase 5 authorization.
