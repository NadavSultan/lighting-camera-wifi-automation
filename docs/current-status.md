# Current status

Last updated: 2026-08-14. Phases 1 and 2 are implemented, tested, production-built, and accepted by the user. Phase 3 and later work remains unauthorized.

## Completed

- All Phase 1 KML/KMZ import, source preservation, map, edit-overlay, save/reopen, and KML export workflows remain operational.
- Project schema `2.0.0` migrates Phase 1 JSON without changing coordinates or guessing a Phoenix 1/Solitaire family.
- The seven approved Phase 1 engineering catalogs remain unchanged at `1.0.0`.
- Three separate operational Phase 2 contracts manage fixture models, IES uploads/associations, and cameras/lenses.
- Six required fixture models are seeded with structured family, variant, and capabilities.
- Phoenix 1 SMART uses two slots at -70/+70 degrees; Solitaire SMART uses -60/+60 degrees. Both use positive 35-degree downward tilt.
- Catalog mounting-template revisions are immutable. Pole assignments pin a revision and adopt newer revisions only explicitly.
- IES upload preserves original bytes and filename, validates supported LM-63 Type C data, hashes the file, parses metadata, and supports explicit many-to-many fixture associations.
- Per-pole and bulk configuration supports model, IES, height, fixture azimuth, Wi-Fi data, and SMART camera/lens assignments without editing source coordinates.
- Catalog-management and model-dependent pole-configuration UI is available through the **Catalogs** toolbar action and properties inspector.

## Validation

- Backend: 37 passed; one existing non-failing Starlette/httpx2 deprecation warning.
- Engineering data validator: passed all seven frozen catalog/schema pairs and source hashes.
- Frontend rendered-output suite, strict TypeScript, and ESLint: passed.
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

Phase 2 is closed and accepted. Do not begin Phase 3 camera-ground-geometry work without a new explicit authorization and the missing mechanical/terrain assumptions.
