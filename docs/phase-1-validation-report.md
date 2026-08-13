# Phase 1 independent validation report

Validation date: 2026-08-13

Scope: completed Phase 1 only

Decision: **PASS after fixes**

Phase 2 was not started. No camera, Wi-Fi coverage, photometric, CAP, reporting, presentation, proposed-pole, or pole-generation feature was implemented.

## Executive result

The approved Phase 1 workflow is operational: KML/KMZ import, immutable original source retention, map-centred pole display, LITE/WIFI/SMART classification, pole height and fixture edits, portable project JSON save/reopen, and updated KML export. Existing-pole mode remains the default and the UI exposes no pole creation, deletion, movement, or proposed-layout action.

Six confirmed defects were found and fixed during validation. The final automated, build, startup, API, source-integrity, export/reimport, and live UI checks passed. No confirmed Phase 1 defect remains open.

## Findings

### Critical

#### F-01 — Portable project source integrity and atomicity were incomplete — Fixed

- Evidence: Before the fix, an API regression test showed that a portable project with a false `sha256` was accepted with HTTP 200. A same-ID source replacement was rejected only after `project.json` had already changed, proving that the rejected operation could corrupt saved project state. Static inspection also showed that an unsafe portable filename could escape the `sources/` directory and that a new portable project could supply pole records inconsistent with its embedded KML/KMZ.
- Affected files/components: `backend/app/models.py` (`SourceFile`), `backend/app/services/store.py` (`ProjectStore.save`), `backend/app/services/kml.py` (portable source verification), and `backend/app/main.py` (`POST /api/projects/open`).
- Expected behavior: Embedded bytes must match their recorded size and SHA-256; source filenames must be safe basenames; immutable source data must be checked before any persisted project replacement; source pole records must be reproducible from the embedded customer file.
- Actual behavior: Integrity metadata was trusted, source replacement checks ran after the project JSON write, and portable source records were not reconciled with the embedded file.
- Recommended fix: Validate Base64, size, digest, and filename in the authoritative model; reparse and compare the source layer on JSON open; preflight existing source equality and archived bytes before atomically replacing project JSON.
- Resolution: Implemented with regression coverage. Rejected opens leave the prior project and archived customer bytes unchanged.

### High

#### F-02 — Duplicate KML Placemark IDs collapsed distinct poles — Fixed

- Evidence: An adversarial KML with two Point Placemarks using `id="same"` imported two records but produced only one unique application pole ID. Because edits are keyed by pole ID and MapLibre feature IDs use the same value, the poles could not be edited or selected independently.
- Affected files/components: `backend/app/services/kml.py` pole identity assignment; downstream `pole_edits` and frontend map feature identity.
- Expected behavior: Every imported Point must have a unique stable internal ID while retaining the original customer Placemark ID as source metadata.
- Actual behavior: The duplicate source ID was reused directly as both internal IDs.
- Recommended fix: Preserve `source_placemark_id`, assign a deterministic unique internal ID to later collisions, issue a `duplicate_placemark_id` warning, and enforce source-ID uniqueness at the project-model boundary.
- Resolution: Implemented. The duplicate-ID fixture now imports as two independently addressable poles and retains `source_placemark_id="same"` on both.

### Medium

#### F-03 — Non-finite altitude values were accepted — Fixed

- Evidence: A Point containing `-80.1,25.7,nan` imported as a valid pole with a non-finite altitude. Such a value cannot round-trip reliably through strict JSON and can silently become null or invalid output.
- Affected file/component: `backend/app/services/kml.py` coordinate parsing.
- Expected behavior: Longitude, latitude, and supplied altitude must all be finite numeric values; an invalid record in a partially valid KML should be skipped with a `malformed_coordinate` error warning.
- Actual behavior: Bounds checks covered longitude and latitude but no finiteness check covered altitude.
- Recommended fix: Require `math.isfinite` for every parsed coordinate component before accepting the Point.
- Resolution: Implemented. The invalid Point is skipped while other valid records import.

#### F-04 — The documented frontend lint acceptance gate failed — Fixed

- Evidence: The final `eslint . --ignore-pattern dist --ignore-pattern .next` run returned exit code 1 with four errors: two `jsx-a11y` errors for a clickable non-interactive toast and two `no-unused-vars` errors for unused D1 imports.
- Affected files/components: `frontend/app/components/EngineeringWorkspace.tsx` error toast, `frontend/app/globals.css` toast styling, and the unused Phase 1 D1 boundary in `frontend/db/index.ts`.
- Expected behavior: The documented Phase 1 acceptance command must complete with zero lint errors; a dismissible alert must be keyboard-operable.
- Actual behavior: The command failed, and the alert could only be dismissed with a pointer.
- Recommended fix: Render the dismissible alert as a semantic button and remove imports that are intentionally unused because Phase 1 has no database.
- Resolution: Implemented. ESLint completes with zero errors or warnings, and the toast is keyboard-focusable.

### Low

#### F-05 — Structured backend validation errors were unreadable in the frontend — Fixed

- Evidence: FastAPI returns Pydantic request-validation details as an array of objects, while `frontend/app/lib/api.ts` typed `detail` as a string and passed it directly to `Error`. JavaScript coerced the array to an unhelpful object string instead of displaying validation messages.
- Affected file/component: `frontend/app/lib/api.ts` error-response handling.
- Expected behavior: Malformed or unsafe portable project JSON should produce a concise, readable validation message in the UI.
- Actual behavior: Structured 422 details could render as `[object Object]`.
- Recommended fix: Treat `detail` as unknown, extract each structured item's `msg`, and join multiple validation messages while preserving ordinary string details.
- Resolution: Implemented with a rendered-suite source assertion; string and structured error responses now have readable messages.

