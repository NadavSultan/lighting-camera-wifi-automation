# Phase 4 lighting calculation engine completion report

Date: 2026-08-17  
Role: dedicated Phase 4 implementation engineer  
Repository: `C:\Users\Nadav\Desktop\Automation Project\lighting-camera-wifi-automation`

## Completion boundary

The authorized Phase 4 implementation is complete at implementation commit `eafd320369600ff4c8d32b8dc32c80e1e81b3d24` (`feat: implement Phase 4 lighting calculation engine`). This is an implementation claim set, not independent QA evidence. Phase 4 is not declared approved. Phase 5 conceptual Wi-Fi and all later work remain unauthorized and were not implemented.

## Versions and contracts

- Project JSON Schema: `2.4.0`.
- Software/API/frontend/backend: `0.4.0`.
- Fixture operational catalog: retained at `1.2.0`.
- Camera operational catalog: retained at `1.1.0`.
- IES operational catalog: additive `1.2.0`, adding immutable `file_history` while preserving original bytes, filename, SHA-256 identity, parsed metadata, validation state, and explicit associations.
- Seven frozen Phase 1 engineering catalogs: unchanged at `1.0.0`.
- Generated `schemas/project.schema.json`, `schemas/openapi.json`, and `schemas/ies-library.schema.json` match the exact in-memory runtime contracts.

Primary implementation files are `backend/app/services/lighting_calculation.py`, `backend/app/models.py`, `backend/app/main.py`, `backend/app/catalog_models.py`, `backend/app/services/catalogs.py`, `backend/app/services/configuration.py`, `frontend/app/components/EngineeringWorkspace.tsx`, `frontend/app/components/EngineeringMap.tsx`, `frontend/app/lib/types.ts`, `frontend/app/lib/api.ts`, and `frontend/app/lib/phase4-workflows.mjs`. Phase 4 mathematical coverage is in `backend/tests/test_phase4_lighting_calculation.py`; rendered/workflow coverage is in `frontend/tests/rendered-html.test.mjs`.

## Calculation areas and persistence

`calculation_areas` is a lighting-only user-configuration collection. It is structurally separate from camera `priority_areas`, future Wi-Fi analysis, customer source polygons, and derived/recommended layers. Each record has stable ID, editable name/classification, one validated WGS84 exterior ring, plane elevation, grid spacing, maintenance factor, timestamps, polygon revision, state, warnings, assumptions, and provenance.

Create, select, edit, explicit empty-draft redraw, cancel, invalid-draft rejection, delete, and explicit calculate/recalculate workflows are present. Rename/settings edits preserve the existing ring. Redraw replaces the prior valid ring only after complete validation and increments the polygon revision. Derived results persist separately under `lighting_calculations.results`; stale configuration removes the prior result rather than presenting it as current.

Defaults are 0.0 m plane elevation, 2.0 m point spacing, and maintenance factor 1.0. Maintenance factor is `(0,1]`; spacing is finite, positive, and at most 1000 m.

## Grid generation

- Engineering calculations use the project-selected projected CRS with metre axes; WGS84 is display/interchange only.
- The grid is anchored to the projected CRS `(0,0)` lattice. Candidate coordinates are exact integer multiples of requested spacing.
- Ordering is deterministic: increasing projected Y, then increasing projected X.
- Points covered by the polygon buffered by `1e-7 m` are accepted, implementing the documented inside-or-boundary numeric tolerance.
- A result exceeding 25,000 accepted points is rejected. A bounding-box candidate safeguard also rejects unsafe payloads before enumeration.
- Spacing is never silently enlarged and accepted points are never silently dropped.
- A valid polygon yielding zero points returns an explicit warning, an empty point list, null illuminance statistics, and null uniformity ratios.

## Photometric frames, interpolation, and equations

World coordinates are X east, Y north, Z up. The immutable photometric origin is the authoritative source-pole X/Y transformed to the project CRS and Z equal to configured mounting height. Fixture azimuth never translates this origin.

Azimuth zero is project/grid north and positive rotation is clockwise. The IES C0 plane aligns with selected fixture azimuth. For a point relative to the fixed origin:

- world azimuth is `atan2(dx, dy)`;
- local C-plane angle is `(world azimuth - fixture azimuth) mod 360`;
- vertical Type C angle is `gamma = atan2(horizontal distance, mounting height - plane elevation)`;
- linear interpolation is performed across exact vertical angles within each adjacent C-plane, then across C-planes;
- full 0/360 data use a continuous seam; supported 0-90 and 0-180 plane ranges use deterministic Type C symmetry expansion;
- candela values are multiplied by the exact source candela multiplier. Absolute photometry is used directly without treating the `-1` lumens-per-lamp sentinel as physical flux.

