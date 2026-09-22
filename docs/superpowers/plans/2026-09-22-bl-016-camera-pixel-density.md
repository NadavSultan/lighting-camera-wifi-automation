# BL-016 Camera Pixel-Density Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, persisted, backend-authoritative camera pixel-density vector map that reports horizontal pixels across a front-facing 0.16 m face and renders auditable density bands and overlaps in the existing Camera workflow.

**Architecture:** A dedicated Python/Shapely service resolves revision-pinned camera inputs, intersects the accepted pinhole frustum with the approved midpoint plane and distance cap, partitions the result into mutually exclusive density bands, and derives overlap provenance. Pydantic schema `2.8.0` persists the profile, freshness state, and canonical projected/WGS84 geometry; React/MapLibre requests calculation and renders the backend result without recalculating engineering values.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, PyProj, Shapely, React 19, TypeScript 5.9, MapLibre GL 5.7, Node test runner, Vinext.

**Spec:** `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md`

## Global Constraints

- Read `AGENTS.md`, all required startup files, the architecture, the engineering design, and this plan before changing implementation files.
- Existing-pole mode remains mandatory. Never create, move, optimize, redistribute, or delete customer poles.
- Preserve every `Input/` byte and all source coordinates exactly.
- Keep accepted Phase 3 `camera_geometry` unchanged; BL-016 uses separate `camera_pixel_density_profile` and `camera_pixel_density` fields.
- Project schema is `2.8.0`; software/API is `0.8.0`; migration is additive, lossless, and creates no historical result.
- Calculation uses the existing projected metre CRS and camera basis. WGS84 is display/interchange only.
- Horizontal density is `fx * 0.16 / forward_depth` at the AUTO midpoint plane; lens distortion is excluded.
- The result is VideoCAD-style horizontal pixels per object width, but the product must not claim VideoCAD file compatibility or exact numerical parity.
- Thresholds are `[2, 3, 5, 7, 10, 15, 20, 30, 45, 70] px/face`, lower-inclusive, classified from unrounded values with `1e-9 px/face` threshold snapping.
- Use the approved Option A colours and `0.58` fill opacity from the spec. Backend and frontend consume one canonical legend definition.
- Use a 128-sided maximum-distance polygon; default distance is `50.0 m`.
- Hard limits: 200 enabled cameras, 20,000 overlap regions, 250,000 projected vertices and 250,000 WGS84 vertices, and 25 MiB compact result JSON.
- Fail atomically. Never simplify, truncate, or partially save geometry to satisfy a limit.
- Stale geometry remains stored for audit but is hidden; only a successful explicit calculation creates a current visible layer.
- No detection, recognition, identification, analytics, occlusion, visibility, professional-validation, or compliance claim.
- No new report visualization or density KML/KMZ export in V1; existing report generation must remain compatible.
- Do not create Phase 8 or a phase seal. BL-016 uses a dated post-roadmap work record, Independent QA, and a scoped master gate.

## Review Focus

- **Threshold and numeric edge cases:** non-finite inputs, almost-equal thresholds, zero/negative forward depth, and near-horizontal rays must fail or classify deterministically rather than leak NaN geometry.
- **Geometry explosion:** fragmented multipolygons, holes, exact-at-limit results, and one-above each camera/overlap/vertex/byte cap must either persist completely or fail atomically.
- **Freshness races:** a saved project edited after calculation, a failed recalculation, and presentation-only changes must preserve the correct current/stale state without showing stale colour.
- **Untrusted display strings:** pole IDs, camera-slot IDs, and warnings shown in map popups must be inserted as text DOM nodes, never interpolated into `setHTML`.
- **Legacy/report compatibility:** every supported pre-`2.8.0` project and every Phase 7 report format must remain readable/generatable without fabricated density data or new report claims.

## Acceptance IDs

- `BL016-01` — additive, lossless, idempotent migration to project schema `2.8.0` and software/API `0.8.0`.
- `BL016-02` — finite, ordered project profile with correct `0.5 / 2.0 / 1.25 / 50.0` defaults.
- `BL016-03` — one immutable canonical Option A legend with exact thresholds, colours, units, face width, and opacity.
- `BL016-04` — correct ideal-pinhole horizontal `px/face` equation for every supplied lens.
- `BL016-05` — correct lower/upper envelope, midpoint domain, projected-metre calculation, and 128-sided distance cap.
- `BL016-06` — exact pinned fixture/template/camera/lens provenance and deterministic disabled-slot representation.
- `BL016-07` — invalid-camera isolation with explicit warnings and no invented inputs.
- `BL016-08` — mutually exclusive canonical bands, stable ordering/rounding, and repeat-run determinism.
- `BL016-09` — maximum-density overlap compositing, full contributor provenance, multiplicity, and deterministic winner tie-break.
- `BL016-10` — exact acceptance/rejection at all camera, overlap, vertex, and serialized-byte safety limits.
- `BL016-11` — complete engineering-input fingerprint with presentation-only exclusions.
- `BL016-12` — retained-but-hidden stale lifecycle and successful-current replacement.
- `BL016-13` — atomic calculate API with controlled identity/validation errors and byte-preserving failure.
- `BL016-14` — Camera-panel profile, status, explicit calculation action, and automatic current-layer/legend display.
- `BL016-15` — exact Option A MapLibre rendering on standard and satellite backgrounds with transparency outside valid colour.
- `BL016-16` — separate overlap dots/dashes/labels and safe read-only point inspection listing winner and all contributors.
- `BL016-17` — save, close, reopen, edit, failed-recalculate, and successful-recalculate persistence behavior.
- `BL016-18` — Phase 7 report compatibility without new density report/KMZ claims or visualization.
- `BL016-19` — unchanged Phase 3 geometry, prior workflows, source coordinates, and supplied-input SHA-256.
- `BL016-20` — complete deterministic and production-browser evidence, clean readiness PASS, and truthful Independent-QA handoff.

---

### Task 1: Activate the workflow record and prove the environment

**Files:**
- Create: `harness/phases/2026-09-22-bl-016-camera-pixel-density.md`
- Create: `harness/logs/2026-09-22-bl-016-camera-pixel-density.md`
- Modify: `GOALS.md`
- Modify: `PLANS.md`
- Modify: `OPERATIONS.md`
- Modify: `docs/current-status.md`

**Interfaces:**
- Consumes: approved architecture commit `5837f29b65c706ca9db3f2c2491f8234a5a19bde` plus this approved plan commit.
- Produces: one dated controlling work record, one append-only execution log, an exact base identity, an authorized file boundary, acceptance IDs `BL016-01` through `BL016-20`, and verified command entry points.

