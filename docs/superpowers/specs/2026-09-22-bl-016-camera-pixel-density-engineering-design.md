# BL-016 Camera Pixel-Density Map — Engineering Design

Date: 2026-09-22

Status: design approved in conversation; implementation remains separately gated

Scope: BL-016 / WA-09 only

Architecture source: `docs/bl-016-camera-pixel-density-architecture.md`

## 1. Objective

Implement a deterministic, persisted camera pixel-density colour map for the existing fixed-camera workflow. The map reports horizontal image density as pixels across a front-facing reference face of width `0.16 m`, abbreviated `px/face`.

The feature is geometric and informational. It is VideoCAD-style in its use of horizontal pixels per object width and AUTO midpoint height, but it does not claim numerical parity with VideoCAD. Lens distortion, terrain, occlusion, recognition performance, analytics performance, and compliance remain excluded.

## 2. Approved decisions

The following decisions are binding for BL-016 V1:

1. The backend owns all engineering calculations and persists deterministic vector geometry. The frontend only requests calculation and renders returned or reopened results.
2. The measurement plane is the AUTO midpoint between the project lower and upper projection planes. Defaults are `0.5 m`, `2.0 m`, and therefore `1.25 m`.
3. Density is horizontal pixels across a front-facing `0.16 m` reference face centered on the measurement plane.
4. Band classification uses the unrounded calculated density. A value exactly on a threshold belongs to that threshold's band.
5. The project maximum visible distance defaults to `50.0 m` and is represented by a deterministic 128-sided polygon in the project CRS.
6. V1 supports at most 200 enabled cameras per calculation.
7. Output limits are 20,000 overlap regions, 250,000 persisted geometry vertices, and 25 MiB for the compact serialized pixel-density result.
8. Any project-level validation or output-limit failure is atomic: the submitted project and previous result remain unchanged.
9. Calculation is explicit through **Calculate camera density**. Engineering-significant edits make the previous result stale; stale geometry remains stored for audit but is hidden from the map.
10. Successful calculation automatically enables the density layer and opens the colour legend. Layer and legend visibility remain independent presentation controls afterward.
11. The fixed V1 palette is Option A, **Balanced engineering**, at `0.58` fill opacity.
12. Overlap density is never summed or averaged. The highest contributing density supplies the base colour; a separate overlay communicates multiplicity.
13. Clicking a density or overlap location opens a read-only map popup with the displayed band, winning camera, all covering cameras, and multiplicity.
14. Project schema becomes `2.8.0`; software and API version become `0.8.0`.
15. Migration is additive and lossless. It adds defaults and an empty result state but never fabricates historical density results.
16. V1 uses the ideal rectilinear pinhole model. Lens distortion is explicitly excluded until revision-pinned calibration data exists.

## 3. Compatibility boundary

BL-016 extends but does not replace the accepted Phase 3 camera geometry layer.

- Existing `camera_geometry` footprints, overlaps, warnings, provenance, and freshness behavior remain intact.
- The legacy `CameraFootprintResult.pixel_density.method = "not-calculated"` seam remains unchanged for compatibility.
- New editable settings and derived output live under dedicated `camera_pixel_density_profile` and `camera_pixel_density` fields.
- Source poles, exact uploaded bytes, customer coordinates, pole edits, catalog histories, pinned revisions, lighting, Wi-Fi, CAP, and report results are not rewritten.
- Existing-pole mode remains mandatory. BL-016 never proposes, moves, optimizes, or deletes poles or cameras.

## 4. Coordinate and camera frame

Use the existing conventions in `docs/coordinate-conventions.md` and `backend/app/services/camera_geometry.py`:

- World projected axes: `X` east, `Y` north, `Z` up.
- Azimuth: degrees clockwise from true north.
- Downward tilt: degrees below horizontal.
- Optical origin: source-pole projected `X/Y`, fixture height as `Z`, and approved zero XYZ camera-origin offsets.
- Camera basis:

  ```text
  forward  = (sin(a) cos(t),  cos(a) cos(t), -sin(t))
  right    = (cos(a),        -sin(a),         0)
  image_up = (-sin(a) sin(t), -cos(a) sin(t), cos(t))
  ```

