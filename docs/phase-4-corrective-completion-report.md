# Phase 4 corrective completion report

Date: 2026-08-17  
Role: dedicated Phase 4 corrective implementation engineer  
Scope: confirmed findings P4-IR-01 through P4-IR-07 only

## Completion boundary

The corrective implementation is commit `50fa336eee8a1619308aa9d25c189da8d0e4a3cd` (`fix phase 4 QA findings P4-IR-01 through P4-IR-07`). This report records implementation and regression evidence, not independent approval. Phase 4 remains unapproved pending a separate independent corrective retest and an explicit master gate decision. Phase 5 conceptual Wi-Fi and all later work remain unauthorized and were not implemented.

The implementation baseline remains `eafd320369600ff4c8d32b8dc32c80e1e81b3d24`; the pre-QA corrective baseline remains `5ada5665ed26a85210da1ff1d4fa49d787cf276d`.

## Finding-by-finding resolution

### P4-IR-01 — stale lighting results

Each new result carries a canonical SHA-256 fingerprint of the selected projected CRS, calculation-area inputs and polygon revision, authoritative source origins, effective active/type/height inputs, and lighting-significant fixture/model/template/IES/azimuth/properties pins. A shared backend invalidator removes any missing-area or fingerprint-mismatched result and resets its area state. Save, open, get, bulk, camera-recalculation, and lighting-calculation API paths invoke that rule. The frontend immediately clears all lighting results after a calculation-significant per-pole, restore, or bulk edit. Engineering notes, camera overrides, and Wi-Fi configuration are excluded from the frontend significance comparison.

Focused API and frontend regressions cover height, azimuth, fixture model, exact IES pin, active state, restore, bulk mutation, note-only edits, and save/reopen. The tests confirm that recalculation inputs cannot leave stale provenance/results current or persisted.

### P4-IR-02 — historical metadata versus immutable bytes

The shared exact-pin resolver now decodes and reparses the pinned revision's immutable original bytes with the authoritative non-recursive IES parser. It compares canonical parsed metadata exactly with persisted metadata and rejects missing or mismatched metadata without using current bytes or metadata. Only the canonical reparsed metadata is returned after equality succeeds.

Focused cases cover a valid unchanged historical record, mismatched input watts, mismatched angle/count/domain metadata, missing metadata, and current-versus-historical non-substitution. The earlier revision-1/revision-2 exact-pin behavior remains intact.

### P4-IR-03 — approved C-plane domains and seam continuity

IES semantic validation now accepts only one rotationally symmetric plane, complete `0-90`, complete `0-180`, or complete `0-360` Type C domains. Other partial domains are rejected. A complete `0-360` distribution must have matching C0/C360 candela rows within `1e-9` relative or `1e-9 cd` absolute tolerance; contradictory seam rows are rejected and are never averaged or overwritten. Existing finite, strict-monotonic angle checks remain in force.

Focused cases cover all four approved forms, unsupported `[10,20]`, a discontinuous seam, and parsing of all four supplied IES files.

### P4-IR-04 — non-finite calculation safety

All strict Pydantic models now reject NaN and infinity. IES validation rejects non-finite scaled intensity, including the adversarial `1e308` candela multiplied by a `1e308` multiplier. The calculation engine requires finite scaled/interpolated intensity, per-fixture illuminance, summation, maintenance scaling, per-fixture retained contributions, statistics, ratios, projected coordinates, and WGS84 coordinates. Expected numerical failures return controlled `422` responses; no non-finite lux is serialized as `null`. A failed calculation does not save its working copy, so an earlier valid project/result remains reopenable. Project retrieval distinguishes missing projects (`404`) from invalid/corrupt stored projects (`422`).

### P4-IR-05 — invalid CRS and subnormal spacing

The project contract now requires grid spacing from `0.01 m` through `1000 m`; `0.01 m` is accepted exactly and `5e-324` is rejected. Before grid generation, the engine validates that the CRS parses, is projected, and has metre axes. Expected pyproj construction/transformation errors and arithmetic overflows become readable `422` calculation-input errors. Tests cover invalid CRS text, geographic `EPSG:4326`, non-metre projected `EPSG:2263`, subnormal spacing, the exact lower boundary, and preservation of the previously stored project/result after failure.

### P4-IR-06 — boundary-tolerance candidate enumeration

Grid lattice index bounds are expanded by `BOUNDARY_TOLERANCE_M` before `ceil`/`floor` enumeration, while the existing buffered `covers` acceptance remains authoritative. Ordering stays deterministic Y-then-X, identities and point safeguards are unchanged, and no duplicates are introduced. Tests exercise edges and vertices at minimum and maximum bounds, exactly on the boundary, `9.99e-8 m` outside as accepted, and `1.001e-7 m` outside as rejected, plus an ordinary unchanged grid.

### P4-IR-07 — lighting-specific polygon wording

The Phase 4 helper retains the shared geometry validator but translates every relevant error to “calculation area” or “lighting calculation area.” Phase 3 priority-area wording and behavior are unchanged. Frontend tests cover fewer than three vertices, duplicate-only vertices, self-intersection, degeneracy, non-finite coordinates, and WGS84 bounds, and assert that Phase 4 output never says “priority area.”

