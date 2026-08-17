# Phase 4 Final Focused Corrective Retest Report

Date: 2026-08-17

Role: independent Phase 4 QA engineer

## Overall result

**FAIL**

P4-IR-05 is not fully resolved under the final focused acceptance contract. The correction converts syntactically invalid CRS input such as `NOT-A-CRS` into controlled HTTP 422 responses across the affected shared paths, with readable messages and preserved stored state. However, unsupported project CRS values remain accepted by those same shared paths: both geographic `EPSG:4326` and projected non-metre `EPSG:2263` returned HTTP 200 for save/update, open, get, bulk configuration, and camera geometry recalculation. Save/update and bulk configuration persisted those unsupported CRS values instead of preserving the previously valid project. The lighting endpoint alone rejected them with 422.

Phase 4 cannot be formally closed. Further corrective implementation and an independent focused retest are required. Phase 5 remains gated; this report neither authorizes nor begins Phase 5.

## Review boundary and commits

- Repository: `C:\Users\Nadav\Desktop\Automation Project\lighting-camera-wifi-automation`.
- Correction implementation tested: `828ca658fcdf9f5aea513b833b772975f05df487` (`fix final Phase 4 invalid CRS handling`).
- Final corrective completion report commit tested as an unverified claim set: `8bdbe0dba3a983ebde28ecca69c48f08fbf6fad6` (`docs: record final Phase 4 CRS correction`).
- HEAD before this QA report: `8bdbe0dba3a983ebde28ecca69c48f08fbf6fad6`.
- Prior corrective retest report SHA-256: `0FE6167908A391F6699C45BA0C272197C4AB9870D024D310D27E380723B4989A`.
- Scope was limited to P4-IR-05. P4-IR-01, P4-IR-02, P4-IR-03, P4-IR-04, P4-IR-06, and P4-IR-07 were not reopened because this narrow retest did not demonstrate a related regression.
- The implementation diff from `f170950` through `828ca658` changes `backend/app/services/camera_geometry.py`, `backend/tests/test_phase3_camera_geometry.py`, `docs/current-status.md`, and the previously uncommitted prior QA report. The completion-report commit adds only `docs/phase-4-final-corrective-completion-report.md`. No `Input/`, catalog, frontend, schema, or other application component changed.
- Pre-existing untracked `.runtime-logs/` content was not modified or staged.

## Environment and commands

- Windows 11, PowerShell, repository `.venv` Python 3.12 environment; host Python reported `3.12.7`.
- Git `2.53.0.windows.3`.
- Pinned frontend runtime Node `v24.19.0`; pnpm `11.19.0`.
- Backend rendered server: isolated temporary project/catalog roots, Uvicorn on `127.0.0.1:8024`.
- Frontend rendered server: the checked-in production build copied to an isolated temporary runtime, with only that disposable runtime's baked API URL changed from port 8000 to isolated port 8024, served by Vinext on `127.0.0.1:3025`. No repository frontend file was changed.
- Browser: Codex in-app Chromium browser against the real production-rendered application.

Principal commands and probes:

```text
.\.venv\Scripts\python.exe -m pytest -q backend/tests/test_phase3_camera_geometry.py::test_camera_geometry_crs_boundary_preserves_approved_behavior backend/tests/test_phase3_camera_geometry.py::test_invalid_camera_crs_is_controlled_across_shared_api_paths_and_preserves_store backend/tests/test_phase4_lighting_calculation.py::test_invalid_crs_and_unsafe_spacing_return_controlled_errors_and_preserve_project

.\.venv\Scripts\python.exe -m pytest -q backend/tests
.\.venv\Scripts\python.exe .\scripts\validate_engineering_data.py
.\.venv\Scripts\python.exe C:\Users\Nadav\AppData\Local\Temp\lcwa_phase4_final_retest_probe.py
git diff --name-status f170950..828ca658fcdf9f5aea513b833b772975f05df487
git diff --check f170950..828ca658fcdf9f5aea513b833b772975f05df487
```