For a world point `P` and optical origin `O`, define:

```text
delta = P - O
x_camera = dot(delta, right)
y_camera = dot(delta, image_up)
z_camera = dot(delta, forward)
```

`z_camera` is positive forward depth. A point is inside the ideal rectilinear frustum only when:

```text
z_camera > 1e-9 m
abs(x_camera) <= z_camera * tan(horizontal_fov_deg / 2)
abs(y_camera) <= z_camera * tan(vertical_fov_deg / 2)
```

All calculations occur in the validated metre-based project CRS. WGS84 rings are display/interchange copies only.

## 5. Projection planes and valid envelope

The project profile owns:

```json
{
  "lower_projection_height_m": 0.5,
  "upper_projection_height_m": 2.0,
  "measurement_height_mode": "midpoint",
  "maximum_visible_distance_m": 50.0,
  "legend_id": "face-density-0.16m-v1"
}
```

Validation rules:

- Every numeric value is finite.
- `0 <= lower_projection_height_m < upper_projection_height_m`.
- `maximum_visible_distance_m > 0`.
- The derived midpoint is strictly between the lower and upper planes.
- The project CRS is projected and has metre axes.

The projection envelope is the horizontal projection of the camera frustum clipped vertically to the closed slab between the lower and upper planes and horizontally to the distance cap. The density domain is the frustum intersection on the midpoint plane, further clipped to that envelope and cap. Only the density domain receives colour. The stored projection envelope remains available for provenance and boundary inspection.

AUTO midpoint is:

```text
measurement_height_m =
    (lower_projection_height_m + upper_projection_height_m) / 2
```

This follows VideoCAD's published AUTO/Within-projection midpoint convention while retaining this application's own deterministic geometry contract.

## 6. Pinhole density equation

For a camera with horizontal pixel count `resolution_width_px` and horizontal FOV `horizontal_fov_deg`:

```text
fx_px = resolution_width_px /
        (2 * tan(horizontal_fov_deg / 2))

px_per_face = fx_px * 0.16 m / z_camera_m
```

The reference face is centered at the evaluated midpoint-plane point. Its width axis is parallel to camera-right, so it is front-facing in the horizontal criterion. The unrounded double-precision result controls band membership.

To make threshold boundaries deterministic, a calculated value within `1e-9 px/face` of a configured threshold is snapped to that threshold for classification only. Persisted display values and statistics may be rounded, but rounding never chooses the band.

This equation does not model:

- face yaw or pitch away from the front-facing reference orientation;
- radial or tangential lens distortion;
- sensor crop or output resampling beyond the pinned catalog resolution;
- blur, focus, compression, lighting, motion, noise, weather, or analytics.

## 7. Static legend

The application-owned reference definition is immutable in V1:

| Minimum `px/face` | Maximum | Colour | Token |
|---:|---:|---|---|
| 2 | 3 | `#c7f9ff` | `face-density-2` |
| 3 | 5 | `#8fe7f2` | `face-density-3` |
| 5 | 7 | `#4cc9f0` | `face-density-5` |
| 7 | 10 | `#3a86ff` | `face-density-7` |
| 10 | 15 | `#2fb344` | `face-density-10` |
| 15 | 20 | `#8bc34a` | `face-density-15` |
| 20 | 30 | `#ffd43b` | `face-density-20` |
| 30 | 45 | `#ff922b` | `face-density-30` |
| 45 | 70 | `#f03e3e` | `face-density-45` |
| 70 | open | `#d633ff` | `face-density-70` |

Fill opacity is `0.58` on both standard and satellite maps. Thresholds are lower-inclusive and upper-exclusive except the open-ended highest band. Values below `2 px/face` are transparent.

The canonical definition contains the legend ID, metric, units, face width, thresholds, colours, tokens, and opacity. Backend and frontend must consume the same canonical reference data; they must not maintain independent handwritten engineering values.

## 8. Persisted model

Project schema `2.8.0` adds:

