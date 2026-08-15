# Phase 3 completion report

Completion date: 2026-08-15

Implementation commit: `c8814587d08731cbb5e125d644b6a55f67483d48`

Scope: Phase 3 fixed-mount SMART camera ground geometry, map visualization, overlap, priority areas, and pixel-density architecture only.

Disposition: **Implementation complete; independent integration review and QA pending.** Phase 4 and later work was not started.

## Implementation summary

- Added deterministic flat-ground pinhole-frustum projection in the project-selected projected CRS, with WGS84 result geometry solely for map display/interchange.
- Added two fixed camera slots for Phoenix 1 SMART (`-70/+70` degrees) and Solitaire SMART (`-60/+60` degrees), fixed 35-degree downward tilt, immutable zero XYZ optical-center offsets, and fixture-level rotation of both slots.
- Added explicit compatible lens/revision and enabled-state handling, with no default lens and no per-camera direction/tilt UI.
- Added per-camera map polygons, distinct camera-1/camera-2 styles, overlap polygons and pairwise square-metre metrics, fixture sidebar azimuth editing, and a draggable fixture rotation handle.
- Added WGS84 priority-area draw/name/select/edit/delete persistence, projected-metre intersection unions, covered area, percentage, and intersecting footprint IDs.
- Added complete calculation provenance, deterministic warnings, and an explicit revision-aware pixel-density `not-calculated` seam with no analytics thresholds or suitability claims.
- Preserved source uploads, source pole IDs, raw coordinate strings, numeric coordinates, user configuration, calculated output, and recommendations as separate layers.

## Contract, catalog, and migration changes

- Project schema: additive `2.1.0` to `2.2.0`; software/API version `0.3.0`.
- Supported project migrations: `1.0.0`, `2.0.0`, and `2.1.0` to `2.2.0`.
- Added typed `priority_areas` user data and typed `camera_geometry` calculated data containing footprints, overlaps, priority summaries, warnings, assumptions, and pixel-density state.
- Fixture-model operational contract: additive `1.1.0` to `1.2.0`. SMART fixtures append immutable mounting-template revision 2 with `geometry_contract_version=fixed-zero-origin-1.0.0` and explicit X/Y/Z offsets of `0/0/0 m`. Revision-1 templates remain available for pinned projects.
- Camera-equipment and IES operational contracts remain `1.1.0`. The seven Phase 1 engineering catalogs remain frozen at `1.0.0`.
- Legacy Phase 2 per-pole relative-azimuth/downward-tilt fields remain in the project contract and migrate byte/data-for-data. They are no longer created or edited by the UI. Their presence blocks the affected footprint until the user explicitly resets orientation to the immutable template.
- Generated `project.schema.json`, `fixture-model-catalog.schema.json`, and `openapi.json` were regenerated from current models.

## Geometry definition

Coordinate frame:

- Projected X is east, Y is north, and Z is up, in metres.
- Camera azimuth `a` is clockwise from true north and normalized as `((a % 360) + 360) % 360` into `[0,360)`.
- Downward tilt `t` is positive below horizontal. Phase 3 fixes `t=35°`.
- Optical center is `(pole_projected_x, pole_projected_y, height_m)` because approved template offsets are `(0,0,0) m`.
- Local ground is the horizontal plane `Z=0`.

For horizontal FOV `H` and vertical FOV `V`, the camera basis is:

```text
forward  f = (sin(a) cos(t),  cos(a) cos(t), -sin(t))
right    r = (cos(a),        -sin(a),         0)
image-up u = (-sin(a) sin(t), -cos(a) sin(t), cos(t))
```

For each ordered boundary corner `(sx, sy)` in `(-1,-1), (1,-1), (1,1), (-1,1)`:

```text
ray d = f + sx * tan(H/2) * r + sy * tan(V/2) * u
lambda = height_m / -d.z
ground point = (origin.x + lambda*d.x, origin.y + lambda*d.y)
```

The ray direction need not be normalized because the plane-intersection scale cancels its length. A complete footprint is rejected when any input/ray is non-finite, `d.z >= -1e-10`, `lambda <= 0`, the polygon is invalid, or projected area is at most `1e-8 m²`. No clipping or fabricated closing point is used. Valid vertices are rounded to nine projected-metre decimals, ordered counter-clockwise, rotated to start at the lexicographically smallest `(X,Y)`, and closed by repeating that vertex. WGS84 output is rounded to ten decimal degrees.