## Minimal files and contracts changed

- Backend runtime: `backend/app/main.py`, `backend/app/models.py`, `backend/app/services/configuration.py`, `backend/app/services/ies.py`, and `backend/app/services/lighting_calculation.py`.
- Focused backend regressions: `backend/tests/test_phase4_lighting_calculation.py`.
- Frontend runtime and types: `frontend/app/components/EngineeringWorkspace.tsx`, `frontend/app/lib/phase4-workflows.mjs`, and `frontend/app/lib/types.ts`.
- Focused frontend regressions: `frontend/tests/rendered-html.test.mjs`.
- Regenerated contracts: `schemas/project.schema.json` and `schemas/openapi.json`. The checked-in IES schema remained byte-current and did not require a content change.
- Current technical/governance documentation: `docs/architecture.md`, `docs/current-status.md`, `docs/data-model.md`, and `docs/photometric-conventions.md`.
- Preserved QA evidence newly tracked unchanged: `docs/phase-4-integration-review-and-qa.md`.

Project schema remains `2.4.0`, software/API remains `0.4.0`, and the operational IES contract remains `1.2.0`.

## Automated verification

- Focused Phase 4 backend suite: PASS, 31 tests, including new P4-IR-01 through P4-IR-06 cases and all four supplied IES smoke cases.
- Complete backend suite: PASS, 116 tests. Existing Phase 1, Phase 2 catalog/revision/assignment/bulk behavior, Phase 3 camera geometry/priority-area behavior, Phase 4 migrations, and the exact generated project schema/OpenAPI/IES-schema freshness checks are included. One existing non-failing Starlette/httpx2 deprecation warning remains.
- Supported migrations from `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, and `2.3.0`: PASS through the backend suite.
- Engineering/source validator: PASS for all seven frozen catalog/schema pairs, source hashes, IES parses/references/hashes, and engineering invariants.
- Frontend rendered/workflow tests: PASS, 9 tests, including P4-IR-01 and P4-IR-07 cases.
- Strict TypeScript: PASS.
- ESLint: PASS.
- Production Vinext build: PASS. Existing non-failing route-classification and MapLibre chunk-size advisories remain.
- `git diff --check`: PASS; CRLF conversion notices were advisory and no whitespace error was reported.

The complete regression/contract set was run once after the focused corrections were complete, as requested.

## Rendered corrective smoke evidence

A production build was served against an isolated local API/catalog/project directory and exercised through the real rendered application with the supplied 74-pole KML preserved inside a temporary project and a synthetic supported constant-intensity IES record.

- A selected Road calculation area calculated 9 deterministic points: `Eavg 9.25 lx`, `Emin 8.71 lx`, and `Emax 9.99 lx` from one eligible fixture.
- Changing the selected contributing pole height from `10 m` to `12 m` immediately changed the area display to `Not calculated`; the prior 9-point statistics disappeared before save.
- Saving and reopening through the project API retained height `12 m`, area state `not-calculated`, and zero lighting results. The authoritative first-pole raw coordinate remained `-80.26234411,25.74920999,0`.
- Entering grid spacing `5e-324` produced the controlled rendered message `Grid spacing must be finite, at least 0.01 m, and no greater than 1000 m`. The stored project remained readable with its prior valid `2.0 m` spacing and zero stale results.
- Starting redraw with an empty draft preserved the stored polygon and produced `A lighting calculation area requires at least three distinct vertices.`
- Conceptual Wi-Fi P5, recommended CAP P6, and CAP connections P6 controls remained disabled; stored Wi-Fi coverage remained false.
- Browser console inspection returned no errors.

## Evidence preservation and scope

The QA report SHA-256 was verified before implementation and after commit as exactly `A2857EA33C5A92A2836575E51CD490D57EF9780A9DFF4BCF6C4E4953BFDDD96A`. It is tracked at `docs/phase-4-integration-review-and-qa.md` without modification.

The original Phase 4 completion report remains unchanged at Git blob `2c44e6096fdf19a8dc2aa33b4762e17419e56db3`. The pre-QA corrective completion report remains unchanged at Git blob `60509a9d7dde7410c28607f8b86a892811a56eb0`. No file under `Input/` or `data/` changed. Customer coordinates, exact source/upload bytes, seven frozen Phase 1 catalogs, camera geometry, and camera `priority_areas` were not modified. Lighting `calculation_areas` remain separate.

## Remaining accepted limitations and handoff

The approved simplified direct horizontal Type C model and its equations/orientation are unchanged. Terrain, slope, occlusion, interreflection, reflected light, near-field luminous-opening geometry, physical luminaire tilt, atmospheric effects, standards-compliance evaluation, targets/recommendations, proposed poles, and optimization remain excluded. No AGi32 or other professional-reference comparison was added, so every result retains the unvalidated-reference disclaimer.

No Phase 5 Wi-Fi calculation, CAP placement/recommendation, reporting, proposed-pole, or later-phase functionality was performed. Independent QA should now perform a focused corrective retest of P4-IR-01 through P4-IR-07 against implementation commit `50fa336eee8a1619308aa9d25c189da8d0e4a3cd`, then return evidence for a separate master gate decision. This report does not declare Phase 4 approved.