The independent probe used a temporary project store, the real API application through `TestClient`, all 74 imported Miracle Mile source poles, explicit SMART camera and lighting configuration, a calculation area, and byte-level comparisons of stored project files. Temporary rendered projects and servers were isolated from user runtime projects and removed after the retest.

## Focused automated and regression evidence

- Focused correction tests: **PASS**, 3 tests. These verify the intended `NOT-A-CRS` correction and the previously corrected lighting spacing boundary.
- Complete backend suite: **PASS**, 118 tests, one existing non-failing Starlette/httpx2 deprecation warning. This includes Phase 1-4 backend regressions, supported migrations, and generated-contract assertions.
- Engineering/source validator: **PASS**, including seven catalog/schema pairs and supplied-source hashes.
- No generated-contract source changed in this correction. Existing exact generated-contract and supported-migration assertions remained green in the full backend run.
- `git diff --check f170950..828ca658` reports only the two intentional Markdown hard breaks at lines 3-4 of the prior corrective retest report. No genuine whitespace defect was found in the correction.

The passing implementation-authored tests are insufficient for the final acceptance because `test_camera_geometry_crs_boundary_preserves_approved_behavior` explicitly expects empty camera geometry for geographic and non-metre projected CRS instead of rejecting those unsupported project CRS values. The independent adversarial matrix below exposes the untested cross-path behavior.

## Required-path evidence

### Syntactically invalid CRS: `NOT-A-CRS`

| Path | Result | Readable detail and state evidence |
|---|---:|---|
| Save/update project | 422 | `Invalid projected CRS for camera geometry: NOT-A-CRS`; exact prior valid stored bytes preserved. |
| Open project | 422 | Same readable detail; project count unchanged and no invalid project created. |
| Get deliberately corrupt stored project | 422 | `Stored project is invalid or corrupt: Invalid projected CRS for camera geometry: NOT-A-CRS`; corrupt test fixture was not rewritten and error was not mislabeled as 404. |
| Bulk configuration against corrupt stored project | 422 | Readable invalid-CRS detail; submitted stored bytes preserved. |
| Camera geometry recalculation | 422 | Readable invalid-CRS detail; exact prior valid stored bytes preserved. |
| Lighting calculation | 422 | `Invalid projected CRS: NOT-A-CRS`; exact prior valid stored bytes preserved. |

No path returned HTTP 500. This portion of P4-IR-05 is corrected.

### Unsupported CRS values: `EPSG:4326` and `EPSG:2263`

Both unsupported cases produced the same result matrix:

| Path | Result | Actual behavior |
|---|---:|---|
| Save/update project | 200 | Accepted and overwrote the valid stored project with the unsupported CRS; preservation check failed. |
| Open project | 200 | Accepted, created a stored project, and increased project count by one. |
| Get project | 200 | Returned the unsupported project as current. |
| Bulk configuration | 200 | Accepted and persisted the unsupported project; preservation check failed. |
| Camera geometry recalculation | 200 | Returned an empty camera-geometry result instead of a client error. |
| Lighting calculation | 422 | Correctly rejected with `Lighting calculation requires a projected CRS with metre axes`; prior valid store preserved for this endpoint. |

`EPSG:4326` is geographic, and `EPSG:2263` is projected with non-metre axes. The final acceptance requires invalid **or unsupported** project CRS values to be rejected deterministically across every affected shared path. Returning 200 and persisting either value violates that contract even though no HTTP 500 occurs.

### Valid projected-metre CRS: `EPSG:32617`

The independent valid-path project passed every required operation:

| Path | Result |
|---|---:|
| Save/update | 200 |
| Open | 200 |
| Get | 200 |
| Bulk configuration | 200 |
| Camera geometry recalculation | 200, with 2 valid camera footprints |
| Lighting calculation | 200, with 9 deterministic lighting points |

Material stored state compared equal after reopen. This confirms that the correction did not regress ordinary `EPSG:32617` persistence, camera recalculation, or lighting calculation.

## Rendered-app and browser-console evidence

The production-rendered application was exercised against the isolated correction backend rather than a source-only or unit-test harness.

