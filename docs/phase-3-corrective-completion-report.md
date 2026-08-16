# Phase 3 corrective completion report

Date: 2026-08-16

Scope: user-authorized corrections for independent QA findings P3-IR-01 through P3-IR-06 only. Phase 4 and later work was not started.

Implementation commit: `acd14aac431b4737192333f085dfec1b8ce93311`

## Outcome

All six findings are corrected. The project contract advances additively from `2.2.0` to `2.3.0`; software and OpenAPI advance from `0.3.0` to `0.3.1`. The seven frozen Phase 1 engineering catalogs remain `1.0.0`, the operational fixture catalog remains `1.2.0`, and operational camera/IES catalogs remain `1.1.0`.

The independent QA report is committed unchanged. Its working-file and staged Git-blob SHA-256 is `216F805A798D564E2BEE1232DA40B6DD883EBAB6BC3E64F6BC766346F447ACB4`.

## Finding-by-finding traceability

### P3-IR-01 — Priority-area editing

- `frontend/app/components/EngineeringWorkspace.tsx` separates create, name-only rename, and explicit redraw. Rename retains the exact existing `wgs84_coordinates` object; redraw always begins with an empty draft. Cancel and failed validation leave the saved ring unchanged.
- `frontend/app/lib/phase3-workflows.mjs` requires at least three distinct finite WGS84 vertices and rejects bounds violations, self-intersection, and degenerate area before returning a closed ring. Messages are user-readable.
- `backend/app/models.py` independently enforces closure, distinct vertices, finite/bounded coordinates, Shapely validity, and non-degenerate area before persistence.
- `frontend/tests/rendered-html.test.mjs` verifies empty-redraw, geometry-preserving rename, distinct-vertex, self-intersection, degenerate, and non-mutation behavior.
- `backend/tests/test_phase3_camera_geometry.py` verifies backend rejection and lossless quarantine of invalid legacy `2.2.0` records.

### P3-IR-02 — Generated contracts

- `schemas/project.schema.json` and `schemas/openapi.json` were regenerated from the current runtime models. `PriorityAreaCoverageSummary.warnings` is present in both.
- `backend/tests/test_phase3_camera_geometry.py` compares the checked-in project schema and OpenAPI documents exactly with fresh in-memory generation.
- Existing operational-catalog freshness tests remain active. Runtime Pydantic models, TypeScript types, generated contracts, migrations, and persisted JSON use the same `2.3.0` fields.

### P3-IR-03 — Camera warning visibility

- `frontend/app/components/EngineeringWorkspace.tsx` aggregates every enabled footprint with warnings into the global Validation panel. Each entry names its pole and camera slot and selects the affected pole when activated.
- `frontend/app/components/EngineeringMap.tsx` derives a pole-level warning source and renders a high-contrast warning ring. `layer_state.warnings` controls that map layer.
- `backend/app/services/store.py` includes enabled-camera warnings in project-summary warning counts.
- Disabled cameras remain warning-free and are excluded from both global and summary aggregation. Backend and frontend regressions cover that boundary.

### P3-IR-04 — Calculation provenance

- `CameraFootprintResult` now stores `horizontal_fov_deg`, `vertical_fov_deg`, and the exact pinned mounting-template `geometry_contract_version` while retaining all existing pole, fixture, template, camera, lens, CRS, orientation, origin-offset, model-version, assumption, and warning provenance.
- `backend/app/services/camera_geometry.py` copies the exact catalog lens FOV values and pinned template contract into each result. Missing pinned templates retain null contract provenance and cannot calculate.
- `frontend/app/lib/types.ts`, generated schemas, OpenAPI, migrations, tests, and persisted project files are aligned.

### P3-IR-05 — Azimuth presentation

- `formatEngineeringAzimuth` normalizes and formats displayed azimuths to at most three decimal places.
- `frontend/app/components/PoleInspector.tsx` uses the formatter. Backend doubles and geometry calculations remain unchanged; the rendered `51.888999999999996` value displays as `51.889°`.

### P3-IR-06 — Documentation

- Updated `camera-conventions.md`, `engineering-assumptions.md`, `current-status.md`, `implementation-plan.md`, `decision-log.md`, `risk-register.md`, `schema-contracts.md`, `architecture.md`, and `data-model.md`.
- Documentation identifies zero XYZ optical-center offsets and flat local Z=0 ground as approved Phase 3 MVP contracts, not blockers.
- Future authoritative mechanical offsets require a new immutable template revision and explicit adoption. Future terrain requires a separately reviewed geometry model. Neither future refinement is inferred or implemented here.

## Contract and migration behavior

- Project schema `2.3.0` accepts migrations from `1.0.0`, `2.0.0`, `2.1.0`, and `2.2.0`.
- Source poles, exact raw coordinate text, numeric longitude/latitude, uploaded bytes, fixture assignments, pinned revisions, and legacy per-camera orientation overrides are preserved.
- Old calculated footprint records without the new provenance fields remain readable because the additive fields are nullable; deterministic recalculation produces complete new provenance.
- An invalid legacy `2.2.0` priority-area record is preserved byte-for-data in `legacy_invalid_priority_areas` and excluded from calculations until the user explicitly redraws it. It is never silently accepted, corrected, or discarded.
- No Phase 1 engineering catalog or source file changed.

