# Phase 2 corrective completion report

Completion date: 2026-08-15

Corrective implementation commit: `081da6ed9aa52a792112d3a1ed9b6c7e69a5d006`

Disposition: **Corrective implementation complete; returned for independent QA retesting.** This report does not change the independent QA FAIL, does not claim corrective acceptance, and does not authorize or begin Phase 3.

## Contract and migration outcome

- The seven approved Phase 1 engineering catalogs and every supplied `Input/` file are unchanged.
- The fixture-model, IES-library, and camera-equipment operational contracts advance from `1.0.0` to `1.1.0` under their existing identities.
- The project contract advances from `2.0.0` to `2.1.0`. Phase 1 `1.0.0` and initial Phase 2 `2.0.0` projects migrate without coordinate changes or Phoenix 1/Solitaire inference.
- Initial Phase 2 catalog payloads receive empty immutable histories and corrective-baseline revision-1 template equipment pins on load.
- Generated project and operational schemas declare JSON Schema Draft 2020-12 explicitly.

## Finding-by-finding traceability

| Finding | Implemented correction | Affected files / contracts | Automated test evidence | Manual workflow evidence | Remaining limitation |
|---|---|---|---|---|---|
| IR-01 | Fixture, camera, and lens updates archive the previous complete record; assignments pin exact fixture/camera/lens/template revisions; historical content resolves by `(id, revision)`; adoption remains explicit. | `catalog_models.py`, `catalogs.py`, `configuration.py`, `models.py`, fixture/camera seeds and schemas, project schema, frontend types/inspector/workspace. | `test_ir01_catalog_updates_preserve_immutable_revisions_and_exact_pins`; template-pinning regression; migration tests. | Inspector retained the explicit catalog/template adoption control; slot selections created revision-bearing overrides and reset without changing the catalog template. | Initial unversioned Phase 2 overrides are pinned once to the corrective-baseline current revision because no earlier pin exists. |
| IR-02 | Configuration validation no longer indexes a missing active-camera map entry; API deactivation of referenced fixture/camera/lens records returns `409`; administratively inactive references produce readable `422` validation. | `main.py`, `configuration.py`, project/OpenAPI contracts, lifecycle policy docs. | `test_ir02_inactive_camera_validation_is_safe_and_api_deactivation_conflicts`. | Not a normal success-path UI action; API regression covers both supported conflict and defensive invalid-state behavior. | Direct filesystem catalog edits remain an administrative risk and are recorded in R-08. |
| IR-03 | IES validation rejects negative/non-finite candela, non-finite numeric data, unordered or out-of-range angles, invalid counts, lamp/header factors, watts, types, units, and count mismatches. | `ies.py`, IES/OpenAPI schemas. | Parameterized `test_ir03_ies_semantic_validation_rejects_bad_photometry` plus valid supplied-file parsing tests. | Upload UI remains constrained to `.ies`; semantic failures are server-authoritative. | Parser support remains limited to LM-63-1995/2002 Type C with `TILT=NONE`. |
| IR-04 | Invalid/unsupported uploads are preserved as inactive records with errors and optional metadata; valid records can carry warnings; UI renders errors/warnings; operational/generated schemas declare Draft 2020-12. | `catalog_models.py`, `ies.py`, `main.py`, `CatalogManager.tsx`, frontend types, schema exporter, IES schema/OpenAPI. | `test_ir04_failed_ies_is_persisted_with_errors_warnings_and_draft_schema`, including checked-in schema freshness comparisons. | Catalog manager exposes status and validation messages; invalid records cannot be activated from the UI. | Warning coverage is parser-semantic, not a full photometric quality/certification review. |
| IR-05 | Active association/default selection requires an active valid IES file; invalid records cannot reactivate; deactivation clears active associations/defaults. | `catalog_models.py`, `catalogs.py`, `main.py`, `CatalogManager.tsx`, IES/fixture/OpenAPI schemas. | `test_ir05_inactive_or_invalid_ies_cannot_be_associated_or_defaulted`; association/default replacement regression. | Catalog association selector lists active valid files only. | Authoritative fixture-to-IES mapping is still missing; associations remain explicit user choices. |
| IR-06 | Lens `compatible_camera_model_ids` is authoritative; camera compatible-lens lists are derived and strict reciprocity is contract-validated; backend and lens picker use the same relation. | `catalog_models.py`, `catalogs.py`, `configuration.py`, `CatalogManager.tsx`, `PoleInspector.tsx`, camera schema and docs. | `test_ir06_lens_relation_is_authoritative_and_reciprocal`; catalog CRUD regression. | SMART lens picker filtered against the chosen/default camera and accepted the seeded compatible lens. | Compatibility states only catalog pairing, not image-quality suitability for a scene. |
| IR-07 | Pole legacy `fixture_type` must equal the pinned model capability variant; incompatible payloads are rejected. | `configuration.py`, project/OpenAPI contracts and transition-policy docs. | `test_ir07_fixture_classification_must_match_selected_model`; non-SMART capability rejection regression. | Selecting a model updates both the explicit model configuration and displayed capability classification. | Legacy classifications still do not identify a family; explicit model selection remains required. |
| IR-08 | Bulk target mode now supports all poles, one source folder, or an accumulated manual set of arbitrary selected pole IDs. | `EngineeringWorkspace.tsx`, `phase2-workflows.mjs/.d.ts`, frontend workflow tests. | `manual bulk targets and slot reset implement the Phase 2 corrective workflows` tests manual, folder, and all targeting. | Imported 74 poles, selected two distinct map poles, observed `2 manually selected`, and applied one bulk model change to exactly 2 edits. | Manual selection is session UI state; it is not a persisted project selection set. |
| IR-09 | Only non-null explicitly supplied bulk fields mutate data; explicit `pole_height_m: null` and other null patch values mean unchanged. | `configuration.py`, data-model policy. | `test_ir09_explicit_null_bulk_fields_leave_existing_values_unchanged`; unrelated-field/coordinate-preservation bulk regression. | Empty bulk inputs remained “Unchanged”; two-pole model assignment did not alter displayed source coordinates. | Clearing is deliberately not implicit in bulk null; use a specific per-pole/reset action. |
| IR-10 | Each SMART slot with an override exposes a removal action that deletes only that pole delta and restores the pinned template values. | `PoleInspector.tsx`, `phase2-workflows.mjs/.d.ts`, frontend workflow tests. | `manual bulk targets and slot reset implement the Phase 2 corrective workflows` verifies non-mutating single-slot removal. | Selecting a lens changed the slot to `Pole override`; reset removed the action and restored two `Catalog default` labels. | Missing approved default lens assignments means reset can correctly restore an unassigned lens. |
| IR-11 | Added an explicitly retrospective ratification artifact, decision log, risk entry, schema-contract addendum, and status/roadmap correction; no approval is backdated and the QA report is untouched. | `phase-2-contract-ratification.md`, `decision-log.md`, `risk-register.md`, `schema-contracts.md`, `current-status.md`, `implementation-plan.md`. | `test_ir11_retrospective_ratification_is_explicit_and_not_backdated`. | Governance evidence is repository/document review rather than a UI workflow. | The missing pre-implementation Git artifact remains a historical process failure; independent QA must decide whether retrospective ratification satisfies corrective acceptance. |