- Opening the `NOT-A-CRS` project produced the visible message `Invalid projected CRS for camera geometry: NOT-A-CRS`. The workspace remained responsive and unloaded; backend access logs recorded `POST /api/projects/open` as 422. There was no crash or silent failure.
- Opening the `EPSG:4326` project visibly reported `Reopened Unsupported CRS rendered probe from project JSON`, displayed `CRS: EPSG:4326`, and treated the project as loaded. Backend logs recorded `POST /api/projects/open` 200 followed by `POST .../camera-geometry/recalculate` 200. This is rendered confirmation of the gate-failing unsupported-CRS acceptance.
- Opening the `EPSG:32617` project visibly reported success and displayed `CRS: EPSG:32617`. Saving showed `Saved Valid CRS rendered probe locally`; backend logs recorded open 200, camera recalculation 200, and save/update 200.
- Browser console inspection after the invalid, unsupported, and valid workflows returned no warning or error entries and no uncaught exception.
- `Recommend CAP`, the Conceptual Wi-Fi Phase 5 layer, and later-phase controls remained disabled.

## Source integrity

- The independent 74-pole project retained exactly 74 authoritative source poles.
- Before/after tuples of source pole ID, longitude, latitude, and raw coordinate text compared equal through invalid attempts and the valid save/open/recalculation workflow.
- No source pole was moved, generated, optimized, or deleted. No file under `Input/` or the frozen catalogs changed, and the engineering/source validator confirmed all supplied-source hashes.

## P4-IR-05 disposition

**FAIL — Major — unsupported project CRS values remain accepted and persistable across shared project paths.**

- **Affected components:** shared project validation and camera-geometry recalculation used by save/update, open/get, bulk configuration, and explicit camera recalculation; rendered open workflow.
- **Reproduction:** take a valid stored project using `EPSG:32617`; submit the same project through save/update with `projected_crs` changed to `EPSG:4326` or `EPSG:2263`; repeat through open, get, bulk configuration, camera recalculation, and lighting calculation.
- **Expected:** every unsupported CRS is rejected with a readable controlled 4xx response, and no invalid attempt overwrites or creates current stored state.
- **Actual:** save/update, open, get, bulk, and camera recalculation return 200. Save/update and bulk persist the unsupported CRS. Only lighting returns 422.
- **Evidence:** independent API status/state matrix, exact stored-byte comparisons, production-rendered `EPSG:4326` open and automatic camera-recalculation 200 access logs, and successful valid `EPSG:32617` control.
- **Gate impact:** gate-failing. The correction resolves the former `NOT-A-CRS` HTTP 500 but does not satisfy the final required unsupported-CRS contract or state-preservation acceptance.

## Regressions, limitations, advisories, and blockers

- **Related regressions:** none confirmed for valid `EPSG:32617`; the full backend suite remained green. The unsupported-CRS behavior is an incomplete correction/contract mismatch, not evidence that this commit broke a previously passing valid path.
- **Other Phase 4 findings:** not reopened. No evidence from this narrow correction implicated P4-IR-01, P4-IR-02, P4-IR-03, P4-IR-04, P4-IR-06, or P4-IR-07.
- **Accepted limitations:** none newly assessed; they were outside this focused retest.
- **Advisory:** the focused test named `camera_geometry_crs_boundary_preserves_approved_behavior` encodes acceptance of unsupported CRS as empty camera geometry and therefore conflicts with this final retest's explicit rejection acceptance.
- **Environmental blockers:** none. The rendered browser exposed console logs but not a separate request ledger; isolated backend access logs supplied exact HTTP evidence.

## Final gate

**FAIL**

- **Can Phase 4 be formally closed?** No.
- **Is further corrective work required?** Yes. Unsupported geographic and projected non-metre project CRS values must be rejected consistently across save/update, open/get, bulk configuration, camera recalculation, and lighting calculation, followed by an independent focused retest.
- **Does this report authorize Phase 5?** No. Phase 5 remains gated and may not be considered for separate authorization while the Phase 4 gate is failed.