Polygon area, pairwise overlap, priority intersections, and priority covered unions use Shapely in projected metres. Priority coverage unions all intersecting valid enabled footprints before division, so a priority-area percentage does not double-count overlaps. The map's overall overlap total is explicitly labeled summed pairwise overlap.

## Provenance and invalid-state policy

Every footprint result records pole ID; fixture ID/revision; template revision; slot ID; camera and lens IDs/revisions; height; fixture, relative, and absolute azimuths; fixed tilt; zero offsets; projected CRS; geometry-model version `flat-ground-pinhole-1.0.0`; assumptions; warnings; projected/WGS84 geometry; area; and pixel-density status.

An enabled camera produces no polygon when height, explicit compatible lens, camera/lens revision, fixture/template revision, fixed mounting contract, FOV values, or a complete stable ground intersection is unavailable. A disabled camera produces no polygon and no error. LITE/WIFI fixtures produce no camera results. Geometric output is never described as facial recognition, LPR, people counting, analytics quality, or compliance performance.

## Requirement traceability

| Requirement | Implementation | Tests/evidence |
|---|---|---|
| Fixed SMART slots, signs, normalization, coupled rotation | `catalog_models.py`, fixture seed, `camera_geometry.py`, `PoleInspector.tsx`, `EngineeringMap.tsx` | Approved-example parameterization; rotation/separation test; rendered fixture handle workflow |
| Projected frustum/ground intersection and invalid rays | `camera_geometry.py` | All three lenses × representative heights/azimuths; horizontal/upward/non-finite/degenerate cases; canonical ring tests |
| Zero offsets and exact provenance | `catalog_models.py`, project result models, fixture template r2 | Zero-origin/provenance/revision tests; rendered provenance labels |
| Missing input, disabled state, legacy override safety | `camera_geometry.py`, `PoleInspector.tsx` | Missing height/lens/revision, disabled, and legacy-preservation/blocking tests; rendered missing-state workflow |
| Overlap visualization and metrics | `camera_geometry.py`, `EngineeringMap.tsx`, `EngineeringWorkspace.tsx` | Overlap-area tests; rendered 4-footprint/3-pair workflow |
| Priority-area CRUD, persistence, intersections | project models, geometry service, workspace/map | Intersection/union and exact save/reopen tests; rendered draw/save/reopen workflow |
| Pixel-density boundary | `PixelDensityStatus`, footprint provenance | Null/not-calculated assertions; UI geometric-only labels |
| Source-coordinate integrity | geometry service uses `source.poles`; no coordinate mutation API/UI | all-pole tuple comparisons, migration tests, rendered raw-coordinate before/after/reopen evidence |
| No independent camera angle editing | fixed/disabled inherited fields and explicit legacy reset only | rendered-source tests assert angle change handlers are absent |
| Later-phase gating | workspace controls and service boundary | rendered tests and manual workflow; Phase 4+ controls remained disabled |

## Automated validation

Final results:

- Backend: `81 passed` in 2.37 seconds; one unchanged non-failing Starlette/httpx deprecation warning.
- Engineering/source validator: PASS for all seven frozen Phase 1 catalogs, schemas, domain checks, cross-references, supplied IES hashes, and supplied-source hashes.
- Frontend rendered/workflow tests: `5 passed`, `0 failed`.
- Strict TypeScript: PASS.
- ESLint: PASS with zero errors or warnings.
- Production Vinext build: PASS across client/server reference analysis, RSC, client, and SSR. It retains the known non-failing >500 kB MapLibre chunk advisory and Vinext route-classification advisory.
- Schema freshness: backend tests compare all generated contracts to current model generation and pass.
- The normal pinned `pnpm run build` wrapper attempted a non-interactive dependency refresh after the package-version update and aborted with `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`; invoking the same installed Vinext CLI directly with pinned Node completed the production build successfully. No dependency content was changed by that aborted wrapper.

## Real rendered manual workflow evidence

The app was run at `http://localhost:3013/` against an isolated local API at port 8013.