## Complete validation evidence

- Backend: `51 passed`; one non-failing Starlette/httpx2 deprecation warning.
- Phase 2 contract/seed validation: all three `1.1.0` seeds validate against checked-in Draft 2020-12 schemas; generated-schema freshness is test-enforced.
- Engineering data: all seven frozen Phase 1 catalogs, domain checks, cross-references, and supplied-source hashes pass.
- Frontend: `3 passed`; strict TypeScript passes; ESLint passes with no reported errors/warnings.
- Production build: passes; only the existing non-failing MapLibre chunk-size advisory remains.
- Migration: Phase 1 `1.0.0`, initial project `2.0.0`, and initial operational catalog `1.0.0` migrations pass.
- Coordinate preservation: backend KML/project/bulk suites pass. Manual UI import found 74 source poles; one displayed raw coordinate remained exactly `-80.2623542518245,25.7494765240893,0` through bulk apply, undo, and redo. No browser console errors occurred.
- Phase boundary: rendered/manual UI verification confirmed Phase 3 FOV, Phase 4 RF, Phase 5 lighting, and Phase 6 CAP controls remain disabled; no later-phase engine or API was added.

## Carried-forward data limitations

- Missing authoritative fixture-to-IES/electrical BOM mapping.
- Unresolved Solitaire 50 W / 60 W conflict.
- Missing physical camera XYZ offsets.
- Missing default lens assignments for SMART camera slots.
- Current IES support is limited to LM-63-1995/2002 Type C with `TILT=NONE`.
- Terrain/ground-plane assumptions remain unapproved; all Phase 3 and later calculations remain excluded.

## QA handoff

Retest IR-01 through IR-11 against commit `081da6ed9aa52a792112d3a1ed9b6c7e69a5d006` and this report. Do not use the original Phase 2 completion report as current acceptance evidence. Do not begin Phase 3.
