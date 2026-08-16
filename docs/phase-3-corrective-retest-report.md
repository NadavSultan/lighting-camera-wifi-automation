# Phase 3 corrective integration review and QA retest

Date: 2026-08-16  
Assignment: independent corrective QA for P3-IR-01 through P3-IR-06; read-only except for this requested report  
Repository: `C:\Users\Nadav\Desktop\Automation Project\lighting-camera-wifi-automation`

## Gate decision

**PASS WITH CONDITIONS. Phase 4 may not begin yet.**

P3-IR-01, P3-IR-02, P3-IR-03, P3-IR-04, and P3-IR-06 are independently verified as corrected. P3-IR-05 is corrected for ordinary floating-point noise but remains incomplete at the rounding boundary: `formatEngineeringAzimuth(359.9999)` displays `360`, which is outside the normalized engineering range `[0, 360)`. This is a **Minor** confirmed defect. It does not change the authoritative backend value, corrupt geometry, or affect the reproduced `51.888999999999996 -> 51.889` case, but it fails the explicit normalized-display requirement.

The condition for a clean Phase 3 gate is to correct and independently retest P3-IR-05 at rounding boundaries, including values immediately below 360 degrees and equivalent negative/greater-than-360 inputs. Phase 4 also still requires its own explicit authorization.

## Tested baseline and environment

- Corrective implementation under test: `acd14aac431b4737192333f085dfec1b8ce93311` (`fix: address Phase 3 integration findings`).
- Corrective completion report commit: `98ba990110e63b5e4be332df7e3de456816f9ab4` (`docs: record Phase 3 corrective completion`).
- Checked-out HEAD during the retest: `98ba990110e63b5e4be332df7e3de456816f9ab4`; its parent is the implementation commit above.
- OS: Windows 11, build `10.0.26200`.
- Python: 3.12.7 in `.venv`; FastAPI 0.141.1, Pydantic 2.13.4, Shapely 2.1.2, pyproj 3.7.2.
- Frontend runtime: Node 24.19.0, pnpm 11.19.0, TypeScript 5.9.3, React 19.2.6, MapLibre GL 5.7.1, Vinext 1.0.0-beta.2.
- Rendered test: production frontend at `http://127.0.0.1:3018/` against an isolated local API at `http://127.0.0.1:8018/`, using isolated QA project and catalog directories.
- Real source input: `Input/Miracle_Mile_Lighting_Poles.kml`, 74 poles, SHA-256 `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`.

The original report `docs/phase-3-integration-review-and-qa.md` is unchanged from the corrective implementation baseline. Its SHA-256 remains `216F805A798D564E2BEE1232DA40B6DD883EBAB6BC3E64F6BC766346F447ACB4`, and `git diff --exit-code acd14aac431b4737192333f085dfec1b8ce93311 -- docs/phase-3-integration-review-and-qa.md` passed.

## Finding-by-finding result

### P3-IR-01 — Priority-area editing: PASS

Severity of original finding: Major. Corrective status: **closed**.

Independent evidence:

- Created a four-vertex priority area in the rendered production UI and persisted it.
- Rename-only changed `Priority area 1` to `QA Priority Renamed`. Before and after JSON comparison showed byte-for-value-identical `wgs84_coordinates`; only the name and modification time changed.
- Redraw started with `0 vertices`, proving the saved ring was not copied into or appended to the replacement draft.
- Cancel and failed replacement attempts preserved the saved valid area.
- A two-vertex replacement was rejected and left the saved area unchanged.
- A rendered bow-tie replacement was rejected and left the saved area unchanged.
- Independent frontend-helper and backend-model adversarial cases rejected fewer than three distinct vertices, duplicate-only inputs, non-finite values, longitude and latitude outside WGS84 bounds, self-intersection, and zero-area degeneracy.
- A different valid four-vertex replacement saved successfully. The new closed ring persisted exactly after project save/reopen.
- After explicit action-time approval, the temporary QA area was deleted in the rendered UI, saved, and reopened; it remained deleted. The operation affected only the isolated QA project.
- A synthetic invalid legacy 2.2.0 priority-area object, including an unknown custom field, was removed from active calculations and copied losslessly into `legacy_invalid_priority_areas` during migration.

No defect remains in this finding.

### P3-IR-02 — Schema/OpenAPI freshness: PASS

Severity of original finding: Major. Corrective status: **closed**.

Independent exact comparisons regenerated artifacts in memory from the current runtime and found equality for:

- `schemas/project.schema.json`;
- `schemas/openapi.json`;
- the operational fixture-catalog schema;
- the operational camera-catalog schema; and
- the operational IES-catalog schema.

`PriorityAreaCoverageSummary.warnings` is present in both the project schema and OpenAPI contract. Project schema 2.3.0, software/OpenAPI 0.3.1, fixture catalog 1.2.0, and camera/IES catalogs 1.1.0 were internally consistent. The seven frozen Phase 1 catalogs remain 1.0.0 and unchanged.