- [ ] **Step 1: Create and activate one durable goal**

Use the environment's real durable-goal mechanism. The objective must be:

```text
Implement BL-016 exactly as specified in docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md and stop only at clean implementation-readiness PASS or a proven blocker recorded under AGENTS.md.
```

Record the returned goal identity and active state in the work record. Plain prose containing `/goal` is not evidence.

- [ ] **Step 2: Create the work record from the repository template**

Copy the structure of `harness/templates/phase-work-record-template.md` into the dated work record and fill it with:

```markdown
Controlling spec: docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md
Scope: BL-016 / WA-09 only
Non-goals: spec section 19
Milestones: M0 environment; M1 schema/legend; M2 geometry; M3 camera bands; M4 overlaps/limits; M5 API/freshness; M6 reporting; M7 frontend workflow; M8 map/inspection; M9 final verification
Expected seals: none
```

Record `git rev-parse HEAD`, branch, upstream, `git status --short --branch`, and the complete starting diff. The base is the plan commit at execution start, not an assumed historical hash.

- [ ] **Step 3: Lock the file boundary**

Authorize only the files named by Tasks 2–10 plus generated schemas, execution-index documents, and BL-016 harness evidence. Explicitly exclude `Input/`, catalog revisions other than the new static legend, unrelated backlog documents, runtime project data, caches, dependencies, build output, `.superpowers/`, and existing accepted phase seals.

- [ ] **Step 4: Run the environment preflight sequentially**

Run from the repository root:

```powershell
git status --short --branch
git rev-parse HEAD
Test-Path .venv\Scripts\python.exe
.\.venv\Scripts\python.exe --version
node --version
corepack pnpm --version
Push-Location frontend
corepack pnpm install --frozen-lockfile
corepack pnpm run test
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm run build
Pop-Location
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\validate_engineering_data.py
Push-Location backend
..\.venv\Scripts\python.exe -m scripts.export_schema
Pop-Location
git diff --check
git diff --exit-code -- Input
```

Expected: every command exits `0`; the schema generator is byte-clean before implementation; the known Starlette/httpx and Vinext chunk advisories are recorded as warnings, not suppressed.

- [ ] **Step 5: Update the execution index and commit the activation record**

`GOALS.md`, `PLANS.md`, `OPERATIONS.md`, and `docs/current-status.md` must say BL-016 implementation is active but unaccepted, name the controlling spec/plan/work record, and state that later backlog work, merge, push, and seals remain gated.

```powershell
git add -- GOALS.md PLANS.md OPERATIONS.md docs/current-status.md harness/phases/2026-09-22-bl-016-camera-pixel-density.md harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "docs: activate BL-016 implementation"
```

### Task 2: Add schema `2.8.0`, the canonical legend, and lossless migration

**Files:**
- Create: `data/cameras/camera-pixel-density-legend.json`
- Create: `schemas/camera-pixel-density-legend.schema.json`
- Modify: `backend/app/models.py`
- Modify: `backend/app/main.py`
- Modify: `frontend/app/lib/types.ts`
- Modify: `frontend/package.json`
- Modify: `scripts/validate_engineering_data.py`
- Modify: `backend/tests/test_models.py`
- Create: `backend/tests/test_bl016_camera_pixel_density.py`
- Regenerate: `schemas/project.schema.json`
- Regenerate: `schemas/openapi.json`

**Interfaces:**
- Consumes: the exact profile, state, result, band, overlap, and legend contracts in spec sections 5–8.
- Produces: `CameraPixelDensityProfile`, `CameraPixelDensityState`, `CameraPixelDensityLayer`, `CameraPixelDensityResult`, `CameraPixelDensityCameraResult`, `CameraPixelDensityBand`, `CameraPixelDensityOverlapRegion`, and `PixelDensityLegendDefinition`; `Project.camera_pixel_density_profile`; `Project.camera_pixel_density`; `LayerState.camera_pixel_density`.

- [ ] **Step 1: Write migration and validation tests that fail on `2.7.0`**

Add tests with these concrete expectations:

```python
def test_bl016_migration_is_lossless_empty_and_idempotent():
    payload = legacy_project_payload("2.7.0")
    original_source = copy.deepcopy(payload["source"])
    migrated = migrate_project_payload(payload)
    assert migrated["schema_version"] == "2.8.0"
    assert migrated["software_version"] == "0.8.0"
    assert migrated["source"] == original_source
    assert migrated["camera_pixel_density_profile"] == {
        "lower_projection_height_m": 0.5,
        "upper_projection_height_m": 2.0,
        "measurement_height_mode": "midpoint",
        "maximum_visible_distance_m": 50.0,
        "legend_id": "face-density-0.16m-v1",
    }
    assert migrated["camera_pixel_density"] == {
        "state": {"status": "not-calculated", "calculation_input_sha256": None, "message": None},
        "result": None,
    }
    assert migrate_project_payload(copy.deepcopy(migrated)) == migrated
```

Parametrize the same preservation check over every supported version `1.0.0` through `2.7.0`. Add model tests rejecting non-finite heights, `lower >= upper`, non-positive maximum distance, invalid legend ID, malformed hashes, non-closed rings, negative areas, and unknown status values.

- [ ] **Step 2: Run the new model tests and confirm the expected failure**

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py backend/tests/test_models.py -q -p no:cacheprovider
```

Expected: failures show missing `2.8.0` models/migration and legend data, not unrelated baseline failures.

- [ ] **Step 3: Add the canonical legend JSON and schema**

The JSON must contain exactly:

```json
{
  "id": "face-density-0.16m-v1",
  "metric": "horizontal-pixels-per-object",
  "display_units": "px/face",
  "object_width_m": 0.16,
  "fill_opacity": 0.58,
  "thresholds": [
    {"minimum": 2, "maximum": 3, "colour": "#c7f9ff", "token": "face-density-2"},
    {"minimum": 3, "maximum": 5, "colour": "#8fe7f2", "token": "face-density-3"},
    {"minimum": 5, "maximum": 7, "colour": "#4cc9f0", "token": "face-density-5"},
    {"minimum": 7, "maximum": 10, "colour": "#3a86ff", "token": "face-density-7"},
    {"minimum": 10, "maximum": 15, "colour": "#2fb344", "token": "face-density-10"},
    {"minimum": 15, "maximum": 20, "colour": "#8bc34a", "token": "face-density-15"},
    {"minimum": 20, "maximum": 30, "colour": "#ffd43b", "token": "face-density-20"},
    {"minimum": 30, "maximum": 45, "colour": "#ff922b", "token": "face-density-30"},
    {"minimum": 45, "maximum": 70, "colour": "#f03e3e", "token": "face-density-45"},
    {"minimum": 70, "maximum": null, "colour": "#d633ff", "token": "face-density-70"}
  ],
  "editable": false
}
```

The JSON Schema must require exactly those field types, reject extra properties, constrain hex colours with `^#[0-9a-f]{6}$`, and permit `maximum: null` only for the final ordered row. Extend `validate_engineering_data.py` to validate the file and assert increasing contiguous thresholds and the exact approved palette/opacity.

