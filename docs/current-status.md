# Current status

Last updated: 2026-08-15. Phase 1 remains frozen. Phase 2 received an independent **UNCONDITIONAL PASS** and is formally closed. Phase 3 camera geometry is explicitly authorized and in progress; Phase 4 and later work remains unauthorized.

## Completed

- All Phase 1 KML/KMZ import, source preservation, map, edit-overlay, save/reopen, and KML export workflows remain operational.
- Project schema `2.2.0` migrates `1.0.0`, `2.0.0`, and `2.1.0` JSON without changing coordinates, discarding legacy overrides, or guessing a Phoenix 1/Solitaire family.
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

## Validation

- Backend: 51 passed; one existing non-failing Starlette/httpx2 deprecation warning.
- Engineering data validator: passed all seven frozen catalog/schema pairs and source hashes.
- Frontend rendered/workflow suite (3 tests), strict TypeScript, and ESLint: passed.
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

Implement and validate Phase 3 camera-ground geometry only under the approved fixed-mounting, explicit-lens, flat-ground, projected-CRS contract. Stop after the Phase 3 completion report and recommend an independent session “92 – Phase 3 Integration Review & QA”. Do not begin Phase 4.
