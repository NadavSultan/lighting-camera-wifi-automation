# Phase 4 final P4-IR-05 corrective completion report

Date: 2026-08-26
Role: corrective implementation engineer, not independent QA
Scope: final narrowly scoped P4-IR-05 correction only

## Completion boundary

This uncommitted correction is implemented on the clean default-branch base `0b8a6a3` (`docs: record final Phase 4 focused retest`). It corrects the unsupported project-CRS acceptance confirmed by `docs/phase-4-final-focused-retest-report.md`. This report is implementation evidence, not independent approval. Phase 4 remains unapproved pending one fresh independent focused retest and a master gate decision. Phase 5 and all later phases remain unauthorized and unstarted.

P4-IR-01, P4-IR-02, P4-IR-03, P4-IR-04, P4-IR-06, and P4-IR-07 remain closed and were not changed. No camera projection equation, lighting equation, source pole, coordinate, uploaded byte, fixture/catalog record, project schema shape, or phase gate changed.

## Root cause and correction

The prior camera-service correction controlled syntactically invalid CRS parsing but deliberately returned an empty camera layer for geographic and projected non-metre CRS values. Because shared save, open, get, bulk, and recalculation paths relied on that behavior, `EPSG:4326` and `EPSG:2263` were accepted and could be persisted even though lighting rejected them.

The correction adds one shared CRS module and makes the `Project.projected_crs` model field the authoritative persistence/validation boundary. Every non-null engineering CRS must:

- parse through pyproj;
- be projected; and
- expose at least two metre axes.

Only expected `CRSError` parsing failures and `CRSError`/`ProjError` transformer-construction failures are translated to deterministic `ValueError` validation errors. Camera and lighting reuse the same helper and no broad exception handling was added. Missing CRS remains permitted because the current schema declares `projected_crs` nullable, blank-project creation depends on that state, and all supported migrations preserve it until source import selects an engineering CRS.

## Files changed

- `backend/app/crs.py`: authoritative projected-metre parser and narrow shared transformer construction.
- `backend/app/models.py`: validates every non-null project engineering CRS at model construction and assignment.
- `backend/app/services/camera_geometry.py`: rejects unsupported CRS values and reuses the shared helpers without changing geometry equations.
- `backend/app/services/lighting_calculation.py`: reuses the same helpers without changing lighting equations.
- `backend/tests/test_phase3_camera_geometry.py`: corrects the conflicting empty-layer expectation and adds rejected/valid/missing CRS endpoint matrices.
- `docs/current-status.md`: records implementation completion, current evidence, and the still-open gate.
- `docs/phase-4-final-p4-ir-05-corrective-completion-report.md`: this handoff evidence.

No existing QA report was edited. No file under `Input/`, `data/`, `frontend/`, `schemas/`, or the frozen catalogs changed.

## Automated state-preservation evidence

The focused regression matrix exercises `NOT-A-CRS`, geographic `EPSG:4326`, and projected non-metre `EPSG:2263` independently. For every value it confirms:

- save/update returns 422 and preserves the exact prior valid `project.json` bytes;
- open returns 422, does not change project count, and does not create a project directory;
- get of deliberately invalid stored JSON returns 422 with `Stored project is invalid or corrupt`, never 404, and does not rewrite the fixture;
- bulk configuration against deliberately invalid stored JSON returns 422 and preserves its exact pre-request bytes;
- camera-geometry recalculation returns 422 and preserves the exact prior valid stored bytes; and
- lighting calculation returns 422 and preserves the exact prior valid stored bytes.

No exercised rejected path returns 500. A separate valid matrix confirms `EPSG:32617` returns 2xx through save/update, get, bulk, camera recalculation, lighting calculation, and open; camera recalculation retains two valid footprints and lighting retains a deterministic non-empty point result. The project begins with a real KML import, which continues selecting `EPSG:32617`. A blank-project regression confirms nullable/missing CRS remains accepted through create and get.

## Verification evidence

Commands are run from the repository root with an ignored, worktree-local Python 3.12 virtual environment and pytest temporary directories. Runtime project/catalog data is isolated under pytest temporary roots.

- Focused P4-IR-05 run: PASS, 7 tests.
- Complete backend suite: PASS, 122 tests; one existing non-failing Starlette/httpx2 deprecation warning.
- `scripts/validate_engineering_data.py`: PASS; seven catalog/schema pairs and all supplied-source hashes validated.
- Generated project schema and OpenAPI freshness: PASS through the exact in-memory comparison in the complete backend suite.
- `git diff --check`: PASS.

No frontend or contract-generating file changed. Frontend build, typecheck, lint, and contract regeneration are therefore not required for this backend validation-boundary correction. The full backend suite still checks the checked-in project schema and OpenAPI byte-for-byte against current generation.

After master review identified a documentation-only gate inconsistency, the final `docs/current-status.md` gate paragraph was aligned with the controlling final focused retest and `git diff --check` was rerun. No code, test, generated contract, or existing QA report changed in that follow-up, so the recorded focused and complete backend evidence remains applicable.

## Exact tested Git state

The final verification was run against the uncommitted working tree based on `0b8a6a3`. The working tree contains only the seven files listed above; `.venv/` is ignored test tooling and is not part of the change. No commit was created, as required. `Input/` and customer runtime projects were not modified.

## Limitations and gate

This correction makes no professional photometric-validation claim and does not alter any accepted Phase 4 model limitation. Independent QA must treat this report as an unverified claim set and rerun the complete CRS/status/state matrix using separate temporary storage.

Phase 4 remains unapproved. One fresh independent focused P4-IR-05 retest must pass before a master gate decision. Phase 5 Wi-Fi, CAP, reporting, optimization, proposed poles, and all later work remain unauthorized.
