# Current status

Last updated: 2026-08-27. Phase 1 remains frozen. Phase 2 received an independent **UNCONDITIONAL PASS** and is formally closed. Phase 3 received an independent final focused **PASS** and is formally closed. Phase 4 received independent passing evidence for P4-IR-01 through P4-IR-07 and a master **PASS**; it is formally closed at the explicitly simplified direct-lighting scope. Phase 5 received a focused independent **PASS** for its final QA-01 and QA-02 corrections and a master **PASS**; it is formally closed at the conceptual Wi-Fi scope. Phase 6 planning and all 20 implementation-policy decisions are approved; implementation is unauthorized and unstarted.

## Completed

- All Phase 1 KML/KMZ import, source preservation, map, edit-overlay, save/reopen, and KML export workflows remain operational.
- Project schema `2.5.0` and software/API `0.5.0` migrate `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, `2.3.0`, and `2.4.0` JSON without changing coordinates, discarding legacy overrides, inferring Wi-Fi areas, or guessing a Phoenix 1/Solitaire family.
- The seven approved Phase 1 engineering catalogs remain unchanged at `1.0.0`.
- The operational IES contract is `1.2.0` with immutable file history; the camera contract remains `1.1.0`, and the fixture-model contract is `1.2.0` with the immutable fixed-zero-origin template revision.
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
- Final P4-IR-05 correction enforces the non-null project engineering CRS contract (parseable, projected, metre axes) at the authoritative shared project-model boundary and reuses the same narrow pyproj validation/transformer-construction helpers in camera and lighting services. Blank projects retain the existing permitted missing-CRS state.

## Phase 4 implementation

- Project schema `2.4.0`, software/API `0.4.0`, and IES operational contract `1.2.0` add lighting calculation areas, immutable IES record history, exact project IES pins, deterministic projected grids, Type C direct horizontal illuminance, maintained-lux statistics, and complete disclaimers/provenance.
- Lighting calculation areas are separate from camera priority areas. Explicit create/select/edit/redraw/delete and calculate/recalculate workflows are enabled; Wi-Fi and later controls remain disabled.
- Both supplied Phoenix files are approved for Phoenix 1 LITE/WIFI/SMART and both supplied Solitaire files are approved for Solitaire LITE/WIFI/SMART, enforced by exact SHA family restrictions. Association and per-pole selection remain explicit, with no inferred association or automatic default.
- The result model is intentionally simplified and is not independently validated against AGi32 or another professional photometric reference tool.

## Validation

- Backend: 122 passed; one existing non-failing Starlette/httpx2 deprecation warning.
- Engineering data validator: passed all seven frozen catalog/schema pairs and source hashes.
- Frontend rendered/workflow suite (9 tests), strict TypeScript, and ESLint: passed.
- Production Vinext build: passed with the existing non-failing MapLibre chunk-size advisory.
- Rendered Phase 4 workflow: 74-pole KML, explicit Phoenix/Solitaire IES association and selection, separate Road calculation area, 286-point result, azimuth-driven result change, save/reopen, visible provenance/warnings, unchanged source coordinate, separate empty camera priority collection, Phase 5+ gating, and zero browser-console errors.
- Final Phase 5 validation: 137 backend tests, 13 frontend rendered/workflow tests, strict TypeScript, ESLint, production build, engineering-data validation, and schema/OpenAPI freshness passed. The production-rendered focused retest showed 74 global Wi-Fi circles and metrics together with the exact unavailable-boundary message, no inferred area, and zero browser-console errors.
- Independent QA-02 service/API/persistence probes passed all no-op, meaningful-change, clear, combined, and full-replacement revision/timestamp cases.
- The three Phase 2 seeds validate against their checked-in Draft 2020-12 schemas.
- The final focused NIR-01 retest closed the sole remaining condition with no new findings; `docs/phase-2-nir-01-final-retest-report.md` is the controlling Phase 2 gate evidence.
- The final focused P3-IR-05 retest returned PASS with no confirmed defects or regressions; `docs/phase-3-final-focused-retest-report.md` is the controlling Phase 3 gate evidence.
- The final independent P4-IR-05 retest returned PASS across invalid, unsupported, valid projected-metre, and nullable blank-project CRS states; `docs/phase-4-final-p4-ir-05-independent-retest-2026-08-26.md` and `docs/phase-4-master-gate-decision-2026-08-26.md` are the controlling final Phase 4 gate evidence.

## Known limitations

- Missing authoritative fixture-to-IES/BOM mapping; operational compatibility remains explicitly user-assigned.
- For both supplied Solitaire files, 50 W is the controlling Phase 4 nominal input because the filename and LM-63 numeric input field agree; the preserved internal `60W` identifier remains a visible provenance warning and is not rewritten.
- Missing default lens assignments for SMART camera slots; lens selection remains explicit.
- Current IES calculation support is limited to LM-63-1995/2002 Type C files with `TILT=NONE` and the approved zero-physical-tilt far-field direct-light model.
- Terrain/DEM and occlusion remain excluded. Phase 3 uses the approved zero-offset, fixture-origin optical-center contract and flat local ground plane. Phase 4 simplified direct horizontal illuminance is accepted at its explicit limited scope but is not professionally reference-validated. Phase 5 is accepted only as conceptual projected geometry, not verified RF coverage, performance, capacity, service quality, or standards compliance. Phase 6 CAP implementation, automatic pole placement, and reporting remain deferred and unauthorized.

## Phase 5 closure

- Planning decisions and implementation were separately authorized on 2026-08-26.
- The original independent gate review failed QA-01/R-02 and QA-02/G-03; both received corrective implementation and independent focused passing evidence on 2026-08-27.
- `docs/phase-5-final-focused-retest-2026-08-27.md` and `docs/phase-5-master-gate-decision-2026-08-27.md` are the controlling final Phase 5 evidence.
- No source pole, source coordinate, supplied Input file, frozen catalog, CAP recommendation, or Phase 6 behavior was changed.

## Phase 6 planning approval

- The SOL planning task produced the reviewed planning contract, master Terra implementation prompt, and planning report on 2026-08-27.
- The user explicitly approved all 20 recommended implementation-policy decisions in `docs/phase-6-cap-planning-and-implementation-contract.md`; they are binding for any future Phase 6 implementation.
- This approval does not lock actual Miracle Mile operational values. Product mapping, fixture node dispositions, band/jurisdiction, link distance, node/child/hop limits, counting convention, candidate inventory/feasibility, and redundancy selection remain `unknown` unless separately approved and must be handled by the approved runtime preflight rules.
- `docs/phase-6-master-implementation-prompt.md` remains a future Terra implementation prompt and is not executable until the user grants separate explicit Phase 6 implementation authorization.
- Planning changed documentation only. No application code, tests, schemas, generated contracts, catalogs, supplied Input files, or runtime data were changed.

## Current gate

Phases 1-5 are formally closed. Phase 5 is closed by the master **PASS** in `docs/phase-5-master-gate-decision-2026-08-27.md` after independent closure of QA-01/R-02 and QA-02/G-03. Camera `priority_areas`, lighting `calculation_areas`, and Wi-Fi `wifi_analysis_areas` remain separate collections. Phase 6 planning and all 20 implementation-policy decisions are approved. Phase 6 implementation still requires separate explicit authorization; it is unstarted, and Phase 7 remains gated and unauthorized.