No stale generated artifact or catalog inconsistency was found.

### P3-IR-03 — Camera warning representation: PASS

Severity of original finding: Moderate. Corrective status: **closed**.

Rendered evidence:

- Assigning Phoenix 1 SMART at 10 m without lenses produced two global Validation entries, one for each enabled camera.
- A high-contrast pole warning ring was visible on the map. Unchecking the Warnings layer removed the representation and rechecking restored it.
- After selecting a different map pole (`Cobra Head 51`), activating the global camera-1 warning selected the affected pole (`Cobra Head 7`).
- Disabling camera 1 reduced the global count from two to one; camera-1 disappeared while camera-2 remained. Re-enabling restored the expected state.
- Browser console error log was empty throughout the rendered workflow.

Disabled-camera warnings were not aggregated. No defect remains in this finding.

### P3-IR-04 — Footprint provenance: PASS

Severity of original finding: Moderate. Corrective status: **closed**.

Phoenix 1 SMART was configured at 10 m with fixture azimuth 121.889 degrees, camera 1 lens JL-LN039, and camera 2 lens JL-LN042. Persisted and reopened footprint records contained:

- camera 1 H/V FOV `52.0/40.0`, lens revision 1, camera revision 1, template revision 2;
- camera 2 H/V FOV `69.0/54.0`, lens revision 1, camera revision 1, template revision 2; and
- exact `geometry_contract_version: fixed-zero-origin-1.0.0` for both.

The records also retained pole, fixture, height, fixture and relative azimuths, fixed tilt, zero XYZ origin offsets, projected CRS, geometry-model version, projected and WGS84 rings, assumptions, warnings, areas, and explicitly null/not-calculated pixel density. Save/reopen restored the same provenance and two valid footprints.

An older footprint record omitting the three additive fields remained readable with null values. Deterministic recalculation populated `(52, 40, fixed-zero-origin-1.0.0)` and `(69, 54, fixed-zero-origin-1.0.0)` as appropriate.

No defect remains in this finding.

### P3-IR-05 — Azimuth formatting: FAIL

Severity: **Minor**. Corrective status: **not fully closed**.

Ordinary presentation behavior passed: the authoritative stored camera-1 azimuth `51.888999999999996` rendered as `51.889°`, camera 2 rendered as `191.889°`, both used no more than three decimal places, and persistence retained the backend double rather than replacing it with the display string.

Confirmed defect reproduction:

1. Evaluate the shipped presentation helper `formatEngineeringAzimuth(359.9999)`.
2. Observe the returned string `"360"`.

Expected: a normalized displayed azimuth in `[0, 360)`, therefore `0` after three-decimal rounding (or another representation that never displays 360).  
Actual: `360`.

Cause: `frontend/app/lib/phase3-workflows.mjs` normalizes before calling `toFixed(3)`; rounding can therefore cross from 359.9999 to 360. The result is used by `frontend/app/components/PoleInspector.tsx`. The map-handle callback in `frontend/app/components/EngineeringWorkspace.tsx` similarly rounds with `Number(azimuth.toFixed(3))`, so a near-north drag may also stage 360 even though the backend contract requires an azimuth below 360.

Other adversarial outputs were correct: `360 -> 0`, `721.23456 -> 1.235`, and the reproduced floating-noise value rendered as `51.889`. This is presentation/boundary behavior; no evidence showed mutation of an already authoritative backend value.

No fix was made during QA.

### P3-IR-06 — Documentation consistency: PASS

Severity of original finding: Minor. Corrective status: **closed**.

Cross-document review found the current Phase 3 MVP described consistently:

- camera optical centers use the fixture reference origin with fixed X/Y/Z offsets of zero;
- optical-center height equals configured fixture/pole height;
- fixture azimuth rotates both cameras together while their catalog relative azimuths remain immutable; and
- the current ground model is flat local ground at Z=0.

Mechanical offsets, measured mounting refinements, terrain, slope, occlusion, and related refinements are identified as future authoritative template or geometry-model revisions, not current behavior or unimplemented prerequisites for the approved MVP. No contradictory current-contract statement was found.

## Regression and validation evidence

