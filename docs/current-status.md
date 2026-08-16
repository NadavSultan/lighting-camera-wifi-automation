# Current status

Last updated: 2026-08-16. Phase 1 remains frozen. Phase 2 received an independent **UNCONDITIONAL PASS** and is formally closed. The independent Phase 3 corrective retest returned **PASS WITH CONDITIONS**: P3-IR-01, P3-IR-02, P3-IR-03, P3-IR-04, and P3-IR-06 are closed; the remaining P3-IR-05 north-boundary rounding defect has now received a final focused correction and local verification. Phase 3 is not declared approved and awaits an additional independent focused QA retest. Phase 4 and later work remains unauthorized and unstarted.

## Completed

- All Phase 1 KML/KMZ import, source preservation, map, edit-overlay, save/reopen, and KML export workflows remain operational.
- Project schema `2.3.0` migrates `1.0.0`, `2.0.0`, `2.1.0`, and `2.2.0` JSON without changing coordinates, discarding legacy overrides, or guessing a Phoenix 1/Solitaire family.
- The seven approved Phase 1 engineering catalogs remain unchanged at `1.0.0`.
- Operational IES and camera contracts remain `1.1.0`; the fixture-model contract advances additively to `1.2.0` for the immutable fixed-zero-origin template revision.
- Six required fixture models are seeded with structured family, variant, and capabilities.
- Phoenix 1 SMART uses two slots at -70/+70 degrees; Solitaire SMART uses -60/+60 degrees. Both use positive 35-degree downward tilt.
- Fixture, camera, lens, and mounting-template revisions are immutable. Pole assignments pin exact revisions and adopt newer revisions only explicitly.
- IES upload preserves original bytes and filename, validates supported LM-63 Type C data, hashes the file, parses metadata, and supports explicit many-to-many fixture associations.
- Per-pole and bulk configuration supports model, IES, height, fixture azimuth, Wi-Fi data, and SMART camera/lens assignments without editing source coordinates; bulk targets may be all poles, one folder, or a manual multi-pole selection.
- Failed IES uploads are retained as inactive invalid/unsupported records with errors; valid records may carry operational warnings.
- Referenced equipment deactivation is conflict-safe, camera/lens compatibility is reciprocal with the lens relation authoritative, and per-slot overrides have an explicit restore-to-template action.
- Catalog-management and model-dependent pole-configuration UI is available through the **Catalogs** toolbar action and properties inspector.

## Corrective scope

- Priority-area rename preserves geometry; explicit redraw begins empty and validates before replacement.
- Generated project schema/OpenAPI are regenerated and exact in-memory freshness tested.
- Enabled-camera warnings are globally visible and represented on the map under the Warnings layer.
- Footprints persist exact H/V FOV and mounting geometry-contract version; UI azimuths use deterministic engineering formatting.
- Final P3-IR-05 correction normalizes after three-decimal rounding so display and intentional map-handle edits can never produce `360`; authoritative backend values are not rewritten by presentation formatting.

## Validation

- Backend: 85 passed; one existing non-failing Starlette/httpx2 deprecation warning.
- Engineering data validator: passed all seven frozen catalog/schema pairs and source hashes.
- Frontend rendered/workflow suite (6 tests), strict TypeScript, and ESLint: passed.
- Production Vinext build: passed with the existing non-failing MapLibre chunk-size advisory.
- The three Phase 2 seeds validate against their checked-in Draft 2020-12 schemas.
- The final focused NIR-01 retest closed the sole remaining condition with no new findings; `docs/phase-2-nir-01-final-retest-report.md` is the controlling Phase 2 gate evidence.

## Known limitations

- Missing authoritative fixture-to-IES/BOM mapping; operational compatibility remains explicitly user-assigned.
- Unresolved Solitaire 50 W / 60 W filename/header versus internal-model conflict.
- Missing default lens assignments for SMART camera slots; lens selection remains explicit.
- Current IES upload support is limited to LM-63-1995/2002 Type C files with `TILT=NONE`.
- Terrain/DEM and occlusion remain excluded. Phase 3 uses the approved zero-offset, fixture-origin optical-center contract and flat local ground plane; Wi-Fi coverage, illuminance, CAP recommendations, automatic pole placement, and reporting remain deferred.

## Current gate

Return the final focused P3-IR-05 implementation commit and `docs/phase-3-final-corrective-completion-report.md` for an additional independent focused QA retest. Do not declare Phase 3 approved and do not begin Phase 4.
