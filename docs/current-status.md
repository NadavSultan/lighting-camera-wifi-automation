# Current status

Last updated: 2026-08-15. Phase 1 remains frozen. The Phase 2 corrective implementation for independent QA findings IR-01 through IR-11 is implemented and locally validated; acceptance is pending independent QA retesting. Phase 3 and later work remains unauthorized.

## Completed

- All Phase 1 KML/KMZ import, source preservation, map, edit-overlay, save/reopen, and KML export workflows remain operational.
- Project schema `2.1.0` migrates Phase 1 and initial Phase 2 JSON without changing coordinates or guessing a Phoenix 1/Solitaire family.
- The seven approved Phase 1 engineering catalogs remain unchanged at `1.0.0`.
- Three separate operational Phase 2 contracts at `1.1.0` manage fixture models, IES uploads/associations, and cameras/lenses.
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

## Known limitations

- Missing authoritative fixture-to-IES/BOM mapping; operational compatibility remains explicitly user-assigned.
- Unresolved Solitaire 50 W / 60 W filename/header versus internal-model conflict.
- Missing physical camera XYZ offsets.
- Missing default lens assignments for SMART camera slots; lens selection remains explicit.
- Current IES upload support is limited to LM-63-1995/2002 Type C files with `TILT=NONE`.
- Terrain, FOV/pixel-density calculations, Wi-Fi coverage, illuminance, CAP recommendations, automatic pole placement, and reporting remain deferred.

## Next gate

Return Phase 2 to independent QA for retesting against IR-01 through IR-11. Do not begin Phase 3 camera-ground-geometry work.
