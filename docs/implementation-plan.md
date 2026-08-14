# Phased implementation plan

## Phase 1 - project and KML/KMZ foundation

Status: complete, tested, and frozen for acceptance review. No Phase 2 work is authorized by the current handoff.

- Safe KML/KMZ import and immutable source archival.
- Preserve point metadata, folder hierarchy, styles, descriptions, ExtendedData, and exact coordinates.
- Warn about malformed coordinates, unsupported geometries, duplicates, and suspicious outliers without correction.
- Map display and selection; LITE/WIFI/SMART assignment; pole height, status, name/ID, and notes edits.
- Separate source and edit layers; undo/redo; JSON save/reopen; updated KML export.
- Existing-pole mode only. No automatic pole creation or movement.

## Phase 2 - fixture, IES, and camera catalogs

Status: complete, tested, and accepted on 2026-08-14.

- Added operational fixture-model, IES, and camera/lens catalogs while retaining the approved Phase 1 reference catalogs.
- Added validated IES upload/parsing, explicit fixture associations, bulk/folder assignment, and per-pole overrides.
- Added immutable Phoenix 1 SMART ±70-degree and Solitaire SMART ±60-degree mounting-template revisions with positive downward tilt.
- Resolve source discrepancies before use (for example, two `050W` filenames identify a `60W` luminaire internally).

## Phase 3 - camera geometry

Status: not started and not authorized.

- Flat-terrain ground-FOV projection, independent cameras, azimuth handles, overlap and priority areas.
- Keep geometric FOV distinct from analytics-quality coverage and add pixel-density data structures.

## Phase 4 - conceptual Wi-Fi

- WIFI/SMART-only configurable circles, overlaps, gaps, and boundary statistics in projected metres.
- Label all results conceptual, not verified RF design.

## Phase 5 - photometric engine

- First approve IES axes, luminaire orientation, rotation order, interpolation, equations, validation cases, AGi32 comparison method, and tolerances.
- Implement calculation polygons, clipped grids, direct horizontal illuminance, heat maps, and per-area statistics.

## Phase 6 - CAP

- Convert the reviewed datasheet and clarified project rules into an editable constraint file.
- Implement explainable clustering, candidate CAPs, manual locks/reassignment, topology checks, and revalidation.
- Never move or generate lighting poles.

## Phase 7 - reporting

- KML/KMZ layers, CSV/XLSX schedules, calculations, assumptions, validations, JSON archive, PDF summary, and future presentation model.

## Review gates

Each phase requires passing calculation/service tests, schema migration review, representative source validation, and interactive workflow validation before the next phase begins.

The immediate gate is closed: Phase 2 is accepted. A future session may begin Phase 3 only after new explicit authorization and approval of the required physical camera offsets, lens assignments, and terrain assumptions. No later phase was started in the Phase 2 session.
