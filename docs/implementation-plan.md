# Phased implementation plan

## Phase 1 - project and KML/KMZ foundation

Status: complete, tested, accepted, and frozen.

- Safe KML/KMZ import and immutable source archival.
- Preserve point metadata, folder hierarchy, styles, descriptions, ExtendedData, and exact coordinates.
- Warn about malformed coordinates, unsupported geometries, duplicates, and suspicious outliers without correction.
- Map display and selection; LITE/WIFI/SMART assignment; pole height, status, name/ID, and notes edits.
- Separate source and edit layers; undo/redo; JSON save/reopen; updated KML export.
- Existing-pole mode only. No automatic pole creation or movement.

## Phase 2 - fixture, IES, and camera catalogs

Status: complete and formally closed on 2026-08-15 after independent **UNCONDITIONAL PASS**.

- Added operational fixture-model, IES, and camera/lens catalogs while retaining the approved Phase 1 reference catalogs.
- Added validated IES upload/parsing, explicit fixture associations, all/folder/manual bulk assignment, and removable per-pole overrides.
- Corrected IR-01 through IR-11 with immutable complete-record histories, exact equipment revision pins, safe lifecycle validation, hardened IES semantics, reciprocal compatibility, and repository-owned retrospective ratification.
- Added immutable Phoenix 1 SMART ±70-degree and Solitaire SMART ±60-degree mounting-template revisions with positive downward tilt.
- Resolve source discrepancies before use (for example, two `050W` filenames identify a `60W` luminaire internally).

## Phase 3 - camera geometry

Status: complete and formally closed on 2026-08-17 after all P3-IR-01 through P3-IR-06 corrections received independent retest and the final focused P3-IR-05 retest returned **PASS** with no confirmed defects or regressions.

- Flat-terrain ground-FOV projection for two immutable fixed-mount camera slots on SMART fixtures, with fixture-level azimuth editing and map rotation.
- Explicit compatible lens selection, per-slot enable state, deterministic warnings, revision-aware provenance, overlap metrics, and persisted priority-area intersection summaries.
- Keep geometric FOV and pixel-density architecture distinct from analytics-quality coverage; no recognition, LPR, or compliance thresholds.
- Corrective gate adds safe rename/redraw priority editing, generated-contract freshness, global/map camera warnings, complete FOV/mounting provenance, deterministic azimuth formatting, and aligned documentation.

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

The Phase 2 gate is closed with an independent unconditional pass. The Phase 3 gate is closed with an independent final focused pass under the approved zero XYZ origin offsets, explicit per-slot lens requirement, and flat local ground plane. Phase 4 remains gated and requires separate explicit authorization.