#### F-06 — Inline custom IconStyle colours were absent from the parsed source model — Fixed

- Evidence: A Placemark with an inline `<Style><IconStyle><color>ffabcdef</color>` retained the raw uploaded bytes but returned `source_style_color=null`.
- Affected file/component: `backend/app/services/kml.py` style resolution.
- Expected behavior: The parsed source pole should expose the resolved inline icon colour just as it exposes colours referenced through document Styles and StyleMaps.
- Actual behavior: Only shared `styleUrl` targets were resolved.
- Recommended fix: Resolve a Placemark's inline IconStyle colour first, then fall back to the shared Style/StyleMap lookup.
- Resolution: Implemented with regression coverage.

## Input-structure validation matrix

| Structure | Result | Evidence |
|---|---|---|
| Simple Point KML | Pass | Existing service fixture imports exact name, coordinate text, numeric coordinate, altitude, description, and source ID. |
| Nested folders | Pass | Two-level `Outer / Inner` hierarchy retained. |
| ExtendedData | Pass | `Data/value` and `SchemaData/SimpleData` values retained, including XML-decoded text. |
| Custom Style and StyleMap | Pass | Normal StyleMap colour resolves to `ff112233`; inline IconStyle resolves to `ffabcdef`. |
| Duplicate points | Pass | Exact duplicate coordinates produce `duplicate_coordinate`; near duplicates retain both poles and produce distance warnings. |
| Duplicate Placemark IDs | Pass after fix | Both poles receive unique internal IDs, retain the repeated customer ID, and produce a warning. |
| Malformed/partially valid records | Pass after fix | Invalid/out-of-bounds/non-finite Points are skipped with error warnings while valid Points remain. |
| Unsupported geometries | Pass | Non-Point Placemark is counted and warned without modifying the source file. |
| Empty KML | Pass | Cleanly rejected with `No valid Point placemarks were found`. |
| KMZ with KML and resources | Pass | `doc.kml` selected; original archive bytes and supporting resource bytes remain unchanged. |
| Supplied Miracle Mile KML | Pass | 74 poles, five expected folders, zero unsupported geometries, `EPSG:32617`. |

## Data preservation and coordinate evidence

- Checked-in input SHA-256: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
- Embedded project source SHA-256: identical.
- Archived runtime source SHA-256: identical.
- Updated-KML export/reimport: 74 poles, zero coordinate mismatches, zero unsupported geometries.
- Exported KML retained LITE, WIFI, and SMART values in `lcwa_fixture_type` ExtendedData.
- Portable JSON reopen restored one SMART pole at 8.5 m with engineering notes plus a 10-pole WIFI folder assignment (11 separate edit overlays total).
- Customer coordinates remained read-only in the UI and no source pole location changed.

## Frontend validation

The production UI was exercised through the documented `http://127.0.0.1:3000/` origin against the local API:

1. Imported `Input/Miracle_Mile_Lighting_Poles.kml` and displayed 74 source poles in the MapLibre workspace.
2. Confirmed the initial effective counts were LITE 74, WIFI 0, SMART 0.
3. Changed the selected pole to SMART, set height to 8.5 m, and added engineering notes.
4. Bulk-assigned the 10-pole Decorative folder to WIFI.
5. Confirmed counts changed to LITE 63, WIFI 10, SMART 1.
6. Confirmed undo returned LITE 73, WIFI 0, SMART 1 and redo restored LITE 63, WIFI 10, SMART 1.
7. Saved and exported the project.
8. Reopened portable project JSON and confirmed counts, SMART assignment, height, notes, original coordinate text, projected CRS, and 11 edits.
9. Confirmed future-phase controls remained disabled and existing-pole mode remained visible.

## Automated tests, build, and startup

Final validation commands and results:

- Backend `pytest`: 22 passed; one non-failing Starlette/httpx2 deprecation warning.
- Frontend rendered-output tests: 2 passed, 0 failed.
- TypeScript `tsc --noEmit`: passed with zero errors.
- ESLint: passed with zero errors or warnings.
- Production `vinext build`: passed across client, server, RSC, and SSR environments. The known MapLibre-related chunk-size advisory remains non-failing.
- Fresh Uvicorn startup on port 8010: health returned `{"status":"ok","phase":1,"version":"0.1.0"}`.
- Fresh production frontend startup on port 3000: HTTP 200 with title `Lighting Camera WiFi Automation`.
- Validation processes and browser tabs were stopped/closed afterward.

## Accepted limitations, not Phase 1 defects

- OpenStreetMap background tiles require internet access.
- Updated KML is an interchange artifact. Reimport preserves exact coordinates and `lcwa_*` metadata, but portable project JSON is the supported format for reconstructing the separate `pole_edits` layer.
- The rendered-output frontend suite does not automate MapLibre canvas clicks; the acceptance workflow above supplied live UI coverage.
- Camera, Wi-Fi analysis, photometry, CAP, advanced reporting, presentation output, and proposed-layout functionality remain intentionally absent.

## Final gate decision

Phase 1 independently validates as complete after the fixes recorded above. Phase 2 remains not started and unauthorized. The next action is user review and explicit Phase 1 acceptance; only a later explicit authorization may open Phase 2.