| Check | Result | Evidence |
|---|---:|---|
| Complete backend suite | PASS | `85 passed`; one existing non-failing Starlette/httpx deprecation warning |
| Engineering/source validator | PASS | Seven frozen catalog/schema pairs, identifiers, traceability, units, domains, cross-references, IES hashes, and supplied-source hashes validated |
| Exact project-schema/OpenAPI freshness | PASS | Checked-in JSON exactly equaled runtime-generated JSON |
| Operational generated contracts | PASS | Fixture, camera, and IES generated schemas exactly current |
| Migrations 1.0.0, 2.0.0, 2.1.0, 2.2.0 | PASS | All reached 2.3.0 while preserving source, edits, calculated/recommended data; 2.2 invalid priority quarantine verified |
| Authoritative coordinates | PASS | IDs, numeric longitude/latitude, raw coordinate strings, source metadata, and source bytes preserved |
| Frontend tests | PASS | `5 passed`, `0 failed` |
| Strict TypeScript | PASS | Zero errors |
| ESLint | PASS | Zero errors and warnings |
| Production build | PASS | Direct build with installed Vinext CLI completed client references, server references, RSC, client, and SSR |
| Phase 3 geometry smoke | PASS | Phoenix fixed 140-degree and Solitaire fixed 120-degree separation; 35-degree tilt; coupled fixture rotation; valid footprints and provenance |
| Phase 1/2 regression checks | PASS | Frozen inputs/catalogs, source/edit separation, existing-pole mode, Phase 2 fixture configuration, and later-engine gates intact |
| Rendered save/reopen workflow | PASS | 74 poles, geometry, warnings, provenance, revisions, replacement priority geometry, and exact source coordinate evidence restored |
| Browser console | PASS | No console errors |

Independent migration fixtures specifically retained `source`, `pole_edits`, `calculated_layers`, and `recommended_layers` for every supported source schema. Legacy camera-orientation overrides remained readable and continued to block unsafe footprint calculation until reset. Older footprint records remained readable and recalculable.

The supplied 74-pole KML reopened with projected CRS `EPSG:32617`; the first selected source coordinate remained exactly `-80.26234411,25.74920999,0`. `Input/` and all seven frozen Phase 1 engineering catalogs compare unchanged against the Phase 1 baseline commit `9f7f91f`.

## Rendered geometry smoke details

- Phoenix 1 SMART exposed immutable `-70°/+70°` camera offsets and 35-degree downward tilt. With fixture azimuth 121.889 degrees, the inspector showed `51.889°` and `191.889°`: fixed 140-degree separation.
- Camera 1 with JL-LN039 produced a valid 241.6 m² footprint; camera 2 with JL-LN042 produced a valid 1147.0 m² footprint. Changing fixture azimuth moved both absolute directions together.
- Changing to Solitaire SMART exposed immutable `-60°/+60°` offsets and absolute directions `300°/60°` at fixture azimuth zero: fixed 120-degree separation.
- Missing lenses produced clear per-camera warnings and no fabricated footprint. Disabling an affected camera removed its polygon and warning without turning the disabled state into an error.
- LITE/WIFI and later Phase 4-6 controls remained non-camera/non-operational as designed. No analytics, recognition, LPR, compliance, suitability, or pixel-density claim appeared.

## Confirmed defects

1. **Minor — normalized azimuth can display as 360 at a rounding boundary** (`P3-IR-05`).
   - Reproduction, expected/actual behavior, and affected components are documented under P3-IR-05 above.
   - Affected files/components: `frontend/app/lib/phase3-workflows.mjs`, `frontend/app/components/PoleInspector.tsx`, and potentially the near-north map-handle rounding path in `frontend/app/components/EngineeringWorkspace.tsx`.
   - No data corruption was observed and no fix was made.

No Blocker, Critical, Major, or Moderate defect was found in the corrective scope.

## Regressions

No Phase 1, Phase 2, schema, migration, coordinate, catalog, source-input, or Phase 3 geometry regression was found. The original Phase 3 QA report remains unchanged.

## Accepted limitations

- Flat local ground Z=0; no terrain, slope, obstacle, or occlusion model.
- Symmetric rectilinear pinhole geometry using catalog H/V FOV; no distortion model.
- Fixed zero XYZ mounting offsets for the current template revision.
- Explicit compatible pinned lens required for every enabled camera.
- Pixel density remains null/not-calculated.
- Priority areas are single exterior rings without holes or multipolygon authoring.
- Invalid legacy 2.2 priority areas are quarantined for recovery and require explicit redraw before use.
- Phase 4 Wi-Fi coverage, Phase 5 photometry, Phase 6 CAP, reporting, proposed-pole, automatic-placement, and coordinate-optimization functionality remain unimplemented and gated.

These are approved or explicitly deferred limitations, not defects in this retest.

## Advisory toolchain findings

- **Advisory:** invoking the ordinary pnpm build wrapper in the non-interactive QA shell attempted dependency-directory refresh and aborted with `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`. The direct build using the already installed, lockfile-pinned Vinext CLI passed. No source or lockfile change occurred.
- **Advisory:** the production build continues to report the existing large MapLibre chunk (greater than 500 kB) and Vinext route-classification notices. They did not fail the build or affect the rendered QA workflow.
- **Advisory:** the backend suite emits the existing Starlette/httpx deprecation warning. It did not fail a test.

## Final authorization statement

The corrective implementation substantially closes the original Phase 3 QA findings, but P3-IR-05 still fails one explicit normalization boundary. The Phase 3 corrective gate is therefore **PASS WITH CONDITIONS**, and **Phase 4 may not begin** until that Minor defect is corrected, independently retested, and the separate Phase 4 authorization is granted.
