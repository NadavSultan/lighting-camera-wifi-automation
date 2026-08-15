# Decision log

## DL-001 — Retrospective Phase 2 contract ratification

- Date: 2026-08-15
- Status: ratified retrospectively for corrective implementation
- Provenance: explicit user authorization in the Phase 2 corrective session, following independent QA finding IR-11
- Decision: retain the seven Phase 1 engineering catalogs unchanged at `1.0.0`; retain the three Phase 2 operational contract identities; advance the corrected operational contracts to `1.1.0` and the project contract to `2.1.0` with explicit `1.0.0`/`2.0.0` migrations.
- Governance note: the operational contracts were not present in the pre-implementation Git history. This entry does not claim that the original review gate was met and does not alter or weaken IR-11. It records the later authorization that permits the corrective work and provides a repository-owned audit trail for retesting.

## DL-002 — Immutable operational equipment revisions

- Date: 2026-08-15
- Status: approved for Phase 2 correction
- Decision: fixture, camera, and lens updates append the previous complete record to immutable history. Pole assignments resolve the exact fixture, camera, lens, and mounting-template revisions they pin. A new catalog/template revision affects an existing pole only after an explicit adoption or assignment action.
- Compatibility: unversioned camera/lens assignments created by the initial Phase 2 implementation are pinned once, on project open/save, to the then-current operational revision; customer source data and coordinates are not changed.

## DL-003 — Camera/lens compatibility authority

- Date: 2026-08-15
- Status: approved for Phase 2 correction
- Decision: `LensConfiguration.compatible_camera_model_ids` is authoritative. `CameraModel.compatible_lens_ids` is derived, persisted for consumers, and required to be reciprocal. Backend validation and frontend filtering use the authoritative lens relation.

## DL-004 — Operational lifecycle and bulk-null semantics

- Date: 2026-08-15
- Status: approved for Phase 2 correction
- Decision: referenced equipment deactivation returns a conflict; configuration validation remains safe if an inactive reference is encountered. Invalid/inactive IES files cannot be activated, associated actively, or selected as defaults. Explicit JSON `null` values in the Phase 2 bulk patch mean “unchanged”; clearing requires a specific per-pole action.

## DL-005 — Phase boundary

- Date: 2026-08-15
- Status: binding
- Decision: corrective work ends at operational catalogs and existing-pole configuration. Camera ground projection/FOV, RF coverage, illuminance, CAP recommendations, automatic pole placement, and Phase 3 or later behavior remain excluded.
