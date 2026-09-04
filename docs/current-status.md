# Current status

Phase state last changed: 2026-09-04. Documentation consistency reviewed: 2026-09-04. Phases 1-6 retain their prior accepted closure. Phase 7 reporting/export implementation is complete through M0-M9 and awaits independent QA / master gate / seal.

## Completed

- All Phase 1 KML/KMZ import, source preservation, map, edit-overlay, save/reopen, and KML export workflows remain operational.
- Project schema `2.7.0` and software/API `0.7.0` migrate `1.0.0` through `2.6.0` JSON without changing coordinates, discarding legacy overrides, inferring Wi-Fi/CAP data, or guessing a Phoenix 1/Solitaire family. Report preferences and last-report metadata are additive only; generated report bytes are never embedded in projects.
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
- Phase 7 report packages produce a deterministic ZIP (manifest, project JSON archive without embedded source upload bytes, derived engineering KMZ, CSV schedules, XLSX, PDF summary, presentation-model JSON) via synchronous preview/package APIs and a Report Package UI panel.

## Known limitations

- Missing authoritative fixture-to-IES/BOM mapping; operational compatibility remains explicitly user-assigned.
- For both supplied Solitaire files, 50 W is the controlling Phase 4 nominal input because the filename and LM-63 numeric input field agree; the preserved internal `60W` identifier remains a visible provenance warning and is not rewritten.
- Missing default lens assignments for SMART camera slots; lens selection remains explicit.
- Current IES calculation support is limited to LM-63-1995/2002 Type C files with `TILT=NONE` and the approved zero-physical-tilt far-field direct-light model.
- Terrain/DEM and occlusion remain excluded. Phase 3–6 remain accepted only at their documented limited scopes. Automatic pole placement remains prohibited. Phase 7 reports are engineering-review packages only and do not claim professional, RF, compliance, or installation approval.

## Phase 6 closure

- Accepted implementation commit: `3a81f31682c333928879ecb5168183f1f950ac1d`; evidence-only history through independent-QA commit `f9dcea2fcc9bd8fc4a5118793a383736e5d72695`.
- `docs/phase-6-master-gate-decision-2026-09-03.md` records the master **PASS**. `harness/seals/phase-06.md` is the controlling valid acceptance seal.

## Phase 7 implementation

- Planning decisions `P7-D01`–`P7-D15` approved 2026-09-03 (DL-018); implementation authorized 2026-09-04.
- Controlling contract: `harness/phases/phase-07.md`. Work record: `harness/phases/2026-09-04-phase-7-implementation.md`.
- Completion report: `docs/phase-7-implementation-completion-2026-09-04.md`. Handoff: `docs/phase-7-independent-qa-handoff-2026-09-04.md`.
- Verification summary: `harness/verify/2026-09-04-phase-7-verification-summary.md`.

## Current gate

Phases 1-6 remain formally closed. Phase 7 implementation is complete and awaiting independent QA PASS, master gate PASS, and a valid seal. Report packages are transient derived artifacts and do not mutate source or engineering results.