For slant distance `r`, vertical separation `h`, and interpolated intensity `I(gamma,C)`:

`E_horizontal = I(gamma,C) * cos(incidence) / r^2 = I(gamma,C) * h / r^3` lux.

Eligible fixture contributions are summed with `math.fsum`; the area maintenance factor is then applied explicitly. Full precision remains authoritative; UI formatting does not rewrite results.

No physical luminaire tilt is applied. `TILT=NONE` is preserved as IES metadata and is not represented as proof of installed zero tilt. The exact evaluation order is translate to the fixed origin, rotate world direction into the local C-plane frame, interpolate intensity, apply slant distance/incidence, sum contributors, then apply maintenance factor.

## Fixture/IES eligibility and compatibility

Contributors must be active existing poles with an explicit active lighting-capable fixture model/revision, valid mounting height above the area plane, explicit active compatible IES record/revision, active association, and active calculation-eligible equipment references. Incomplete/ineligible poles are excluded with explicit warnings; nothing is guessed or silently treated as a configured zero source.

Exact supplied-file SHA-256 restrictions are:

- Phoenix 100 W `4a897fb04b6d8f6c75c94a3ceba473391021aee6d506f05357f48bc01d26d363` and Phoenix 120 W `eb05f9cc5064ab6a0fa19e2886ff0af9cecfa06a7f2ef0bc2e269e57929173c1`: Phoenix 1 LITE, WIFI, SMART only.
- Solitaire D01 `fda02adb7ca11c6ca5af8e930bdc5e1b8ffb5f558eb8a432a7d4fae87e18db38` and Solitaire D02 `4efa14cfe43e2214080bcd09d6424b353322010c07717106bc3218297839c86a`: Solitaire LITE, WIFI, SMART only.

Association remains an explicit user action, pole selection remains explicit, and no IES default is created. Other newly uploaded supported files are never assigned or associated by filename inference.

## Solitaire treatment

For both Solitaire records, numeric input watts of 50 W controls and the original internal `[LUMINAIRE]` 60W identifier remains byte-for-byte unchanged. Calculated results promote the 50W/60W discrepancy into fixture provenance and the global validation list.

For D02, raw `-0.692 m` width/length values and the original validation warning remain unchanged. Negative dimensions are not converted to positive values. Provenance explicitly states that negative luminous-opening dimensions are preserved and excluded from the Phase 4 far-field point-source model.

## Results, UI, and disclaimers

Each ordered point persists projected coordinate, WGS84 display coordinate, plane elevation, maintained horizontal lux, payload-safe per-fixture contributions, warnings, and stable identity. Each area displays point count, spacing, Eavg, Emin, Emax, Emin/Eavg, Emin/Emax, contributing-fixture count, assumptions, warnings, and full fixture/IES revision/SHA/height/azimuth/origin provenance. Empty and zero-valued sets never divide by zero; unavailable uniformities are null and display as an em dash.

The map has distinct Calculation Areas, Calculation Points, and Lighting Results layers. Lighting teal/cyan/result colors remain distinct from LITE red, WIFI yellow, SMART blue, camera purple/cyan, camera overlap pink, priority amber, and warning orange. Phase 5 Wi-Fi and Phase 6+ controls remain disabled.

Every result displays: “Not independently validated against AGi32 or another professional photometric reference tool.” The UI also states that this is the approved simplified direct-light model and not a standards-compliance determination. No result is labeled compliant, passing, suitable, professional-grade, or equivalent to AGi32.

## Automated validation evidence

Final commands and outcomes on the implementation tree:

- Backend complete suite: PASS, 99 tests (6 API, 1 engineering-data, 12 KML, 4 models, 28 Phase 2, 34 Phase 3, 14 Phase 4). One existing non-failing Starlette/httpx2 deprecation warning remains.
- Engineering/source validator: PASS; seven frozen catalogs matched schemas and all supplied-source hashes/IES parses/references passed.
- Exact project schema, OpenAPI, and operational-catalog in-memory freshness: PASS within the backend suite.
- Migrations from `1.0.0`, `2.0.0`, `2.1.0`, `2.2.0`, and `2.3.0`: PASS; Phase 4 collections start empty and prior source, edits, camera geometry, priority areas, calculated/recommended data, and quarantine data remain preserved.
- Frontend rendered/workflow suite: PASS, 7 tests.
- Strict TypeScript: PASS.
- ESLint: PASS.
- Production Vinext build: PASS. Existing non-failing MapLibre chunk-size and route-classification advisories remain.
- `git diff --check`: PASS; line-ending notices are advisory only.