```json
{
  "camera_pixel_density_profile": {
    "lower_projection_height_m": 0.5,
    "upper_projection_height_m": 2.0,
    "measurement_height_mode": "midpoint",
    "maximum_visible_distance_m": 50.0,
    "legend_id": "face-density-0.16m-v1"
  },
  "camera_pixel_density": {
    "state": {
      "status": "not-calculated",
      "calculation_input_sha256": null,
      "message": null
    },
    "result": null
  }
}
```

Allowed state values are `not-calculated`, `current`, and `stale`. Controlled calculation errors are returned to the caller and do not replace stored state or result.

The result uses model version `camera-face-density-vector-1.0.0` and contains:

- calculation timestamp;
- projected CRS;
- canonical calculation-input SHA-256;
- complete profile snapshot, including derived midpoint and face width;
- ordered per-camera results;
- ordered overlap regions;
- warnings and assumptions;
- exact disclaimer.

Each per-camera result records exact fixture, template, camera, and lens revision provenance; resolution; FOV; height; absolute azimuth; tilt; validity; projection envelope; mutually exclusive bands; warnings; and assumptions.

Each band records threshold bounds, rank, display value, colour token, projected rings, WGS84 rings, and area. Empty bands are omitted. Each overlap region records its deterministic ID, sorted contributing footprint IDs, multiplicity, winning camera and band, projected rings, WGS84 rings, and area.

The exact disclaimer is:

> Geometric horizontal pixel density for a front-facing 0.16 m reference face using an ideal pinhole model; not detection, recognition, identification, analytics, occlusion, visibility, or compliance evidence.

## 9. Canonical geometry and deterministic ordering

- Projected coordinates round to 9 decimal places; WGS84 coordinates round to 10.
- Exterior rings are closed, counter-clockwise, and rotated to begin at the lexicographically smallest rounded vertex.
- Interior rings, if any, are closed, clockwise, and sorted by canonical coordinate sequence.
- Multipolygons are sorted by descending rounded area and then canonical coordinate sequence.
- Cameras are ordered by source sequence index, pole ID, and camera-slot ID.
- Bands are ordered by ascending rank.
- Contributing camera IDs are sorted lexicographically.
- Overlap regions are sorted by multiplicity, contributing ID tuple, winning band rank, and canonical geometry sequence.
- Areas round to 6 decimal places.
- Repeating the same calculation on identical inputs produces identical engineering geometry, ordering, and fingerprint. `calculated_at` is excluded from deterministic equality assertions.

## 10. Overlap calculation and rendering

Density bands are composited by maximum density, never addition or averaging.

1. Build mutually exclusive bands for every valid camera.
2. Overlay the contributing camera bands.
3. Partition shared geometry into regions with an identical sorted set of contributing camera footprint IDs.
4. Select the winner by highest exact density band. If contributors share the same winning rank, choose the lexicographically smallest footprint ID only as deterministic provenance; the displayed colour is unchanged.
5. Store multiplicity and all contributors.

The base map renders the winning density colour. Above it, overlap uses a dashed outline, sparse-dot treatment, and a `2×`, `3×`, or higher label. The overlay is presentation-only and never changes the band value.

Click inspection is read-only and reports:

- displayed band and `px/face` range;
- winning pole/camera-slot identity;
- every contributing pole/camera-slot identity;
- multiplicity;
- result freshness and disclaimer.

## 11. Safety limits

The following hard limits apply before persistence:

- enabled cameras: 200;
- overlap regions: 20,000;
- total persisted geometry vertices across projected and WGS84 representations: 250,000 coordinate positions per representation, counted consistently and documented in code;
- compact UTF-8 JSON size of the `camera_pixel_density.result` object: 25 MiB (`26,214,400` bytes).

The distance cap uses a canonical 128-sided polygon centered on the camera's projected optical origin. Vertex zero is due north and vertices proceed counter-clockwise in the project CRS.

If any limit is exceeded, the endpoint returns a controlled validation response, saves nothing, and preserves the previous project/result byte-for-byte. The service never drops cameras, bands, overlap regions, or vertices to fit a limit.

## 12. Fingerprint and freshness

