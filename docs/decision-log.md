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

## DL-006 — Phase 2 closure and Phase 3 authorization

- Date: 2026-08-15
- Status: approved
- Decision: the independent NIR-01 final retest grants Phase 2 an **UNCONDITIONAL PASS** and formal closure. The user separately authorizes Phase 3 camera geometry. Phase 4 and later work remains excluded.
- Evidence: `phase-2-nir-01-final-retest-report.md`; the earlier FAIL and conditional retest reports remain unchanged historical evidence.

## DL-007 — Phase 3 fixed camera mounting and ground model

- Date: 2026-08-15
- Status: approved
- Decision: each SMART camera optical center is the fixture mounting/reference origin with immutable offsets X=0 m, Y=0 m, Z=0 m. Optical-center height equals configured pole/fixture height. Phoenix 1 SMART slots remain -70/+70 degrees and Solitaire SMART slots -60/+60 degrees, both at fixed 35 degrees below horizontal. Only fixture azimuth rotates both cameras; per-camera azimuth and tilt are not editable.
- Calculation frame: the project-selected local projected CRS in metres, flat horizontal ground at Z=0, symmetric rectilinear pinhole frustum, catalog H/V FOV, no distortion, terrain, occlusion, refraction, or obstacles.

## DL-008 — Phase 3 explicit lens and legacy-override safety

- Date: 2026-08-15
- Status: approved
- Decision: there is no default lens. An enabled slot calculates only with an explicit compatible pinned camera/lens revision and valid height/template. Legacy per-pole relative-azimuth or downward-tilt override bytes remain persisted but block calculation until the user explicitly resets that slot to the immutable template; new angle overrides are not accepted by the Phase 3 UI.

## DL-009 — Phase 3 corrective contract and safe priority replacement

- Date: 2026-08-16
- Status: approved corrective implementation following independent QA FAIL
- Decision: advance the additive project contract to `2.3.0` and software/API to `0.3.1`. Persist exact lens H/V FOV and mounting geometry-contract provenance. Priority-area rename preserves geometry exactly; redraw begins empty and commits only a validated replacement. Invalid legacy `2.2.0` priority records are retained losslessly in a non-calculated quarantine collection.
- UI decision: enabled-camera warnings are global validation items and pole-level map indicators controlled by the Warnings layer. Disabled cameras remain non-errors. Azimuth display is rounded to three decimal places without changing calculation precision.
- Boundary: Phase 4 and later remain unauthorized and unstarted.

## DL-010 — Phase 4/5 roadmap and polygon separation

- Date: 2026-08-17
- Status: approved
- Decision: Phase 4 is the Lighting Calculation Engine and Phase 5 is conceptual Wi-Fi coverage, matching the approved master roadmap.
- Decision: Phase 3 camera `priority_areas` remain separate from Phase 4 lighting `calculation_areas`.
- Decision: lighting calculation areas are user-drawn polygons classified as Road, Sidewalk, Parking, or Other; they must not be inferred from or silently merged with camera priority areas.
- Boundary: this roadmap correction does not authorize Phase 4 implementation. Photometric inputs, conventions, validation criteria, and implementation/QA prompts must be approved first.

## DL-011 — Phase 4 direct-light model and validation boundary

- Date: 2026-08-17
- Status: approved for implementation; independent QA still required
- Decision: project schema `2.4.0` and software/API `0.4.0` add lighting-only `calculation_areas` and persisted `lighting_calculations`. Grids use a projected-CRS-zero lattice, requested spacing, inside-or-boundary policy with `1e-7 m` tolerance, deterministic south-to-north then west-to-east ordering, and a 25,000-point limit without silent spacing changes or point removal.
- Photometry: Type C C0 aligns with fixture azimuth; azimuth is clockwise from grid north; world points rotate into the local frame by subtracting fixture azimuth. No physical tilt is applied. Direct horizontal illuminance is `I * cos(incidence) / r^2`, equivalent to `I*h/r^3`, summed across eligible fixtures and multiplied by the area maintenance factor.
- Compatibility: both supplied Phoenix files are restricted by exact SHA-256 to Phoenix 1 LITE/WIFI/SMART; both supplied Solitaire files are restricted to Solitaire LITE/WIFI/SMART. Association and pole selection remain explicit and no default is created.
- Solitaire: 50 W is controlling; the preserved 60W internal identifier is warned. Raw negative D02 dimensions remain unchanged and luminous-opening geometry is explicitly excluded from the far-field model.
- Validation boundary: synthetic mathematical cases are implementation evidence only. Every result states that it is not independently validated against AGi32 or another professional reference tool and is not a standards-compliance determination. Phase 5 and later remain unauthorized.