Synthetic validation covers hand-computable nadir/off-axis direct horizontal illuminance, inverse-square and incidence behavior, vertical and C-plane interpolation, 0/360 seam, asymmetric azimuth rotation, multiple-fixture summation, maintenance scaling, grid clipping/boundary/order/limit, empty and zero inputs, deterministic recalculation, high-latitude projected CRS, and invariant origin coordinates. All four supplied IES files pass parsing/calculation smoke tests; those smoke cases are not claimed as independent accuracy validation.

## Rendered application evidence

Production-rendered local workflow used `Input/Miracle_Mile_Lighting_Poles.kml` and preserved all 74 source poles. Through the real UI:

- Phoenix 100 W and Solitaire D02 were uploaded with original names/bytes, explicitly associated to Phoenix 1 SMART and Solitaire LITE respectively, and explicitly selected.
- Forty Cobra Head poles were configured as Phoenix 1 SMART at 10 m; fourteen Other poles as Solitaire LITE at 9 m.
- A separate Road calculation polygon used a 0 m plane, 4 m grid, and 0.8 maintenance factor.
- The result contained 286 points and 54 contributors. At the first orientation it displayed Eavg 6.95 lx, Emin 0.53 lx, and Emax 36.61 lx.
- Rotating the Phoenix fixtures to 90 degrees and recalculating changed the result to Eavg 6.72 lx, Emin 0.37 lx, and Emax 38.16 lx. Persisted provenance retained all fixed origin coordinates; only distribution orientation/results changed.
- Save/reopen restored 286 points and the 6.72/0.37/38.16 lx statistics, calculation provenance, disclaimers, selected IES pins, and enabled lighting layers.
- The selected rendered source coordinate remained the exact imported raw string `-80.26234411,25.74920999,0` for the first verified pole. The persisted first-pole ID/longitude/latitude remained `pole-443127e3a723e1b3`, `-80.26234411`, `25.74920999`.
- Embedded source bytes hashed to `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`, exactly matching persisted source SHA-256.
- Camera `priority_areas` remained empty while one lighting `calculation_area` persisted; the two collections were visibly separate.
- Phase 5 conceptual Wi-Fi and CAP controls were disabled.
- Browser console error log was empty.

The rendered run deliberately left SMART camera lenses unassigned, producing the expected Phase 3 camera warnings in the global validation experience. This did not make the lighting fixtures ineligible and demonstrates warning-layer coexistence without guessing lenses.

## Source and regression preservation

No `Input/` file, frozen Phase 1 catalog, source pole, raw coordinate, or source byte was modified. Git changes are additive Phase 4 contracts/services/UI/tests/documentation plus the additive operational IES history field. Phase 1 workflows, Phase 2 catalogs/IES/assignment/bulk/revisions, and Phase 3 camera geometry/priority/azimuth behavior remain covered by their complete regression suites.

## Known limitations

- No AGi32 or other professional-reference comparison exists; no accuracy-equivalence tolerance is claimed.
- Zero physical luminaire tilt and C0-to-fixture-azimuth alignment are approved MVP assumptions pending manufacturer/professional validation.
- Model excludes terrain/slope, occlusion, buildings, obstructions, shadows, reflected light, interreflection, atmospheric effects, near-field luminous-opening geometry, and depreciation beyond explicit area maintenance factor.
- No standards targets, compliance evaluation, lighting recommendations, or suitability judgment exist.
- Persisted per-fixture point contributions are omitted when point-count times contributor-count exceeds 100,000; complete fixture provenance and total lux remain.
- Map rendering uses point-based result coloring, not an independently validated isolux/contour engine.

## Independent QA handoff

Independent QA should treat this report as claims to verify read-only. Recommended focus: exact equation/orientation implementation, interpolation/seam/symmetry cases, point-limit and boundary policy, supplied SHA compatibility restrictions, IES revision immutability, Solitaire warnings, all five migrations, exact generated-contract freshness, 74-pole rendered save/reopen/rotation behavior, source bytes/coordinates, camera-priority separation, Phase 5+ gating, map responsiveness, and browser console. QA must not implement fixes and must not approve or begin Phase 5.