The SHA-256 input is canonical compact JSON with sorted keys and finite values. It includes every engineering-significant input:

- model and geometry-contract versions;
- legend ID, thresholds, colours, opacity, and face width;
- profile values and derived midpoint;
- maximum-distance polygon convention;
- projected CRS;
- effective pole coordinates, activity, SMART assignment, and height;
- fixture model and mounting-template revision;
- fixture azimuth;
- slot ID, enabled state, relative azimuth, tilt, and origin offsets;
- camera ID/revision and horizontal/vertical resolution;
- lens ID/revision and horizontal/vertical FOV.

Presentation-only state is excluded: layer/legend visibility, popup state, selected feature, basemap, viewport, zoom, bearing, pitch, and panel position.

On a significant edit, fingerprint mismatch changes state to `stale` and hides the layer immediately. The result remains persisted for audit. A successful recalculation atomically replaces it and changes state to `current`. A failed recalculation preserves the existing stale or current result and state.

## 13. API lifecycle

The calculation operation is:

```text
POST /api/projects/{project_id}/camera-pixel-density/calculate
```

The request body is the complete candidate project, following the established lighting, Wi-Fi, and CAP calculation pattern. The path ID and payload ID must match. The backend:

1. validates and migrates the candidate payload;
2. resolves revision-pinned catalogs;
3. calculates in memory;
4. validates geometry, canonical ordering, safety limits, and serialized size;
5. applies the result to a deep copy;
6. saves once through the project store;
7. returns the saved project.

No save occurs before step 6. Validation and controlled geometry failures return `422`; project identity conflicts return `409`; missing projects return `404`. Unexpected server failures return the existing sanitized error response and must not modify the stored project.

The static legend is served from one application-owned reference definition through the existing reference/catalog delivery pattern. The calculation result references its immutable legend ID and carries its auditable profile snapshot.

## 14. Migration

Migration from every supported schema version through `2.7.0` to `2.8.0` must:

- preserve all existing keys and values, source bytes, coordinates, edits, histories, derived layers, unknown extension dictionaries, and report data;
- add the default profile only when absent;
- add `camera_pixel_density.state.status = "not-calculated"` and `result = null` only when absent;
- never derive or fabricate historical density geometry;
- be idempotent;
- reject invalid claimed `2.8.0` payloads rather than silently rewriting them.

Regenerate `schemas/project.schema.json` and `schemas/openapi.json` from code and require byte-freshness checks.

## 15. User interface

The Camera discipline contains:

- lower projection plane input;
- upper projection plane input;
- read-only derived AUTO measurement height;
- maximum visible distance input;
- status and validation summary;
- **Calculate camera density** primary action;
- density-layer visibility control;
- **Show colour legend** action.

After successful calculation, the density layer and legend open automatically. Users may hide either without affecting freshness or the fingerprint. Stale geometry is not rendered and the panel shows exactly:

> Stale — recalculate required

The legend shows colour and `px/face` values only. It contains no detection, recognition, identification, or compliance labels.

The MapLibre layer order is:

1. basemap;
2. per-camera/winning density fills;
3. band boundary lines where required for legibility;
4. sparse overlap dots and dashed overlap outlines;
5. overlap multiplicity labels;
6. existing pole/camera interaction layers and popup anchors.

The popup is closable and does not mutate project selection or engineering data.

## 16. Invalid cameras and warnings

An enabled camera contributes no colour when any required input is missing, non-finite, incompatible, stale, or unsupported. This includes missing height, camera revision, resolution, lens revision, FOV, unsupported legacy orientation overrides, non-zero origin offsets, unsupported geometry contract, or a ray/frustum that cannot create valid bounded midpoint geometry.

Warnings attach to the per-camera result and appear in the existing validation experience. One invalid camera does not suppress other valid cameras. A profile, CRS, global safety-limit, or serialization failure rejects the whole calculation.

Disabled camera slots are included as deterministic non-contributing per-camera entries with `enabled = false`, `valid = false`, empty geometry, and no missing-input warnings. They do not count toward the 200-enabled-camera limit and never create bands or overlap geometry.

