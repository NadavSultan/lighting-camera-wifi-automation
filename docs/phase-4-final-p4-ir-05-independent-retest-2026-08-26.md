# Phase 4 P4-IR-05 independent final retest

Date: 2026-08-26
Role: independent final QA engineer
Disposition: **PASS for P4-IR-05**

## Baseline and environment

- Exact tested HEAD: `a313a6c617fa91c9bfd3eff85842205851954717` (`fix: enforce projected metre project CRS`), on local `main`.
- Baseline was clean before testing: `git status --short` returned no entries. It was clean again after temporary probes and pytest directories were removed.
- Windows 11 host; bundled Python 3.12 runtime with isolated temporary installation of the declared backend/dev dependencies; FastAPI, Pydantic, PyProj, Shapely, pytest, and httpx were available.
- All project and catalog stores used fresh temporary directories. `Input/`, customer runtime data, frozen catalogs, source bytes, schemas, and implementation/tests were not modified.
- No isolated frontend runtime was available (`frontend/node_modules` is absent); production-rendered/browser-console smoke was therefore not run.

## Commands

- Independently authored temporary API/store probe using `TestClient`, a fresh KML import, fresh temporary stores, byte comparisons, deliberately invalid stored JSON, model/service probes, and controlled exception injection. Probe passed and was removed.
- Focused tests: `python -m pytest -q tests/test_phase3_camera_geometry.py -k 'crs'` — **14 passed**.
- Focused lighting test: `python -m pytest -q tests/test_phase4_lighting_calculation.py -k 'invalid_crs'` — **1 passed**.
- Complete backend suite: `python -m pytest tests` — **122 passed, 1 warning** (known non-failing Starlette/httpx deprecation warning).
- Engineering validator: `python scripts/validate_engineering_data.py` — **passed** all seven catalog/schema pairs and supplied-source hashes.
- `git diff --check` — **passed**.

## Independent CRS/state matrix

| CRS state | Save/update | Open | Invalid stored get | Bulk | Camera recalc | Lighting | State/result disposition |
|---|---:|---:|---:|---:|---:|---:|---|
| `NOT-A-CRS` | 422 | 422 | 422 | 422 | 422 | 422 | readable project-engineering-CRS errors; no 500, 404 mislabel, mutation, or invalid project creation |
| `EPSG:4326` geographic | 422 | 422 | 422 | 422 | 422 | 422 | rejected consistently; prior valid bytes and invalid fixture bytes preserved |
| `EPSG:2263` projected non-metre | 422 | 422 | 422 | 422 | 422 | 422 | rejected consistently; prior valid bytes and invalid fixture bytes preserved |
| `EPSG:32617` projected metre | 2xx | 2xx | n/a | 2xx | 2xx | 2xx | two valid camera footprints and deterministic non-empty lighting result; material save/open state equivalent |
| missing CRS blank project | accepted | accepted | n/a | n/a | accepted empty state | no CRS invented | nullable blank-project behavior retained |

The independently imported 74-pole Miracle Mile KML selected `EPSG:32617`. The valid lighting control produced four deterministic grid points; camera recalculation produced two valid footprints. The focused suite also directly confirms the former conflicting test now rejects `EPSG:4326` and `EPSG:2263`, rather than accepting empty camera geometry.

## Boundary and defense-in-depth evidence

- `Project(projected_crs=...)` accepted only `EPSG:32617` among the tested non-null values; invalid, geographic, and non-metre projected values raised validation errors.
- Assignment validation rejected `project.projected_crs = "EPSG:4326"`.
- A `model_copy(update=...)` bypassed model validation in a controlled service-level probe; camera geometry still rejected the geographic CRS.
- The shared transformer helper translated an injected `ProjError` to the controlled `ValueError`. An injected unrelated `RuntimeError("programming defect")` propagated unchanged, confirming no broad exception swallowing.

## Byte preservation and integrity

For each rejected CRS, the probe compared the exact prior valid `project.json` bytes after rejected save/update, camera recalculation, and lighting calls. Rejected open left project count unchanged and created no project directory. A deliberately invalid stored fixture was read through get and bulk paths; both returned controlled 422 and left its bytes unchanged. No invalid-store response was mislabeled 404.

Source-integrity checks passed: the imported project retained 74 authoritative source poles, including source IDs, longitude/latitude, and raw coordinate text through the valid and rejected workflows. The engineering validator confirmed all supplied-source hashes and frozen catalog/schema pairs. No protected tree showed a diff.

## Regressions, claims, limitations, and blockers

No related regression was demonstrated in P4-IR-01, P4-IR-02, P4-IR-03, P4-IR-04, P4-IR-06, or P4-IR-07; they were not reopened. Implementation reports and implementation-authored tests were treated as unverified; this disposition relies on the separate probe plus the required regression commands.

The only limitation is environmental: no frontend dependency/runtime was present for production-rendered smoke or browser-console verification. This does not block the confirmed backend disposition. The known Starlette/httpx deprecation warning is non-failing.

## Gate statement

P4-IR-05 independently **PASSes** its stated acceptance contract: every non-null project engineering CRS tested was either valid projected metres or rejected with controlled 422 responses across all affected paths; blank-project missing CRS remains permitted.

Phase 4 is **eligible for a later master gate decision**, but this report does not close Phase 4 and does not authorize Phase 5 or any later phase.

## Master handoff

Hand off P4-IR-05 as independently passed at `a313a6c`; retain Phase 4 governance under the separate master gate decision, with Phase 5 still unauthorized.