1. Imported `Input/Miracle_Mile_Lighting_Poles.kml`: 74 poles, LITE 74/WIFI 0/SMART 0, `EPSG:32617`, first raw coordinate `-80.26234411,25.74920999,0`.
2. Assigned Cobra Head 7 to Phoenix 1 SMART template r2 at 10 m. With explicit JL-LN039/JL-LN042 lenses, the two valid results were at 290°/70° for fixture azimuth 0°, with 241.6 m² and 1,147.0 m² footprints.
3. Dragged the fixture map handle to azimuth 121.889°. Both absolute camera azimuths updated immediately to 51.889°/191.889°, retaining 140° separation. The source raw coordinate remained exact.
4. Changed only camera 1 to JL-LN037: its footprint changed while camera 2 remained 1,147.0 m². Disabled camera 2: only its footprint became not calculated.
5. Cleared height and camera-1 lens: no footprint and explicit `Fixture/pole height is required` plus no-default-lens warning. Restored valid inputs.
6. Selected a second pole and assigned Solitaire SMART template r2. At fixture azimuth 0°, the rendered slots reported 300°/60°, preserving the approved 120° separation.
7. With two valid SMART poles the map displayed four distinct camera footprints, three pairwise overlap polygons, and 11,557.9 m² summed pairwise overlap.
8. Drew and named `Storefront priority`. The projected summary reported 13,960.3 m² covered of 14,469.8 m², or 96.5%, explicitly labeled geometric only.
9. Saved and reopened the portable project JSON through the rendered controls. Reopen restored LITE 72/SMART 2, four valid footprints, three overlap pairs, priority geometry/summary, fixed revisions, and the exact first raw coordinate.
10. Browser console errors/warnings: none. Phase 4 Wi-Fi, Phase 5 lighting, Phase 6 CAP, reporting, and automatic/proposed-pole controls remained unavailable.

## Source and QA-evidence integrity

- Supplied Miracle Mile source SHA-256 remains `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
- Automated and rendered checks retained 74 source IDs and exact `(raw_coordinates, longitude, latitude)` values through assignment, calculation, rotation, overlap, priority-area save, and reopen.
- `Input/` files and all seven frozen Phase 1 catalogs were not changed.
- Approved QA evidence was added without rewriting findings. Preserved hashes:
  - Phase 2 integration report: `FB6A391D2623ED9F8E547CC20516793354EDAA0476746BE3D412F3E94234AC03`.
  - Phase 2 corrective retest: `F4492A855351A67899514F17C7B339C062F4FA1D9D54B6F7E55FCC1F3E913294`.
  - Phase 2 NIR-01 final retest: `47F915A4D138B93E97AA0DF46CB0AF8DA8075FF9E7A30846A788E6327D4034D7`.

## Known limitations and deferred items

- Flat local ground only; no DEM, terrain slope, buildings, vegetation, pole/fixture occlusion, refraction, or obstacles.
- Symmetric rectilinear catalog FOV only; no lens-distortion correction.
- Wide JL-LN037 vertical FOV at 35° down places its upper boundary ray close to horizontal and can create very large but mathematically valid flat-ground footprints. The documented `d.z` tolerance rejects horizontal/unstable cases rather than clipping them.
- No default lens; every enabled slot requires an explicit compatible pinned lens revision.
- Pixel density remains explicitly null/not calculated. No recognition, LPR, people-counting, analytics, compliance, or operational-suitability threshold exists.
- Priority polygons are single exterior rings; holes/multipolygons are not Phase 3 user inputs.
- Pairwise overlap totals can include the same ground area in multiple pairs and are labeled accordingly; priority covered area uses a union and does not double-count.
- Existing revision-1 SMART templates and legacy per-pole angle overrides remain preserved but block Phase 3 calculation until explicit adoption/reset.
- Wi-Fi coverage, photometry/IES illuminance, CAP recommendations, reporting/presentation, proposed poles, automatic placement, coordinate optimization, and every Phase 4+ feature remain unimplemented.

## Handoff recommendation

Open an independent session **“92 – Phase 3 Integration Review & QA”** against implementation commit `c8814587d08731cbb5e125d644b6a55f67483d48` and this completion report. Treat the report as a claim set requiring independent adversarial and rendered verification. Do not begin Phase 4 unless Phase 3 receives its own acceptance decision and separate authorization.