## 17. Verification contract

### Deterministic backend cases

Tests must cover:

- the exact pinhole equation at the optical axis and off-axis points;
- all supplied pinned lens FOVs (`52° × 40°`, `69° × 54°`, `87° × 68°`) using IMX477 `4056 × 3040` resolution;
- lower `0.5 m`, upper `2.0 m`, and AUTO midpoint `1.25 m` semantics;
- threshold values immediately below, exactly at, and immediately above every boundary;
- every quadrant and azimuth wraparound;
- the fixed positive 35-degree downward tilt convention;
- 50 m cap vertex count, orientation, and canonical first vertex;
- mutually exclusive bands and exact union against the valid midpoint domain;
- one, two, and three-camera overlaps, winner selection, multiplicity, and contributor ordering;
- invalid-camera isolation;
- missing/geographic/non-metre CRS rejection;
- non-finite input rejection;
- exact limit boundaries and one-above failures for cameras, overlaps, vertices, and bytes;
- atomic preservation after every controlled failure;
- deterministic rerun equality;
- fingerprint inclusion/exclusion matrix;
- stale-result hiding and successful replacement;
- lossless, idempotent migration from every supported schema version;
- schema and OpenAPI byte freshness.

Reference-case expected values must be independently calculated in tests from fixed analytic inputs, not copied from service output. No test may claim exact VideoCAD parity without independently supplied and approved VideoCAD reference results.

### Frontend and rendered cases

Tests and production-browser QA must cover:

- initial not-calculated state;
- valid profile editing and validation;
- successful explicit calculation;
- automatic layer and legend opening;
- exact Option A colours, thresholds, units, and `0.58` opacity on standard and satellite basemaps;
- one camera for every supplied lens;
- `2×` and `3×` overlap styling and click inspection;
- winner and complete contributor list;
- invalid-camera warnings with valid cameras still rendered;
- transparent below-threshold/outside-envelope/beyond-cap areas;
- stale edit, immediate hiding, save/reopen, and recalculation;
- failed recalculation preserving the previous result;
- zero browser console errors;
- unchanged Phase 3 footprints and regressions across lighting, Wi-Fi, CAP, reports, source preservation, and existing-pole mode.

The supplied Miracle Mile workflow must retain the exact input SHA-256:

`2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`

## 18. Reporting and export compatibility

V1 does not add a new PDF, XLSX, presentation, KML, or KMZ density visualization. Existing Phase 7 generation must continue to succeed. The deterministic project JSON archive naturally includes the new profile, state, and derived result under schema `2.8.0`; existing reports must not mislabel it as professionally validated camera performance.

A future report visualization or specialized export requires separate authorization.

## 19. Non-goals

- Detection, observation, recognition, identification, LPR, people counting, or analytics thresholds.
- VideoCAD file compatibility or exact numerical parity.
- Lens-distortion correction without revision-pinned calibration evidence.
- Terrain, DEM, slope, occlusion, buildings, poles, trees, foliage, weather, refraction, blur, motion, focus, compression, or lighting-quality modeling.
- Density summation or averaging across cameras.
- Per-project or per-camera legend editing.
- Automatic camera/lens selection or inferred missing catalog data.
- Changing the accepted Phase 3 footprint result.
- New report visualizations or KML/KMZ density export.
- Pole creation, movement, optimization, redistribution, or deletion.
- Phase 8 or a new numbered phase.

## 20. Definition of Done for implementation readiness

Implementation may be handed to Independent QA only when:

- every approved rule above is implemented within the authorized file boundary;
- the work record and execution log identify the exact base and implementation commits;
- all deterministic backend, frontend, migration, schema, build, and rendered checks pass on the exact implementation commit;
- implementation-readiness verification passes on a clean worktree;
- source hashes and customer coordinates are unchanged;
- no required check is skipped or replaced by historical evidence;
- the handoff explicitly states that readiness is not acceptance and creates no phase seal.

Independent QA and a separate scoped master PASS remain required before BL-016 is accepted. Implementation, merge, push, and any later backlog item remain separately gated.
