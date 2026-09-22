# BL-016 camera pixel-density implementation verification

Date: 2026-09-22
Scope: BL-016 / WA-09 only
Base commit: `05257e87b4d6500146239f62f4ebafa4b2217b67`
Verified product tip: `986c6eabc403ed5e5a713f6c0f2d069f310f1677`
Final implementation commit: `8a271bf12b070c5c9883f2b2942ad54c6ace4f77`

## Decision

The BL-016 implementation satisfies the implementation-readiness gate and is handed to Independent QA. Acceptance is not granted here; Independent QA and a separate scoped master PASS remain pending.

## Current deterministic verification

All commands below ran on the BL-016 product tip in this detached linked worktree and exited `0` unless explicitly described as a diagnostic recovery attempt in the execution log.

| Check | Result |
|---|---|
| Backend full suite from `backend/` | PASS, suite reached 100% |
| `scripts/validate_engineering_data.py` | PASS, 8 catalogs |
| `backend/scripts/export_schema.py` | PASS, 5 generated schema paths |
| Frontend frozen install | PASS |
| Frontend full tests | PASS, 107 tests |
| Frontend typecheck / lint / production build | PASS |
| `git diff --check` | PASS |
| `git diff --exit-code -- Input` | PASS |
| `git diff --exit-code -- schemas` after export | PASS |
| Miracle Mile KML SHA-256 | PASS: `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328` |

Exact commands, recovery attempts, and per-task results are preserved in `harness/logs/2026-09-22-bl-016-camera-pixel-density.md`.

## Current live evidence

`harness/verify/run_bl016_camera_pixel_density_live.py` used a fresh temporary `LCWA_DATA_DIR`, FastAPI port `8070`, Vinext production port `3070`, and the supplied Miracle Mile KML. The current JSON record is `harness/verify/2026-09-22-bl-016-camera-pixel-density-live.json`.

- Import proved 74 preserved source poles, `existing-poles`, and `EPSG:32617`.
- Eight configured camera slots resolved and calculated valid bands; 30 overlap regions were produced.
- The default profile and ten-row Option A legend, including `0.58` opacity, matched the contract.
- A controlled `422` calculation failure preserved stored bytes.
- A significant edit retained but hid the stale result and emitted the exact stale message; recalculation restored current state.
- KML export and the Phase 7 report package both succeeded.
- Chrome headless rendered the production shell with exit code `0`; the production server logs contain no startup failure, and both isolated listeners were released.

The browser screenshot proves the production shell, while the complete engineering-state workflow is proved by real production API calls plus deterministic frontend state/map tests. Independent QA must still perform the interactive rendered walkthrough, including both backgrounds, all three supplied lenses, inspection, close/reopen, and cross-layer regression. This boundary is intentional and is not represented as Independent-QA evidence.

## Acceptance mapping

| ID | Status | Current objective evidence |
|---|---|---|
| `BL016-01` | PASS | migration/model tests, full backend suite, generated project schema |
| `BL016-02` | PASS | profile validation/default tests and live default-profile assertion |
| `BL016-03` | PASS | canonical legend JSON/schema/validator tests, endpoint and live legend assertion |
| `BL016-04` | PASS | analytic supplied-lens equation tests and valid live camera bands |
| `BL016-05` | PASS | analytic envelope/midpoint/projected-metre/128-gon cap tests |
| `BL016-06` | PASS | pinned revision, provenance, and disabled-slot tests |
| `BL016-07` | PASS | invalid-camera isolation and explicit-warning tests |
| `BL016-08` | PASS | canonical band partition, ordering, rounding, and repeatability tests |
| `BL016-09` | PASS | analytic two-/three-camera overlap, contributor, winner, and tie tests |
| `BL016-10` | PASS | exact camera/overlap/vertex/serialized-byte boundary tests |
| `BL016-11` | PASS | fingerprint inclusion/exclusion and deterministic identity tests |
| `BL016-12` | PASS | stale/current lifecycle tests and live stale/recalculate assertions |
| `BL016-13` | PASS | atomic API, identity/validation, and byte-preserving failure tests plus live `422` assertion |
| `BL016-14` | PASS | frontend panel/API/view tests and source-integrated explicit calculate flow |
| `BL016-15` | PASS | exact ten-band MapLibre style/order/opacity and visibility tests |
| `BL016-16` | PASS | overlap dot/dash/label, winner/contributor GeoJSON, and safe DOM inspection tests |
| `BL016-17` | PASS | backend/frontend persistence and stale/recalculate tests; live retain/hide/replace assertion |
| `BL016-18` | PASS | report compatibility tests and live Phase 7 package assertion; no new report visualization |
| `BL016-19` | PASS | Phase 3/full regressions, KML export, existing-pole assertion, Input diff and exact source hash |
| `BL016-20` | PASS | deterministic/live evidence, exact implementation identity, clean readiness manifest, and truthful handoff |

## Warnings and limitations

- Starlette/httpx and anyio emit known dependency deprecation warnings.
- Vinext reports the existing large-chunk advisory, plugin timing notices, and unknown-route classification advisory during production build.
- Git may report CRLF conversion warnings on Windows; `git diff --check` passes.
- The first Chrome launch returned `2147483651`; an isolated user-data directory with crash helpers disabled succeeded. An earlier live-run attempt encountered an orphaned local frontend listener; that exact test listener was stopped, the runner was strengthened to fail closed on occupied ports and record listener identities, and the clean rerun passed. Superseded attempts are not acceptance evidence.

## Gate

- Implementation: complete and ready for Independent QA.
- Independent QA: pending.
- Scoped master decision: pending.
- Seal: absent and unauthorized.
- Merge, push, BL-019/020, Phase 8, and later work: unauthorized.