- [ ] **Step 4: Implement strict Pydantic models and version changes**

Add the exact named classes to `backend/app/models.py`. Use finite-number validators and these state types:

```python
CameraPixelDensityStatus = Literal["not-calculated", "current", "stale"]

class CameraPixelDensityProfile(StrictModel):
    lower_projection_height_m: float = 0.5
    upper_projection_height_m: float = 2.0
    measurement_height_mode: Literal["midpoint"] = "midpoint"
    maximum_visible_distance_m: float = 50.0
    legend_id: Literal["face-density-0.16m-v1"] = "face-density-0.16m-v1"

class CameraPixelDensityState(StrictModel):
    status: CameraPixelDensityStatus = "not-calculated"
    calculation_input_sha256: Annotated[str | None, Field(pattern=r"^[0-9a-f]{64}$")] = None
    message: str | None = None
```

Set `SCHEMA_VERSION = "2.8.0"`, `SOFTWARE_VERSION = "0.8.0"`, update every literal version field, add `2.7.0` to the migration source set, add the new defaults only when absent, and add `camera_pixel_density: bool = False` to `LayerState`. Update `frontend/package.json` version and mirror every new model in `frontend/app/lib/types.ts` without using `any`.

- [ ] **Step 5: Expose the canonical legend through one read-only endpoint**

Add:

```python
@app.get("/api/reference/camera-pixel-density-legend", response_model=PixelDensityLegendDefinition)
def get_camera_pixel_density_legend() -> PixelDensityLegendDefinition:
    return load_camera_pixel_density_legend()
```

The loader reads the versioned repository JSON, validates it once through the Pydantic model, and returns a deep copy. Do not duplicate thresholds or colours in route code.

- [ ] **Step 6: Run migration, legend, validator, and schema checks**

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py backend/tests/test_models.py backend/tests/test_engineering_data.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\validate_engineering_data.py
Push-Location backend
..\.venv\Scripts\python.exe -m scripts.export_schema
Pop-Location
git diff --check
```

Expected: all selected tests pass; validator includes the new legend; generated schemas contain `2.8.0`, `0.8.0`, new models, and the read-only legend endpoint.

- [ ] **Step 7: Commit the schema and canonical legend**

```powershell
git add -- data/cameras/camera-pixel-density-legend.json schemas/camera-pixel-density-legend.schema.json backend/app/models.py backend/app/main.py frontend/app/lib/types.ts frontend/package.json scripts/validate_engineering_data.py backend/tests/test_models.py backend/tests/test_bl016_camera_pixel_density.py schemas/project.schema.json schemas/openapi.json harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "feat: add BL-016 schema and density legend"
```

### Task 3: Implement deterministic camera-plane geometry and band primitives

**Files:**
- Create: `backend/app/services/camera_pixel_density.py`
- Modify: `backend/tests/test_bl016_camera_pixel_density.py`

**Interfaces:**
- Consumes: existing camera basis conventions and `PixelDensityLegendDefinition`.
- Produces: `camera_basis()`, `camera_coordinates()`, `horizontal_density_px_per_face()`, `project_frustum_plane()`, `distance_cap_polygon()`, `density_band_index()`, `clip_midpoint_density_bands()`, and canonical polygon/ring helpers.

- [ ] **Step 1: Add failing analytic equation tests**

Use fixed IMX477 width `4056`, object width `0.16`, and forward depth `10.0 m`. Assert:

```python
@pytest.mark.parametrize(("horizontal_fov_deg", "expected"), [
    (52.0, 66.528259051565),
    (69.0, 47.212132962364),
    (87.0, 34.193057505117),
])
def test_bl016_reference_lens_density(horizontal_fov_deg, expected):
    assert horizontal_density_px_per_face(4056, horizontal_fov_deg, 10.0) == pytest.approx(expected, abs=1e-12)
```

Add tests for camera coordinates at azimuths `0/90/180/270/360`, positive 35-degree downward tilt, front/behind points, non-finite inputs, `z_camera <= 1e-9`, and invalid FOV/resolution.

- [ ] **Step 2: Add failing threshold-boundary tests**

For every threshold `[2,3,5,7,10,15,20,30,45,70]`, assert immediately below, within `1e-9`, exactly at, and immediately above. Exact/within-tolerance values must select the threshold band; `1.999999` must be transparent; `70` and above must select rank 10.

- [ ] **Step 3: Add failing plane and 128-gon tests**

Assert default midpoint `1.25`, lower/upper cross sections, valid closed CCW rings, 129 stored cap coordinates including closure, due-north first vertex, 50 m radius within `1e-9 m`, and invalid/upward/horizontal ray failures. Add a regression where the widest supplied lens remains bounded at the 50 m cap.

- [ ] **Step 4: Implement the minimal geometry primitives**

Use these constants and signatures:

```python
PIXEL_DENSITY_MODEL_VERSION = "camera-face-density-vector-1.0.0"
FACE_WIDTH_M = 0.16
FORWARD_DEPTH_TOLERANCE_M = 1e-9
THRESHOLD_SNAP_TOLERANCE = 1e-9
DISTANCE_CAP_SIDES = 128
PROJECTED_DIGITS = 9
WGS84_DIGITS = 10
AREA_DIGITS = 6

def horizontal_density_px_per_face(width_px: int, horizontal_fov_deg: float, forward_depth_m: float) -> float:
    if width_px <= 0 or not math.isfinite(horizontal_fov_deg) or not 0 < horizontal_fov_deg < 180:
        raise ValueError("Camera resolution and horizontal FOV must be finite and positive.")
    if not math.isfinite(forward_depth_m) or forward_depth_m <= FORWARD_DEPTH_TOLERANCE_M:
        raise ValueError("Camera-space forward depth must be greater than 1e-9 m.")
    focal_length_px = width_px / (2 * math.tan(math.radians(horizontal_fov_deg) / 2))
    return focal_length_px * FACE_WIDTH_M / forward_depth_m

