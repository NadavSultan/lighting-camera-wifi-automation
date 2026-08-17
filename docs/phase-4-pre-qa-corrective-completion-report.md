# Phase 4 pre-QA corrective completion report

Date: 2026-08-17  
Role: dedicated Phase 4 pre-QA correction engineer  
Scope: P4-PREQA-01 and P4-PREQA-02 only

## Completion boundary

The corrective implementation is commit `5ada5665ed26a85210da1ff1d4fa49d787cf276d` (`fix: preserve historical IES revision pins`). This report records implementation and regression evidence, not independent QA approval. Phase 4 remains unapproved pending separate independent QA and a master gate decision. Phase 5 conceptual Wi-Fi and all later work remain unauthorized and were not implemented.

The baseline Phase 4 implementation remains `eafd320369600ff4c8d32b8dc32c80e1e81b3d24`, with its completion report committed at `9a7e5a4`. The original `docs/phase-4-completion-report.md` blob is unchanged: both `9a7e5a4` and the corrective implementation commit resolve it to Git blob `2c44e6096fdf19a8dc2aa33b4762e17419e56db3`.

## Root cause and correction

`validate_project_configuration` and the lighting eligibility service indexed only `IesLibrary.files`. Both then required a project pin to equal the current record revision. Although contract `1.2.0` already persisted immutable `file_history`, neither path resolved an exact historical `(ies_file_id, ies_file_revision)`. Advancing a current record could therefore exclude a legally pinned pole or tempt an unsafe current-record fallback.

One shared resolver in `backend/app/services/ies.py` now:

- requires an explicit revision pin;
- finds exactly one current lifecycle record for the stable IES ID;
- requires that current record to remain active and valid;
- requires exactly one active explicit association to the pinned fixture model;
- resolves exactly one `(id, revision)` across current `files` plus immutable `file_history`;
- revalidates the pinned record's original Base64 bytes, SHA-256, validation state, and parsed metadata before use;
- rejects missing, ambiguous, inactive, invalid, unsupported, or corrupt pins with no substitution of current bytes.

Configuration validation and lighting calculation call this same resolver. The pinned record, not the current record, supplies photometric bytes, parsed metadata, original filename, SHA-256, preserved warnings, and numerical output. The current record and current association supply lifecycle safety only.

Explicit bulk assignment/reselection now requires the IES library, accepts only a current active valid record, and writes that current revision. A recalculation or ordinary save never changes an existing pin. Supported API attempts to deactivate a referenced IES file, deactivate its referenced association, or remove that association return `409 Conflict`.

## Exact revision-1/revision-2 evidence

The new API/service regression creates revision 1 under stable ID `ies-immutable-history-test`, with a constant 1,000 cd distribution, SHA-256 identity, filename `revision-1.ies`, parsed Type C metadata, and a preserved revision-1 warning. At 10 m nadir it calculates exactly 10 lx.

The test advances the same ID to revision 2 using different bytes, a different SHA-256, filename `revision-2.ies`, a different warning, and a 2,000 cd distribution, while storing revision 1 unchanged in `file_history`.

- Project save and calculation retain pin revision 1.
- Recalculation retains identical ordered point results and does not mutate the pin.
- Provenance retains revision 1, its SHA-256, original filename, complete parsed metadata, and its preserved warning.
- The maintained nadir result remains 10 lx after revision 2 becomes current.
- Explicit bulk reselection of the same IES ID changes the pin to revision 2.
- The next calculation records revision-2 identity/provenance and produces 20 lx.
- Removing revision 1 from history makes a revision-1 project save fail `422` with the explicit statement that current revision was not substituted.
- New assignments to inactive or invalid current records fail `422`.
- Referenced IES and association deactivation/removal fail `409`.

Catalog persistence reloads `file_history` with the exact revision-1 ID, revision, and SHA. The five supported project-migration cases additionally assert that existing exact IES pins survive migration.

## Files and contracts changed

