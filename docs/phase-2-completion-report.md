# Phase 2 completion report

Completion date: 2026-08-14

Acceptance status: **Accepted by the user on 2026-08-14**

Phase 2 implementation commit: `39495cfb6d6ab9b419f79cc66a7094854b0ccd55`

Scope: fixture, IES, camera/lens catalogs and existing-pole configuration only

## Implementation summary

- Added three operational Draft 2020-12 contracts and retained all seven approved Phase 1 engineering catalogs unchanged at `1.0.0`.
- Updated portable projects to schema `2.0.0` with a lossless Phase 1 migration. Legacy classifications never infer Phoenix 1 or Solitaire.
- Seeded Phoenix 1 and Solitaire LITE, WIFI, and SMART fixture models with structured family, variant, and capability fields.
- Added validated LM-63-1995/2002 Type C, `TILT=NONE` upload, immutable original bytes, SHA-256 identity, parsed metadata, explicit many-to-many associations, and default selection.
- Added editable/versioned camera and lens records with explicit compatibility.
- Added immutable SMART template revisions and revision-pinned pole assignments. Catalog edits do not mutate pole overrides; existing poles adopt new templates only explicitly.
- Added per-pole and explicit-field bulk configuration UI/API while keeping source coordinates immutable.

## Capability matrix

| Model | Lighting | Wi-Fi | Cameras | Template |
|---|---:|---:|---:|---|
| Phoenix 1 LITE | Yes | No | No | None |
| Phoenix 1 WIFI | Yes | Yes | No | None |
| Phoenix 1 SMART | Yes | Yes | Two | -70/+70 degrees, 35 degrees down |
| Solitaire LITE | Yes | No | No | None |
| Solitaire WIFI | Yes | Yes | No | None |
| Solitaire SMART | Yes | Yes | Two | -60/+60 degrees, 35 degrees down |

Azimuth is clockwise from true north and normalized to `[0, 360)`. Downward tilt is stored as a positive angle below horizontal.

## User workflow

1. Open **Catalogs** to view/add/edit/deactivate fixture, camera, and lens records.
2. Upload an IES file, associate it explicitly with one or more fixture models, and optionally set a default.
3. Select a pole and choose a specific fixture model. Legacy classifications show **Explicit selection required** until resolved.
4. Configure IES, height, fixture azimuth, Wi-Fi notes, and SMART slot camera/lens/enable/angle overrides.
5. Use **Bulk assignment** to select a folder or all poles. Only non-empty fields are changed; incompatible Wi-Fi/camera/IES operations are rejected.

## Validation evidence

- Backend: 37 tests passed, including all Phase 1 regressions and Phase 2 catalog, IES, geometry, migration, API, bulk, override, revision-pinning, and coordinate-preservation cases.
- Engineering data validator: the seven frozen catalog/schema pairs and supplied-source hashes remain passing.
- Frontend: rendered-output tests, strict TypeScript, and ESLint passed; production build passed with the existing non-failing MapLibre chunk-size advisory.
- Checked-in Phase 2 seed data validates against all three new contracts.

## Intentionally deferred

- Camera ground-FOV/pixel-density calculation and map rendering.
- Wi-Fi coverage calculation or rendering.
- Illuminance grids, photometric calculations, and result visualization.
- CAP recommendations, topology, automatic pole placement, and reporting/presentation generation.

## Carried-forward data limitations

- Missing authoritative fixture-to-IES/BOM mapping.
- Unresolved Solitaire 50 W / 60 W conflict.
- Missing physical camera XYZ offsets.
- Missing default lens assignments for SMART camera slots.
- Current IES support is limited to LM-63-1995/2002 Type C files with `TILT=NONE`.