def density_band_index(value: float, thresholds: Sequence[float]) -> int | None:
    if not math.isfinite(value):
        raise ValueError("Pixel density must be finite.")
    snapped = next((threshold for threshold in thresholds if abs(value - threshold) <= THRESHOLD_SNAP_TOLERANCE), value)
    eligible = [index for index, threshold in enumerate(thresholds) if snapped >= threshold]
    return eligible[-1] if eligible else None

def distance_cap_polygon(origin_x_m: float, origin_y_m: float, radius_m: float) -> Polygon:
    if not all(math.isfinite(value) for value in (origin_x_m, origin_y_m, radius_m)) or radius_m <= 0:
        raise ValueError("Maximum visible distance must be finite and positive.")
    vertices = [
        (
            origin_x_m + radius_m * math.sin(2 * math.pi * index / DISTANCE_CAP_SIDES),
            origin_y_m + radius_m * math.cos(2 * math.pi * index / DISTANCE_CAP_SIDES),
        )
        for index in range(DISTANCE_CAP_SIDES)
    ]
    return Polygon(canonical_ring(vertices, digits=PROJECTED_DIGITS))
```

Reuse or move the accepted canonical-ring behavior without changing Phase 3 outputs. Use Shapely intersections only after validating all numeric inputs. Normalize polygons after every overlay operation and reject non-polygonal/degenerate output rather than persisting repair guesses.

- [ ] **Step 5: Implement midpoint domains and depth-slab band clipping**

At the measurement plane, `z_camera` is an affine function of projected `X/Y`. Convert density thresholds into forward-depth boundaries `depth = fx * 0.16 / threshold`, clip the convex midpoint domain by those depth half-planes, then intersect with the cap. Each band must be mutually exclusive under the lower-inclusive classification policy.

Expose:

```python
def clip_midpoint_density_bands(
    domain: Polygon,
    *,
    origin_xyz_m: tuple[float, float, float],
    forward: tuple[float, float, float],
    measurement_height_m: float,
    focal_length_px: float,
    legend: PixelDensityLegendDefinition,
) -> list[BandGeometry]:
    result: list[BandGeometry] = []
    density_scale = focal_length_px * FACE_WIDTH_M
    for rank, threshold in enumerate(legend.thresholds, start=1):
        minimum_depth = 0.0 if threshold.maximum is None else density_scale / threshold.maximum
        maximum_depth = density_scale / threshold.minimum
        geometry = clip_polygon_to_depth_interval(
            domain,
            origin_xyz_m=origin_xyz_m,
            forward=forward,
            plane_height_m=measurement_height_m,
            minimum_depth_m=minimum_depth,
            maximum_depth_m=maximum_depth,
        )
        if not geometry.is_empty:
            result.append(BandGeometry(rank=rank, threshold=threshold, geometry=canonical_polygonal(geometry)))
    return result
```

- [ ] **Step 6: Run focused geometry tests**

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py -q -p no:cacheprovider -k "reference_lens or threshold or camera_coordinates or midpoint or cap or band"
```

Expected: all focused analytic tests pass with no warnings or nondeterministic ordering.

- [ ] **Step 7: Commit geometry primitives**

```powershell
git add -- backend/app/services/camera_pixel_density.py backend/tests/test_bl016_camera_pixel_density.py harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "feat: calculate deterministic camera density bands"
```

### Task 4: Resolve pinned cameras, calculate per-camera results, and fingerprint inputs

**Files:**
- Modify: `backend/app/services/camera_pixel_density.py`
- Modify: `backend/tests/test_bl016_camera_pixel_density.py`

**Interfaces:**
- Consumes: project, fixture catalog, camera catalog, legend, Task 3 geometry primitives.
- Produces: `camera_pixel_density_input_sha256(project, fixtures, cameras, legend)`, `calculate_camera_pixel_density(project, fixtures, cameras, legend)`, and ordered `CameraPixelDensityCameraResult` values.

- [ ] **Step 1: Add failing pinned-input and disabled-slot tests**

Build fixture/camera/lens test catalogs with current and historical revisions. Assert the service uses the exact pinned revision rather than the current revision. Assert a disabled slot produces one entry with `enabled=False`, `valid=False`, empty geometry, no missing-input warnings, and does not count toward the camera cap.

- [ ] **Step 2: Add failing invalid-camera isolation tests**

Parametrize one invalid slot for each condition: missing height, camera, camera revision, resolution, lens, lens revision, H/V FOV, incompatible lens, non-zero origin offsets, legacy orientation override, unsupported geometry contract, and degenerate ray. Pair it with one valid camera and assert the valid camera still produces bands while the invalid entry produces explicit warnings and no geometry.

- [ ] **Step 3: Add failing fingerprint inclusion/exclusion tests**

Assert the digest changes independently for every spec section 12 engineering input. Assert it does not change for layer visibility, legend open state, selection, basemap, viewport, panel position, notes, or calculation timestamp. Reject NaN/Infinity during canonical JSON creation.

- [ ] **Step 4: Implement revision resolution and per-camera calculation**

Follow the accepted `camera_geometry.calculate_camera_geometry` resolution order, but do not call or mutate that layer. Use `camera_absolute_azimuth`, fixed-zero-origin validation, and project transformers. Populate full provenance, profile snapshot, projection envelope, bands, warnings, assumptions, and disclaimer.

The top-level function signature is:

```python
def calculate_camera_pixel_density(
    project: Project,
    fixtures: FixtureModelCatalog,
    cameras: CameraEquipmentCatalog,
    legend: PixelDensityLegendDefinition,
    *,
    calculated_at: datetime | None = None,
) -> CameraPixelDensityResult:
    resolved = resolve_camera_pixel_density_inputs(project, fixtures, cameras)
    enabled_count = sum(item.enabled for item in resolved)
    if enabled_count > MAX_ENABLED_CAMERAS:
        raise ValueError("Camera pixel-density calculation exceeds the 200-enabled-camera safety limit.")
    camera_results = [calculate_one_camera_density(project, item, legend) for item in resolved]
    overlaps = calculate_density_overlaps(camera_results)
    result = CameraPixelDensityResult(
        calculated_at=calculated_at or utc_now(),
        projected_crs=project.projected_crs,
        calculation_input_sha256=camera_pixel_density_input_sha256(project, fixtures, cameras, legend),
        profile_snapshot=profile_snapshot(project.camera_pixel_density_profile, legend),
        camera_results=camera_results,
        overlap_regions=overlaps,
        warnings=aggregate_camera_warnings(camera_results),
        assumptions=PIXEL_DENSITY_ASSUMPTIONS,
    )
    validate_camera_pixel_density_result_limits(result)
    return result
```

