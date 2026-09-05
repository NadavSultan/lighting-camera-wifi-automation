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

## Phase 4 - lighting calculation engine

Status: complete and formally closed on 2026-08-26 after all P4-IR-01 through P4-IR-07 findings received independent passing evidence and the master gate returned **PASS**.

- First approve authoritative fixture-to-IES mapping, fixture orientation and IES axes, rotation order, interpolation, equations, maintenance-factor behavior, uniformity definitions, validation cases, comparison method, and tolerances.
- Add lighting-specific `calculation_areas`, separate from Phase 3 camera `priority_areas`, classified as Road, Sidewalk, Parking, or Other.
- Use an editable calculation plane at ground/road level and a default 2-metre clipped point grid inside each polygon.
- Calculate direct horizontal illuminance at each point and show average, minimum, maximum, explicit uniformity ratios, assumptions, warnings, and fixture/IES provenance.
- Add map point/result visualization and heat maps without making standards-compliance claims unless an approved standard, targets, and validation evidence exist.

## Phase 5 - conceptual Wi-Fi

Status: complete and formally closed on 2026-08-27 after the independent final review findings QA-01 and QA-02 received a focused independent **PASS** and the master gate returned **PASS**.

- Add WIFI/SMART-only configurable circles, overlaps, gaps, and boundary statistics in projected metres.
- Label all results conceptual, not verified RF design.
- Keep a separate user-drawn Wi-Fi analysis-area collection for boundary/gap statistics; do not infer a project boundary from source extents or other phase polygons.
- Preserve source poles and all prior calculated/recommended collections; add only a separate persisted conceptual Wi-Fi result layer.

## Phase 6 - CAP

Status: complete and formally closed on 2026-09-03 after implementation readiness, independent QA **PASS**, master gate **PASS**, and a valid Phase 6 seal.

- Convert the reviewed datasheet and clarified project rules into an editable constraint file.
- Implement explainable clustering, candidate CAPs, manual locks/reassignment, topology checks, and revalidation.
- Never move or generate lighting poles.

## Phase 7 - reporting

Status: planning decisions approved on 2026-09-03; original implementation authorized 2026-09-04 and failed independent QA at `fd8a43d`; bounded remediation authorized 2026-09-05 under amended `P7-D08`. Remediation product work is committed; readiness, new independent QA, master gate, and seal remain outstanding. No Phase 7 seal.

- KML/KMZ layers, CSV/XLSX schedules, calculations, assumptions, validations, JSON archive, PDF summary, and future presentation model.

## Review gates

Each phase requires passing calculation/service tests, schema migration review, representative source validation, and interactive workflow validation before the next phase begins.

The Phase 2 gate is closed with an independent unconditional pass. The Phase 3 gate is closed with an independent final focused pass under the approved zero XYZ origin offsets, explicit per-slot lens requirement, and flat local ground plane. The Phase 4 gate is closed with independent passing evidence for P4-IR-01 through P4-IR-07 and the master decision recorded in `docs/phase-4-master-gate-decision-2026-08-26.md`. Phase 5 is closed after the final focused independent PASS recorded in `docs/phase-5-final-focused-retest-2026-08-27.md` and the master decision in `docs/phase-5-master-gate-decision-2026-08-27.md`. Phase 6 is closed after the independent QA PASS in `harness/verify/2026-09-02-phase-6-independent-qa-review.md` and the master decision in `docs/phase-6-master-gate-decision-2026-09-03.md`. Phase 7 original implementation failed independent QA at `fd8a43d`; remediation is authorized and in progress toward readiness and a new independent QA. No Phase 7 seal.