## Automated evidence

- Backend complete suite: `85 passed` in 2.69 seconds. The existing non-failing Starlette/httpx deprecation warning remains.
- Engineering/source validation: PASS for all seven frozen catalog/schema pairs, identifiers, traceability, units, domain checks, cross-references, supplied IES hashes, and all supplied-source hashes.
- Project schema/OpenAPI freshness: PASS through exact in-memory equality tests inside the backend suite.
- Operational catalog schema freshness: PASS through the existing exact-generation tests.
- Migrations and coordinate preservation: PASS for `1.0.0`, `2.0.0`, `2.1.0`, and `2.2.0`, including legacy angle bytes and invalid-priority quarantine.
- Frontend rendered/workflow suite: `5 passed`, `0 failed` after the corrective production build.
- Strict TypeScript: PASS with zero errors.
- ESLint: PASS with zero errors or warnings.
- Vinext production build: PASS across client references, server references, RSC, client, and SSR. The existing non-failing large MapLibre chunk and Vinext route-classification advisories remain.
- Dependency restoration used the pinned lockfile and existing content-addressable store; `495` packages were restored with no lockfile change.

## Real rendered manual workflow evidence

The production build ran at `http://127.0.0.1:3000/` against the current local API at port 8000.

1. Imported `Input/Miracle_Mile_Lighting_Poles.kml` through the rendered control. The app showed 74 source poles, LITE 74/WIFI 0/SMART 0, projected CRS `EPSG:32617`, and first raw coordinate `-80.26234411,25.74920999,0`.
2. Assigned the selected pole to Phoenix 1 SMART template r2 and set height to 10 m. Before lens selection the global Validation panel showed both enabled camera warnings without requiring per-pole inspection.
3. The map displayed an affected-pole warning ring. Unchecking Warnings removed that representation; rechecking restored it. Disabled later-phase layer controls remained disabled.
4. Selected JL-LN039 for camera 1 and JL-LN042 for camera 2, then set fixture azimuth `121.889°`. The app immediately showed two valid footprints at `51.889°` and `191.889°` with fixed 140° separation.
5. Inspector provenance showed template r2, `fixed-zero-origin-1.0.0`, X/Y/Z `0/0/0 m`, pinned camera/lens r1, exact H/V FOV `52°/40°` and `69°/54°`, and formatted azimuths. The persisted backend double remained `51.888999999999996`, proving presentation-only rounding.
6. Drew a three-vertex priority area and saved it. Renamed it to `Corrective priority`; the saved geometry remained unchanged.
7. Began Redraw and confirmed the draft started at zero vertices. Drew a bow-tie replacement; Save rejected it with `The replacement priority area is self-intersecting.` The prior `Corrective priority` polygon remained present.
8. Cancelled the failed redraw, began Redraw again at zero vertices, drew a valid replacement, and saved successfully.
9. Saved and reopened the project JSON through rendered controls. Reopen restored 74 source poles, the named priority area, two footprints, exact provenance, and formatted azimuths.
10. With explicit action-time approval, deleted only the temporary `Corrective priority` area. The rendered status confirmed `Priority area deleted; source poles and coordinates unchanged`, the row disappeared, and the source count remained 74.
11. Browser console error log: empty. Lighting, Wi-Fi coverage, CAP recommendations, reporting, and proposed/automatic pole placement remained unavailable.

## Coordinate and source integrity

- Miracle Mile source SHA-256 remains `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`.
- The saved/reopened corrective project contained 74 poles. First source identity and coordinate evidence remained: `pole-443127e3a723e1b3`, raw `-80.26234411,25.74920999,0`, longitude `-80.26234411`, latitude `25.74920999`.
- Automated assignment, geometry, migration, save/reopen, and rendered interaction checks confirm source pole IDs and coordinates are never generated, moved, optimized, corrected, or deleted.
- `Input/` and all seven frozen Phase 1 engineering catalogs are unchanged.

## Remaining limitations and deferred items

- The geometry is flat local ground only. There is no DEM, terrain slope, building/tree/fixture occlusion, refraction, or obstacle model.
- The camera model is symmetric rectilinear pinhole using catalog H/V FOV; there is no lens-distortion correction.
- Zero XYZ offsets are the approved MVP mounting contract, not an assertion about future measured hardware. Future authoritative offsets require a new immutable revision.
- There is no default lens. Every enabled camera requires an explicit compatible pinned lens.
- Pixel density remains explicitly null/not calculated. No recognition, LPR, people-counting, analytics, compliance, or suitability threshold is present.
- Priority areas are single exterior rings without holes or multipolygon authoring.
- Legacy invalid priority records are retained for recovery but require explicit user redraw before calculations.
- Wi-Fi coverage, photometry/illuminance, CAP recommendations, reporting/presentation generation, proposed poles, automatic placement, and coordinate optimization remain unimplemented.

## Handoff recommendation

Run an independent Phase 3 corrective integration review and QA session against implementation commit `acd14aac431b4737192333f085dfec1b8ce93311` and this report. Treat all evidence above as claims to verify independently. Phase 4 remains gated and must not begin without a separate acceptance decision and authorization.