Use `calculated_at` injection only for deterministic tests. It is excluded from the fingerprint.

- [ ] **Step 5: Enforce the 200-enabled-camera boundary**

Add exact tests for 200 accepted and 201 rejected before geometry allocation. Error copy:

```text
Camera pixel-density calculation exceeds the 200-enabled-camera safety limit.
```

- [ ] **Step 6: Run focused service tests**

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py -q -p no:cacheprovider -k "pinned or disabled or invalid_camera or fingerprint or camera_limit or per_camera"
```

- [ ] **Step 7: Commit per-camera calculation**

```powershell
git add -- backend/app/services/camera_pixel_density.py backend/tests/test_bl016_camera_pixel_density.py harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "feat: resolve BL-016 camera inputs and provenance"
```

### Task 5: Partition overlaps and enforce geometry/result limits

**Files:**
- Modify: `backend/app/services/camera_pixel_density.py`
- Modify: `backend/tests/test_bl016_camera_pixel_density.py`

**Interfaces:**
- Consumes: ordered valid per-camera bands.
- Produces: deterministic `CameraPixelDensityOverlapRegion` values, `count_persisted_vertices()`, and `validate_camera_pixel_density_result_limits()`.

- [ ] **Step 1: Add failing two- and three-camera overlap tests**

Create analytic rectangles with known intersections. Assert:

```python
assert region.camera_footprint_ids == ["pole-a/camera-1", "pole-b/camera-1"]
assert region.multiplicity == 2
assert region.winning_band_id == "px-face-30"
assert region.winning_camera_footprint_id == "pole-a/camera-1"
```

For equal winning ranks, assert lexicographically smallest footprint ID wins provenance while colour remains identical. For three cameras, assert one `3×` region plus correctly partitioned `2×` regions without double-counted area.

- [ ] **Step 2: Add failing multipolygon, hole, and ordering tests**

Use fragmented Shapely fixtures that yield multiple polygons and holes. Assert canonical ring winding, part ordering, contributor ordering, deterministic IDs, and exact repeat-run serialized equality excluding `calculated_at`.

- [ ] **Step 3: Add exact-at-limit and one-above safety tests**

Test 20,000/20,001 overlap regions, 250,000/250,001 projected coordinates, 250,000/250,001 WGS84 coordinates, and compact JSON byte sizes `26,214,400`/`26,214,401`. Monkeypatch generated collections for boundary tests; do not allocate pathological real overlay inputs merely to reach byte limits.

- [ ] **Step 4: Implement deterministic overlap partitioning**

Use an STRtree to find candidate intersections. Partition geometry so each stored region has one exact contributor set. Determine the winning band by highest rank, then deterministic footprint-ID tie-break. Generate IDs as SHA-256 of canonical contributor IDs, winner, rank, and projected geometry; use a stable prefix such as `density-overlap-` plus the first 24 hex characters.

- [ ] **Step 5: Implement and call all safety-limit validators before return**

The compact size check must use:

```python
payload = result.model_dump(mode="json")
size_bytes = len(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
```

Raise controlled `ValueError` messages naming the exceeded limit. Never mutate, drop, simplify, or truncate the candidate result.

- [ ] **Step 6: Run overlap and limit tests**

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py -q -p no:cacheprovider -k "overlap or multipolygon or hole or vertex_limit or byte_limit"
```

- [ ] **Step 7: Commit overlap and safety work**

```powershell
git add -- backend/app/services/camera_pixel_density.py backend/tests/test_bl016_camera_pixel_density.py harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "feat: add BL-016 overlap provenance and limits"
```

### Task 6: Add atomic API calculation, freshness, and save/reopen behavior

**Files:**
- Modify: `backend/app/services/camera_pixel_density.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/services/store.py` only if the established atomic-save hook requires it
- Modify: `backend/tests/test_bl016_camera_pixel_density.py`
- Modify: `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `calculate_camera_pixel_density()` and input fingerprint.
- Produces: `apply_camera_pixel_density_result()`, `invalidate_stale_camera_pixel_density()`, and `POST /api/projects/{project_id}/camera-pixel-density/calculate`.

- [ ] **Step 1: Add failing API success and identity tests**

Create an isolated `ProjectStore`, save a valid project, POST its full JSON, and assert response/state/result persistence. Assert mismatched path/payload IDs return `409`, absent ID returns `404`, and a successful response sets:

```python
assert body["camera_pixel_density"]["state"]["status"] == "current"
assert body["camera_pixel_density"]["state"]["calculation_input_sha256"] == body["camera_pixel_density"]["result"]["calculation_input_sha256"]
assert body["layer_state"]["camera_pixel_density"] is True
```

- [ ] **Step 2: Add failing atomic-preservation tests**

For invalid profile, CRS, geometry, 201 cameras, overlap/vertex/byte limit, and forced unexpected exception, hash the stored `project.json` before and after the request. Controlled failures return `422`; unexpected failures use the existing sanitized server behavior. Every after-hash must equal the before-hash.

- [ ] **Step 3: Add failing stale/current transition tests**

Apply a result, then independently change each significant input and call invalidation. Assert state becomes `stale`, result remains byte-equal, and layer visibility becomes false. Change notes, basemap/layer visibility, selection, and other presentation state and assert state stays `current`. A failed recalculation must preserve the prior state/result. A successful recalculation replaces it and returns `current`.

- [ ] **Step 4: Implement apply and invalidation functions**

```python
def apply_camera_pixel_density_result(project: Project, result: CameraPixelDensityResult) -> Project:
    updated = project.model_copy(deep=True)
    updated.camera_pixel_density.result = result
    updated.camera_pixel_density.state = CameraPixelDensityState(
        status="current",
        calculation_input_sha256=result.calculation_input_sha256,
        message=None,
    )
    updated.layer_state.camera_pixel_density = True
    updated.updated_at = utc_now()
    return updated
```

`invalidate_stale_camera_pixel_density()` recomputes the authoritative fingerprint with pinned catalogs. On mismatch it retains `result`, sets `status="stale"`, uses message `Stale — recalculate required`, and disables the layer.

- [ ] **Step 5: Implement the atomic route**

Follow the established lighting/Wi-Fi/CAP route pattern, but calculate and validate entirely before `projects.save(updated)`. Validate project configuration first. Convert known `ValueError`/Pydantic validation failures to `422` without saving. Do not alter `camera_geometry`.

- [ ] **Step 6: Wire backend invalidation into project save paths**

Before saving candidate project edits through PUT, bulk configuration, catalog-revision adoption, or any route that can change significant inputs, run authoritative invalidation. Do not invalidate on presentation-only changes. Tests must exercise ordinary save, bulk configuration, and explicit calculation paths.

- [ ] **Step 7: Run API and full backend tests**

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py backend/tests/test_api.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

- [ ] **Step 8: Commit API and freshness behavior**

```powershell
git add -- backend/app/services/camera_pixel_density.py backend/app/main.py backend/app/services/store.py backend/tests/test_bl016_camera_pixel_density.py backend/tests/test_api.py harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "feat: persist BL-016 calculations atomically"
```

If `backend/app/services/store.py` is unchanged, omit it from `git add`; do not create a no-op edit.

### Task 7: Preserve Phase 7 reporting and generated contracts

**Files:**
- Modify: `backend/app/services/reporting.py` only where version/current-project serialization requires it
- Modify: `backend/tests/test_phase7_reporting.py`
- Modify: `backend/tests/test_engineering_data.py`
- Regenerate: `schemas/project.schema.json`
- Regenerate: `schemas/openapi.json`

**Interfaces:**
- Consumes: schema/software version constants and persisted project JSON.
- Produces: unchanged report formats that tolerate and archive schema `2.8.0` without adding a density PDF/XLSX/KMZ/presentation visualization.

- [ ] **Step 1: Update version assertions and add failing compatibility tests**

Replace hardcoded historical current-version assertions with `2.8.0`/`0.8.0` while preserving legacy migration fixtures. Add a calculated BL-016 project and assert:

```python
archive_project = json.loads(members["project/project.json"])
assert archive_project["camera_pixel_density"]["result"]["model_version"] == "camera-face-density-vector-1.0.0"
assert b"face-density" not in members["engineering/derived-layers.kml"]
assert "camera pixel density" not in extract_pdf_text(members["summary/project-summary.pdf"]).lower()
```

Also assert every prior report member still validates, the report disclaimer gains no recognition/performance claim, and stale density does not alter existing camera inclusion disposition.

- [ ] **Step 2: Run report tests and inspect failures before editing service code**

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_phase7_reporting.py backend/tests/test_engineering_data.py -q -p no:cacheprovider
```

Change `reporting.py` only for actual schema/version compatibility. Do not add density visual output.

- [ ] **Step 3: Regenerate and verify contracts**

```powershell
Push-Location backend
..\.venv\Scripts\python.exe -m scripts.export_schema
Pop-Location
.\.venv\Scripts\python.exe scripts\validate_engineering_data.py
.\.venv\Scripts\python.exe -m pytest backend/tests/test_phase7_reporting.py backend/tests/test_engineering_data.py -q -p no:cacheprovider
git diff --check
```

- [ ] **Step 4: Commit report/schema compatibility**

```powershell
git add -- backend/app/services/reporting.py backend/tests/test_phase7_reporting.py backend/tests/test_engineering_data.py schemas/project.schema.json schemas/openapi.json harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "test: preserve reports with BL-016 schema"
```

Omit `reporting.py` if tests prove no service change is required.

### Task 8: Add frontend types, API, local freshness, and Camera-panel workflow

**Files:**
- Create: `frontend/app/lib/camera-pixel-density-view.mjs`
- Create: `frontend/app/lib/camera-pixel-density-view.d.mts`
- Create: `frontend/tests/camera-pixel-density-view.test.mjs`
- Create: `frontend/app/components/CameraPixelDensityPanel.tsx`
- Create: `frontend/app/components/CameraPixelDensityLegend.tsx`
- Modify: `frontend/app/lib/api.ts`
- Modify: `frontend/app/lib/types.ts`
- Modify: `frontend/app/components/EngineeringWorkspace.tsx`
- Modify: `frontend/app/globals.css`
- Modify: `frontend/tests/rendered-html.test.mjs`
- Modify: `frontend/tests/left-panel-layout.test.mjs`

**Interfaces:**
- Consumes: `Project.camera_pixel_density_profile`, layer state/result, and the canonical legend endpoint.
- Produces: `getCameraPixelDensityLegend()`, `calculateCameraPixelDensity(project)`, `cameraPixelDensityView(project)`, `invalidateCameraPixelDensityIfSignificant(previous, next)`, profile controls, calculation action, status copy, and session-only legend visibility.

- [ ] **Step 1: Add failing pure-view and local-invalidation tests**

Cover `not-calculated`, `current`, `stale`, current-with-hidden-layer, invalid/missing result, and stale-with-retained-result. Assert exact stale copy. Add a field matrix proving local invalidation for profile, height, azimuth, fixture/template/camera/lens revisions, enabled state, relative azimuth, tilt, offsets, resolution/FOV snapshots where present; prove no invalidation for notes, basemap, layer toggles, popup, selection, and panel state.

- [ ] **Step 2: Add failing API and rendered-source assertions**

Assert `api.ts` posts the full project to `/camera-pixel-density/calculate`, fetches the canonical legend, and parses backend errors through the existing safe `api()` helper. Rendered/source tests must require the exact button label, profile labels/defaults, status copy, disclaimer, and no detection/recognition labels in the legend.

- [ ] **Step 3: Implement the pure helper and declarations**

Expose:

```ts
export type CameraPixelDensityView = {
  status: "not-calculated" | "current" | "stale";
  canCalculate: boolean;
  layerAvailable: boolean;
  message: string;
};

export function cameraPixelDensityView(project: Project | null): CameraPixelDensityView;
export function invalidateCameraPixelDensityIfSignificant(previous: Project, next: Project): Project;
```

The helper may conservatively mark stale only for the exact approved significant fields; it must never delete the retained result. Backend invalidation remains authoritative.

- [ ] **Step 4: Implement API functions and panel components**

`CameraPixelDensityPanel` owns no engineering calculation. It receives project/profile/state/legend, busy state, and callbacks. It validates finite UI inputs before mutation, shows derived midpoint read-only, disables calculation when the profile is invalid or another request is busy, and displays warnings and the exact disclaimer.

`CameraPixelDensityLegend` renders all ten immutable rows from the fetched legend and uses `aria-label="Camera pixel-density colour legend"`. It renders only colour and `px/face` ranges.

- [ ] **Step 5: Integrate into `EngineeringWorkspace`**

Add session state `densityLegendOpen`. On successful calculation:

```ts
const calculated = await calculateCameraPixelDensity(project);
setProject(calculated);
setDensityLegendOpen(true);
setStatus("Calculated camera pixel-density map");
```

Use local invalidation in `mutateProject` before setting edited state. Add the `camera_pixel_density` layer row to the Camera discipline, disabled unless a current result exists. A user layer toggle must not alter the fingerprint.

- [ ] **Step 6: Run frontend focused tests, typecheck, and lint**

```powershell
Push-Location frontend
node --test tests/camera-pixel-density-view.test.mjs tests/rendered-html.test.mjs tests/left-panel-layout.test.mjs
corepack pnpm run typecheck
corepack pnpm run lint
Pop-Location
```

- [ ] **Step 7: Commit the Camera-panel workflow**

```powershell
git add -- frontend/app/lib/camera-pixel-density-view.mjs frontend/app/lib/camera-pixel-density-view.d.mts frontend/tests/camera-pixel-density-view.test.mjs frontend/app/components/CameraPixelDensityPanel.tsx frontend/app/components/CameraPixelDensityLegend.tsx frontend/app/lib/api.ts frontend/app/lib/types.ts frontend/app/components/EngineeringWorkspace.tsx frontend/app/globals.css frontend/tests/rendered-html.test.mjs frontend/tests/left-panel-layout.test.mjs harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "feat: add BL-016 camera workflow"
```

### Task 9: Render density bands, overlap treatment, labels, and safe inspection

**Files:**
- Create: `frontend/app/lib/camera-pixel-density-map.mjs`
- Create: `frontend/app/lib/camera-pixel-density-map.d.mts`
- Create: `frontend/tests/camera-pixel-density-map.test.mjs`
- Create: `frontend/app/components/CameraPixelDensityLabels.tsx`
- Modify: `frontend/app/components/EngineeringMap.tsx`
- Modify: `frontend/app/globals.css`
- Modify: `frontend/tests/rendered-html.test.mjs`

**Interfaces:**
- Consumes: current backend-produced WGS84 rings, band ranks/tokens, overlap regions, canonical legend, and `LayerState.camera_pixel_density`.
- Produces: density-band GeoJSON, overlap polygon/centroid GeoJSON, deterministic layer definitions, visible `2×/3×` canvas labels, and safe read-only popup DOM.

- [ ] **Step 1: Add failing GeoJSON and visibility tests**

Assert stale/not-calculated results produce empty feature collections even if the layer flag is true. Current results produce one feature per polygon part with `footprint_id`, `band_id`, `rank`, `minimum`, `maximum`, and `colour_token`. Verify holes remain holes and multipolygons are not flattened into overlapping independent exteriors.

- [ ] **Step 2: Add failing winner/inspection tests**

Given overlapping features, assert the helper selects highest rank, resolves the stored winner, and lists every sorted contributor. Include pole/slot strings containing `<script>`, quotes, ampersands, and bidi characters. The popup builder must return text data or DOM nodes and tests must prove `innerHTML` is never built from those strings.

- [ ] **Step 3: Add failing layer-style tests**

Assert ten band layers render in ascending rank so the highest density wins visually; each colour comes from the fetched canonical legend and fill opacity is exactly `0.58`. Assert overlap adds a dashed line and generated sparse-dot pattern above fills. Assert standard/satellite background selection does not change engineering colours.

- [ ] **Step 4: Implement map helpers**

Expose:

```ts
export function densityBandFeatures(project: Project): FeatureCollection<Polygon | MultiPolygon>;
export function densityOverlapFeatures(project: Project): FeatureCollection<Polygon | MultiPolygon>;
export function densityOverlapLabelPoints(project: Project): DensityOverlapLabelPoint[];
export function densityInspectionAt(features: MapGeoJSONFeature[]): DensityInspection | null;
```

Return empty collections unless state is `current`, result fingerprint matches state fingerprint, and the persisted layer flag is true.

- [ ] **Step 5: Add MapLibre sources/layers and generated dot pattern**

In `EngineeringMap`, add sources before layers. Generate an 8×8 transparent RGBA image with one neutral high-contrast dot via `map.addImage`; do not add remote assets or dependencies. Add band fills per rank, optional subtle boundaries, overlap dot fill, dashed overlap outline, and pointer handlers.

Use `Popup.setDOMContent(element)`. Construct the element with `document.createElement` and assign all project-derived values with `textContent`.

- [ ] **Step 6: Implement multiplicity labels without a glyph dependency**

`CameraPixelDensityLabels` follows the existing `LightingPointLabels` canvas/frame-scheduler pattern. Draw only labels whose projected centroids are on screen, with white text and a dark halo. Cancel animation frames and remove map/window listeners on unmount. Labels are presentation-only.

- [ ] **Step 7: Run focused and full frontend verification**

```powershell
Push-Location frontend
node --test tests/camera-pixel-density-map.test.mjs tests/camera-pixel-density-view.test.mjs tests/rendered-html.test.mjs
corepack pnpm run test
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm run build
Pop-Location
```

- [ ] **Step 8: Commit map rendering and inspection**

```powershell
git add -- frontend/app/lib/camera-pixel-density-map.mjs frontend/app/lib/camera-pixel-density-map.d.mts frontend/tests/camera-pixel-density-map.test.mjs frontend/app/components/CameraPixelDensityLabels.tsx frontend/app/components/EngineeringMap.tsx frontend/app/globals.css frontend/tests/rendered-html.test.mjs harness/logs/2026-09-22-bl-016-camera-pixel-density.md
git diff --cached --check
git commit -m "feat: render BL-016 density and overlaps"
```

### Task 10: Complete end-to-end verification, rendered evidence, and readiness handoff

**Files:**
- Create: `harness/verify/run_bl016_camera_pixel_density_live.py`
- Create: `harness/verify/2026-09-22-bl-016-camera-pixel-density-live.json`
- Create: `harness/verify/2026-09-22-bl-016-camera-pixel-density-verification.md`
- Create: `harness/verify/2026-09-22-bl-016-camera-pixel-density-readiness.json`
- Create: `harness/verify/2026-09-22-bl-016-camera-pixel-density-independent-qa-handoff.md`
- Modify: `harness/logs/2026-09-22-bl-016-camera-pixel-density.md`
- Modify: `GOALS.md`
- Modify: `PLANS.md`
- Modify: `OPERATIONS.md`
- Modify: `docs/current-status.md`
- Modify: `docs/post-roadmap-backlog.md`

**Interfaces:**
- Consumes: the complete BL-016 implementation and all acceptance IDs.
- Produces: reproducible deterministic verification, isolated production-browser evidence, a clean implementation commit, a passing readiness manifest, and an Independent-QA handoff. It does not create acceptance or a seal.

- [ ] **Step 1: Add the isolated live verification runner**

The runner must use a fresh temporary `LCWA_DATA_DIR`, isolated FastAPI port `8070`, isolated production Vinext port `3070`, and the supplied Miracle Mile KML. It records exact HEAD, working-tree status, server identities, API responses, browser console/page errors, screenshots, and structured assertions to JSON. It must never use runtime project data from the normal store.

- [ ] **Step 2: Exercise the complete rendered workflow**

The live script or supervised browser session must prove:

1. Import returns 74 source poles, `existing-poles`, `EPSG:32617`, and the exact source SHA-256.
2. A valid SMART fixture with each of the three supplied lenses calculates expected current density geometry.
3. Default profile displays `0.5 / 2.0 / 1.25 / 50.0`.
4. Successful calculation automatically enables the layer and opens the exact ten-row Option A legend.
5. Standard and satellite backgrounds retain the same colours and `0.58` opacity.
6. One-camera bands are visible; below-threshold/outside-envelope/beyond-cap areas are transparent.
7. Two- and three-camera overlaps show `2×` and `3×`; click inspection lists all contributors and the winner.
8. An invalid camera warns while a valid camera still renders.
9. A significant edit immediately hides the layer and shows `Stale — recalculate required` while retaining the result.
10. Save, close, reopen preserves stale/current state correctly; recalculation restores current visibility.
11. A controlled failed recalculation preserves the previous result.
12. Existing Phase 3 footprints, lighting, Wi-Fi, CAP, project JSON export, KML export, and Phase 7 report generation still function.
13. Browser console/page error count is zero.

- [ ] **Step 3: Run the final deterministic verification sequence**

Run sequentially from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\validate_engineering_data.py
Push-Location backend
..\.venv\Scripts\python.exe -m scripts.export_schema
Pop-Location
Push-Location frontend
corepack pnpm install --frozen-lockfile
corepack pnpm run test
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm run build
Pop-Location
git diff --check
git diff --exit-code -- Input
Get-FileHash Input\Miracle_Mile_Lighting_Poles.kml -Algorithm SHA256
```

Expected KML hash:

```text
2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328
```

Rerun schema generation after the implementation is staged/committed and require `git diff --exit-code -- schemas` to prove byte freshness.

- [ ] **Step 4: Write the verification summary and update execution state**

The summary must map every `BL016-01` through `BL016-20` acceptance ID to current command or rendered evidence, identify warnings, state exact commit/worktree, and label all historical evidence as historical. Update the execution index to “implementation readiness pending clean commit,” not accepted.

- [ ] **Step 5: Commit the bounded implementation/evidence set**

Stage only authorized BL-016 product, tests, generated schemas, canonical reference data, execution-index files, and harness evidence. Exclude screenshots/temp stores if the repository pattern keeps them under ignored `harness/tmp/`; exclude `.superpowers/`, caches, dependencies, build output, runtime projects, uploads, exports, and `Input/` changes.

```powershell
git diff --cached --check
git commit -m "docs: record BL-016 implementation readiness"
git status --short --branch
git rev-parse HEAD
```

- [ ] **Step 6: Create and verify the readiness manifest**

Populate `harness/verify/2026-09-22-bl-016-camera-pixel-density-readiness.json` from `harness/templates/implementation-readiness-template.json` with the final implementation commit, all milestones, acceptance IDs, commands, evidence paths, and expected clean worktree. Then run:

```powershell
.\.venv\Scripts\python.exe harness\verify\verify_phase_readiness.py --manifest harness\verify\2026-09-22-bl-016-camera-pixel-density-readiness.json
```

Expected: PASS, all milestones and acceptance IDs present, recorded commit equals HEAD, worktree clean, local `.superpowers/` content ignored and uncommitted, and no phase seal created.

- [ ] **Step 7: Produce the Independent-QA handoff and stop**

The handoff names the exact implementation commit, controlling spec/plan/work record, verification commands, live evidence, source hash, residual warnings, authorized QA scope, and explicit non-goals. Update `OPERATIONS.md` to state:

```text
BL-016 implementation is ready for Independent QA but remains unaccepted. Merge, push, later backlog work, Phase 8, and any seal remain unauthorized.
```

Stop for Independent QA. Do not self-approve, merge, push, start BL-019/BL-020, or create a phase seal.

## Final Definition of Done

- [ ] All ten tasks completed in order with milestone verification recorded.
- [ ] Project/software/API versions are `2.8.0`/`0.8.0`; migration is lossless and idempotent.
- [ ] One canonical immutable legend drives backend and frontend values.
- [ ] Analytic equation, supplied-lens, threshold, projection, cap, canonical-geometry, overlap, and safety-limit tests pass.
- [ ] API calculation is atomic; failures preserve stored bytes; significant edits produce hidden stale results.
- [ ] Frontend never calculates engineering density and never renders stale geometry.
- [ ] Option A palette, 58% opacity, automatic layer/legend, overlap styling, labels, and safe popup inspection are rendered and independently reproducible.
- [ ] Existing Phase 3 geometry and Phase 7 report outputs remain compatible without a new density report visualization.
- [ ] Backend full suite, engineering validator, schema freshness, frontend test/typecheck/lint/build, source diff, source hash, and production-browser workflow pass on the final implementation identity.
- [ ] Readiness verifier passes against the clean final implementation commit.
- [ ] Independent QA handoff exists; BL-016 is explicitly unaccepted; no seal or next-stage authorization exists.

## Recovery Protocol

1. Preserve the worktree and exact failing command/output.
2. Record the last verified milestone and affected files in the execution log.
3. Inspect `git status`, `git diff`, current HEAD, generated artifacts, and active local processes before retrying.
4. Make at least three materially different safe recovery attempts for environment, dependency, port, browser, cache, or file-lock failures.
5. Never discard, reset, overwrite, force-resolve, or manually create a seal.
6. Resume from the first incomplete milestone; do not rerun verified work unless its inputs changed.
7. Stop only for a proven blocker requiring new authority, an unresolved product/source-precedence decision, a prohibited file-boundary expansion, inability to preserve customer source, or required verification that remains impossible after safe recovery is exhausted.