- `backend/app/services/ies.py`: shared exact current/history resolver and integrity/lifecycle rules.
- `backend/app/services/configuration.py`: shared validation and current-only explicit assignment/reselection.
- `backend/app/services/lighting_calculation.py`: exact pinned historical photometry and provenance.
- `backend/app/main.py`: current IES catalog passed to bulk selection and conflict-safe IES/association lifecycle operations.
- `backend/app/models.py`: additive parsed IES metadata in fixture calculation provenance.
- `backend/tests/test_phase4_lighting_calculation.py`: revision-1/revision-2, provenance, missing-history, lifecycle, new-assignment, persistence, and migration regressions.
- `frontend/app/lib/types.ts` and `frontend/app/components/EngineeringWorkspace.tsx`: typed and visible parsed photometry metadata in existing calculation provenance.
- `schemas/project.schema.json` and `schemas/openapi.json`: regenerated exact contracts for the additive provenance field.
- Current governance/handoff documents: `docs/current-status.md`, `docs/decision-log.md`, `docs/implementation-plan.md`, `docs/engineering-assumptions.md`, `docs/engineering-open-questions.md`, and `docs/risk-register.md`.

Project schema remains `2.4.0`, software/API remains `0.4.0`, and the IES operational contract remains `1.2.0`. No frozen catalog or seed data changed.

## Documentation accuracy corrections

Current-state documentation now consistently states that:

- project schema is `2.4.0` and software/API is `0.4.0`;
- the IES operational contract is `1.2.0`;
- both supplied Phoenix files are approved for Phoenix 1 LITE/WIFI/SMART and both supplied Solitaire files for Solitaire LITE/WIFI/SMART, while association and pole selection remain explicit and no automatic default exists;
- 50 W controls for both supplied Solitaire files and the preserved internal `60W` identifier remains a visible warning;
- simplified direct horizontal illuminance is implemented but awaits independent QA;
- Phase 5 Wi-Fi and all later work remain deferred and unauthorized.

Only genuine current-state contradictions were corrected. Historical QA, retest, corrective-completion, and original Phase 4 completion reports were not rewritten.

## Verification results

- Full backend suite: PASS, 101 tests. This includes 28 Phase 2 tests, 34 Phase 3 tests, and 16 Phase 4 tests. The existing non-failing Starlette/httpx2 deprecation warning remains.
- Focused Phase 2 plus Phase 4 catalog/revision run: PASS, 44 tests.
- Revision-1/revision-2 historical-pin API/service regression: PASS.
- Five supported project migrations (`1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, `2.3.0`): PASS with exact IES pin preservation and empty inferred Phase 4 collections for legacy inputs.
- Exact in-memory project JSON Schema and OpenAPI freshness: PASS in the backend suite.
- Operational catalog schema/seed freshness and `file_history` persistence: PASS.
- Engineering/source validator: PASS; seven frozen catalogs match schemas and all supplied-source hashes, IES parses/references/hashes, and engineering invariants remain valid.
- Frontend rendered/workflow tests: PASS, 7 tests.
- Strict TypeScript: PASS.
- ESLint: PASS.
- Production Vinext build: PASS; existing non-failing large-chunk and route-classification advisories remain.
- `git diff --check`: PASS. CRLF conversion notices are advisory; no whitespace error was reported. `frontend/app/lib/phase4-workflows.mjs` therefore required no behavior-neutral EOF edit.

## Preservation and scope evidence

Implementation commit `5ada5665ed26a85210da1ff1d4fa49d787cf276d` changes no file under `Input/` or `data/`, no runtime project, no customer source pole or raw coordinate, and no frozen Phase 1 catalog. The engineering/source validator confirms all supplied-source hashes. Full Phase 1-3 regressions remain green.

The correction does not change lighting equations, grids, orientation, supplied compatibility restrictions, camera geometry, or camera `priority_areas`. Lighting `calculation_areas` and camera `priority_areas` remain separate. No Wi-Fi engine, CAP recommendation, reporting, proposed-pole, standards-compliance, optimization, or other Phase 5+ functionality was added.

## Known limitations and QA handoff

No AGi32 or other professional-reference comparison was introduced. The simplified-model disclaimer and all original Phase 4 calculation exclusions remain in force. This corrective task did not perform independent QA.

Independent QA should verify the exact-pin resolver against current and historical records, integrity failures, lifecycle conflicts, explicit reselection, save/open/recalculate behavior, provenance identity, catalog/project migrations, generated contracts, source preservation, camera-priority separation, and Phase 5+ gating. Phase 4 must not be declared approved without that independent evidence and an explicit master gate decision.
