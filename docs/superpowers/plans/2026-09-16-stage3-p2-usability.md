# Stage 3 P2 Usability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land frontend-only Stage 3 items BL-013, BL-014, and BL-015 so engineers can reopen stored lighting results per area, see a result-first CAP pane with one honest primary action, and read the approved camera projection-boundary explanation.

**Architecture:** Keep the Stage 2 discipline switcher, the single `lightingCardAreaId` card, the area-keyed session position map, existing `runCap` operations, and existing Phase 6 eligibility helpers. Add small pure presentation helpers under `frontend/app/lib/` and reorganize `CapPlanningPanel` plus the Camera pane around those helpers. Do not change engines, schemas, APIs, catalogs, or project JSON layout.

**Tech Stack:** React/TypeScript workspace, existing `.mjs` presentation helpers, Node test runner (`node --test tests/*.test.mjs`), FastAPI store unchanged.

## Global Constraints

- Controlling design: `docs/superpowers/specs/2026-09-16-stage3-p2-usability-design.md`. Intake: `docs/web-app-review-2026-09-08.md` WA-06 / WA-07 / WA-08.
- Stage 3 is post-roadmap and item-based. It does not create Phase 8 or reopen Phases 1–7.
- Implementation remains separately gated until the user authorizes execution of this plan. Saving this plan does not authorize product edits.
- Frontend-only presentation change. No backend interface, schema, migration, catalog, lockfile, `Input/`, source-pole, or saved engineering-value changes.
- Existing-pole mode stays default. Never generate, move, optimize, or delete customer poles.
- Do not invent CAP defaults, candidate coordinates, node policies, limits, feasibility, RF performance, or installation claims.
- Do not bypass `capOperationEnabled` or `capBlockers`. Do not change Phase 4 invalidation. Do not add a camera pixel-density calculation, heat map, or new map layer.
- No multiple simultaneously pinned lighting-result cards. No persistence of card position or panel layout in project JSON.
- Camera downward angle remains degrees below horizontal. Displayed camera boundary is flat-ground FOV projection only.
- Preserve fixture colours: LITE red, WIFI yellow, SMART blue; CAP and priority-area colours stay distinct.
- Keep uploaded source files byte-for-byte unchanged. Miracle Mile SHA-256 must remain `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
- Do not merge, push, create a phase seal, or start BL-016 / BL-019 / BL-020.
- Base product commit for this plan: `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6` on `codex/bl-006-ies-associations`. Stage 2 implementation identity remains `eb3a606`. Preserve unrelated or user-owned files, including `.superpowers/`.
- Verification from `frontend/`: `corepack pnpm run typecheck`, `corepack pnpm run lint`, `corepack pnpm run test`, `corepack pnpm run build`. From repo root: `git diff --check` and `git diff --exit-code -- Input`.
- Do not commit unless the user asks. Commit steps below are for the authorized implementation session only.

## File structure

| Path | Responsibility |
|---|---|
| `frontend/app/lib/lighting-area-result-state.mjs` | Derive `current` / `stale` / `not-calculated` from an area plus its stored result. |
| `frontend/tests/lighting-area-result-state.test.mjs` | Helper coverage for those three states and Show-results enablement. |
| `frontend/app/lib/lighting-card-position.mjs` | Existing clamp/anchor helpers, plus session restore without mutating other areas. |
| `frontend/tests/lighting-card-position.test.mjs` | Existing WA-05 tests plus independent per-area session restore. |
| `frontend/app/lib/cap-primary-action.mjs` | Select the primary CAP action from existing `capOperationEnabled`. |
| `frontend/tests/cap-primary-action.test.mjs` | Primary action never bypasses blockers and always calls `recommend`. |
| `frontend/app/lib/camera-projection-legend.mjs` | Approved projection-boundary copy. |
| `frontend/tests/camera-projection-legend.test.mjs` | Exact limitation language; no detection/pixel-density claim. |
| `frontend/app/components/EngineeringWorkspace.tsx` | Show results, single open card, draft/delete session invariants, Camera legend. |
| `frontend/app/components/CapPlanningPanel.tsx` | Result-first order, one primary action, expandable advanced sections. |
| `frontend/app/globals.css` | Legend and expandable CAP section wrapping; no shell rewrite. |
| `frontend/tests/lighting-areas.test.mjs` | Show results does not calculate; draft/delete session behavior. |
| `frontend/tests/left-panel-layout.test.mjs` | Keep Stage 2 switcher/overflow; required CAP inputs remain expandable. |
| `frontend/tests/rendered-html.test.mjs` | New labels exist; CAP/camera disclaimers remain. |
| `harness/phases/2026-09-16-stage3-p2-usability.md` | Implementation work record. |
| `harness/logs/2026-09-16-stage3-p2-usability.md` | Exact command log. |

## Current code to reuse

- `lightingCardAreaId` and `lightingCardSessions` in `EngineeringWorkspace.tsx` already own the single visible card and session-only positions.
- `deleteCalculationArea` already closes the card and deletes that area's session.
- `cancelCalculationArea` already clears only draft flags.
- `capOperationEnabled(project, operation)` and `capBlockers(inputs)` in `frontend/app/lib/phase6-cap-workflows.mjs` remain the only eligibility source.
- `capResultSummary(project)` already distinguishes `not-calculated`, `current`, `current-with-unresolved`, and `error`.
- Camera pane geometry summary lives in the Camera discipline block around the `geometry-metrics` markup.
- Phase 4 invalidation deletes stored lighting results and sets `calculation_state.status` to `"not-calculated"`. The helper must not recreate deleted results.

## Stale versus not-calculated

`lightingAreaResultState(area, result)` classifies presentation only:

- `not-calculated` — `result == null`. Show results is disabled. No card can be opened.
- `current` — `result` is present and `area.calculation_state.status` is `"calculated"` or `"warning"`. Show results is enabled.
- `stale` — `result` is present but the area status is not `"calculated"` or `"warning"`. Show it as stale/unavailable; do not present statistics as current; do not enable Show results.

If a card is already open and invalidation removes the stored result, keep the existing unavailable card copy. Do not invent a persisted stale blob or change `staleCalculationState`.

---

### Task 1: Session records and preflight

**Files:**
- Create: `harness/phases/2026-09-16-stage3-p2-usability.md`
- Create: `harness/logs/2026-09-16-stage3-p2-usability.md`

**Interfaces:**
- Consumes: `harness/templates/phase-work-record-template.md`, `harness/templates/execution-log-template.md`, this plan, the approved design.
- Produces: dated work record with authorized frontend/harness/docs-index boundary and a command log ready for later rows.

- [ ] **Step 1: Confirm authorization and worktree**

Run:

```powershell
git rev-parse HEAD
git status --short --branch
git diff --stat
```

Expected: HEAD is `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6` or a later docs-only descendant that still contains that commit. Branch is `codex/bl-006-ies-associations`. Product files are clean except unrelated user-owned paths such as `.superpowers/`. If product files are dirty with unrelated work, preserve them and do not revert.

Stop if the user has not explicitly authorized Stage 3 implementation.

- [ ] **Step 2: Create the work record**

Copy `harness/templates/phase-work-record-template.md` to `harness/phases/2026-09-16-stage3-p2-usability.md`. Fill:

- Requested work: Stage 3 P2 usability, BL-013 / BL-014 / BL-015.
- Controlling documents: this plan and `docs/superpowers/specs/2026-09-16-stage3-p2-usability-design.md`.
- Authorized file boundary: `frontend/app/lib/`, `frontend/app/components/EngineeringWorkspace.tsx`, `frontend/app/components/CapPlanningPanel.tsx`, `frontend/app/globals.css`, `frontend/tests/`, `harness/phases/2026-09-16-stage3-p2-usability.md`, `harness/logs/2026-09-16-stage3-p2-usability.md`, `harness/verify/` summaries created later, and execution-index notes in `GOALS.md`, `PLANS.md`, `docs/current-status.md`, `docs/post-roadmap-backlog.md`.
- Non-goals: copy the design Non-goals section by link, not by reinterpretation.
- Stopping condition: `harness/verify/2026-09-16-stage3-p2-usability-verification.md` records PASS for BL-013, BL-014, and BL-015, and frontend typecheck/lint/test/build pass on the implementation commit.

- [ ] **Step 3: Record environment preflight**

From `frontend/`:

```powershell
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm run test
```

Expected: all three exit 0 on the unmodified product tree. Log exact commands in `harness/logs/2026-09-16-stage3-p2-usability.md`. Do not begin product edits if frontend commands cannot run.

- [ ] **Step 4: Commit records only if the user asked to commit**

If committing was requested:

```powershell
git add harness/phases/2026-09-16-stage3-p2-usability.md harness/logs/2026-09-16-stage3-p2-usability.md
git commit -m "docs: open Stage 3 P2 usability work record"
```

---

### Task 2: Lighting area result-state helper

**Files:**
- Create: `frontend/app/lib/lighting-area-result-state.mjs`
- Test: `frontend/tests/lighting-area-result-state.test.mjs`

**Interfaces:**
- Consumes: a calculation area's `calculation_state.status` and the stored value of `project.lighting_calculations.results[area.id]`.
- Produces:

```js
lightingAreaResultState(area, result) // "current" | "stale" | "not-calculated"
lightingAreaShowResultsEnabled(state) // boolean
```

- [ ] **Step 1: Write the failing test**

Create `frontend/tests/lighting-area-result-state.test.mjs`:

```javascript
import test from "node:test";
import assert from "node:assert/strict";
import {
  lightingAreaResultState,
  lightingAreaShowResultsEnabled,
} from "../app/lib/lighting-area-result-state.mjs";

const area = (status) => ({ calculation_state: { status } });
const result = { calculation_area_id: "area-a", statistics: { point_count: 12 } };

test("missing stored result is not-calculated", () => {
  assert.equal(lightingAreaResultState(area("not-calculated"), null), "not-calculated");
  assert.equal(lightingAreaResultState(area("calculated"), undefined), "not-calculated");
  assert.equal(lightingAreaShowResultsEnabled("not-calculated"), false);
});

test("stored result with calculated or warning status is current", () => {
  assert.equal(lightingAreaResultState(area("calculated"), result), "current");
  assert.equal(lightingAreaResultState(area("warning"), result), "current");
  assert.equal(lightingAreaShowResultsEnabled("current"), true);
});

test("stored result without a current area status is stale", () => {
  assert.equal(lightingAreaResultState(area("not-calculated"), result), "stale");
  assert.equal(lightingAreaResultState(area("error"), result), "stale");
  assert.equal(lightingAreaShowResultsEnabled("stale"), false);
});

test("helper does not treat a missing result as current even if status is calculated", () => {
  assert.equal(lightingAreaResultState(area("calculated"), null), "not-calculated");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/lighting-area-result-state.test.mjs`

Expected: FAIL with `Cannot find module` or `lightingAreaResultState is not a function`.

- [ ] **Step 3: Write minimal implementation**

Create `frontend/app/lib/lighting-area-result-state.mjs`:

```javascript
/**
 * Presentation state for one lighting calculation-area row.
 * Does not modify Project data or recreate invalidated results.
 *
 * @param {{ calculation_state?: { status?: string } } | null | undefined} area
 * @param {object | null | undefined} result stored lighting_calculations.results[area.id]
 * @returns {"current" | "stale" | "not-calculated"}
 */
export function lightingAreaResultState(area, result) {
  if (result == null) return "not-calculated";
  const status = area?.calculation_state?.status;
  if (status === "calculated" || status === "warning") return "current";
  return "stale";
}

/**
 * @param {"current" | "stale" | "not-calculated"} state
 */
export function lightingAreaShowResultsEnabled(state) {
  return state === "current";
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/lighting-area-result-state.test.mjs`

Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```powershell
git add frontend/app/lib/lighting-area-result-state.mjs frontend/tests/lighting-area-result-state.test.mjs
git commit -m "feat: classify lighting area rows as current, stale, or not-calculated"
```

---

### Task 3: Per-area lighting card session restore

**Files:**
- Modify: `frontend/app/lib/lighting-card-position.mjs`
- Test: `frontend/tests/lighting-card-position.test.mjs`

**Interfaces:**
- Consumes: the existing session map `{ [areaId]: { anchorLngLat, draggedPosition } }`, an area id, and `ringAnchorLngLat` fallback.
- Produces:

```js
resolveLightingCardSession(sessions, areaId, fallbackAnchor)
// { anchorLngLat: [number, number] | null, draggedPosition: { x: number, y: number } | null }
```

- [ ] **Step 1: Write the failing test**

Append to `frontend/tests/lighting-card-position.test.mjs`:

```javascript
import { clampCard, ringAnchorLngLat, cardOffsetFromProjected, resolveLightingCardSession } from "../app/lib/lighting-card-position.mjs";

test("resolveLightingCardSession restores independent dragged positions", () => {
  const sessions = {
    "area-a": { anchorLngLat: [-80.26, 25.75], draggedPosition: { x: 40, y: 80 } },
    "area-b": { anchorLngLat: [-80.24, 25.76], draggedPosition: { x: 120, y: 200 } },
  };
  assert.deepEqual(resolveLightingCardSession(sessions, "area-a", [-80.0, 25.0]), {
    anchorLngLat: [-80.26, 25.75],
    draggedPosition: { x: 40, y: 80 },
  });
  assert.deepEqual(resolveLightingCardSession(sessions, "area-b", [-80.0, 25.0]), {
    anchorLngLat: [-80.24, 25.76],
    draggedPosition: { x: 120, y: 200 },
  });
});

test("resolveLightingCardSession uses the polygon fallback when no session exists", () => {
  assert.deepEqual(resolveLightingCardSession({}, "area-c", [-80.21, 25.74]), {
    anchorLngLat: [-80.21, 25.74],
    draggedPosition: null,
  });
});

test("resolveLightingCardSession keeps a stored anchor when dragged position is null", () => {
  const sessions = {
    "area-a": { anchorLngLat: [-80.26, 25.75], draggedPosition: null },
  };
  assert.deepEqual(resolveLightingCardSession(sessions, "area-a", [-80.0, 25.0]), {
    anchorLngLat: [-80.26, 25.75],
    draggedPosition: null,
  });
});
```

Update the existing import line rather than adding a second import of the same module.

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/lighting-card-position.test.mjs`

Expected: FAIL with `resolveLightingCardSession is not a function`.

- [ ] **Step 3: Write minimal implementation**

Append to `frontend/app/lib/lighting-card-position.mjs`:

```javascript
/**
 * Restore one area's session-only card position without reading another area.
 *
 * @param {Record<string, { anchorLngLat?: [number, number] | null, draggedPosition?: { x: number, y: number } | null }> | null | undefined} sessions
 * @param {string} areaId
 * @param {[number, number] | null} fallbackAnchor
 * @returns {{ anchorLngLat: [number, number] | null, draggedPosition: { x: number, y: number } | null }}
 */
export function resolveLightingCardSession(sessions, areaId, fallbackAnchor) {
  const session = sessions?.[areaId];
  return {
    anchorLngLat: session?.anchorLngLat ?? fallbackAnchor ?? null,
    draggedPosition: session?.draggedPosition ?? null,
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/lighting-card-position.test.mjs`

Expected: PASS, including the existing WA-05 tests.

- [ ] **Step 5: Commit**

```powershell
git add frontend/app/lib/lighting-card-position.mjs frontend/tests/lighting-card-position.test.mjs
git commit -m "feat: restore per-area lighting card session positions independently"
```

---

### Task 4: Show results wiring in the lighting workspace

**Files:**
- Modify: `frontend/app/components/EngineeringWorkspace.tsx`
- Modify: `frontend/tests/lighting-areas.test.mjs`
- Modify: `frontend/tests/rendered-html.test.mjs`

**Interfaces:**
- Consumes: `lightingAreaResultState`, `lightingAreaShowResultsEnabled`, `resolveLightingCardSession`, `ringAnchorLngLat`.
- Produces: `showLightingResults(areaId: string)` that selects the area, opens that area's stored current result, restores its session position, and never calls `calculateLighting` / `calculateAllLightingAreas` / `calculateSelectedArea`.

- [ ] **Step 1: Write the failing tests**

Append to `frontend/tests/lighting-areas.test.mjs`:

```javascript
test("Show results opens a stored current result without calculating", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const show = workspace.match(/function showLightingResults\([\s\S]*?\n  \}/)?.[0] ?? "";
  assert.match(workspace, /Show results/);
  assert.match(show, /lightingAreaResultState\(area, result\) !== "current"/);
  assert.match(show, /setSelectedCalculationAreaId\(areaId\)/);
  assert.match(show, /resolveLightingCardSession/);
  assert.match(show, /setLightingCardAreaId\(areaId\)/);
  assert.doesNotMatch(show, /calculateLighting/);
  assert.doesNotMatch(show, /calculateAllLightingAreas/);
  assert.doesNotMatch(show, /calculateSelectedArea/);
});

test("only one lighting result card identity exists", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(workspace, /const \[lightingCardAreaId, setLightingCardAreaId\] = useState<string \| null>\(null\)/);
  assert.doesNotMatch(workspace, /lightingCardAreaIds/);
});

test("creating or cancelling a lighting draft does not discard stored results or sessions", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const start = workspace.match(/function startCalculationArea\(\) \{[\s\S]*?\n  \}/)?.[0] ?? "";
  const cancel = workspace.match(/function cancelCalculationArea\(\) \{[\s\S]*?\n  \}/)?.[0] ?? "";
  assert.doesNotMatch(start, /lighting_calculations\.results/);
  assert.doesNotMatch(start, /setLightingCardSessions/);
  assert.doesNotMatch(cancel, /lighting_calculations\.results/);
  assert.doesNotMatch(cancel, /setLightingCardSessions/);
  assert.doesNotMatch(cancel, /setLightingCardAreaId/);
});

test("deleting a lighting area removes its session and closes its card", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const remove = workspace.match(/function deleteCalculationArea\([\s\S]*?\n  \}/)?.[0] ?? "";
  assert.match(remove, /delete draft\.lighting_calculations\.results\[areaId\]/);
  assert.match(remove, /if \(lightingCardAreaId === areaId\) setLightingCardAreaId\(null\)/);
  assert.match(remove, /delete next\[areaId\]/);
});

test("discipline switching does not clear an active lighting polygon draft", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  assert.match(workspace, /onClick=\{\(\) => setLeftDiscipline\(item.id\)\}/);
  assert.doesNotMatch(workspace, /setLeftDiscipline\(item.id\); setCalculationDraft/);
  assert.doesNotMatch(workspace, /setLeftDiscipline\(item.id\); setDrawingCalculationArea\(false\)/);
});
```

In `frontend/tests/rendered-html.test.mjs`, inside the existing workspace source test that already reads `EngineeringWorkspace.tsx`, add:

```javascript
assert.match(workspace, /Show results/);
assert.match(workspace, /showLightingResults/);
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test tests/lighting-areas.test.mjs tests/rendered-html.test.mjs`

Expected: FAIL on missing `showLightingResults` / `Show results`.

- [ ] **Step 3: Write minimal implementation**

In `frontend/app/components/EngineeringWorkspace.tsx`:

1. Add imports:

```tsx
import { lightingAreaResultState, lightingAreaShowResultsEnabled } from "../lib/lighting-area-result-state.mjs";
import { resolveLightingCardSession, ringAnchorLngLat } from "../lib/lighting-card-position.mjs";
```

Remove the previous `ringAnchorLngLat`-only import so the module is imported once.

2. Add this function after `deleteCalculationArea`:

```tsx
  function showLightingResults(areaId: string) {
    if (!project) return;
    const area = project.calculation_areas.find((item) => item.id === areaId);
    const result = project.lighting_calculations.results[areaId];
    if (!area || lightingAreaResultState(area, result) !== "current") return;
    const fallback = ringAnchorLngLat(area.wgs84_coordinates);
    const resolved = resolveLightingCardSession(lightingCardSessions, areaId, fallback);
    setSelectedCalculationAreaId(areaId);
    setLightingCardSessions((sessions) => ({ ...sessions, [areaId]: resolved }));
    setLightingCardAreaId(areaId);
  }
```

3. Replace the lighting-area row map with a block that distinguishes the three states. Keep provenance/disclaimer markup only for `current`. The action row must include Show results:

```tsx
{project?.calculation_areas.map((area) => {
  const result = project.lighting_calculations.results[area.id];
  const resultState = lightingAreaResultState(area, result);
  const showResults = lightingAreaShowResultsEnabled(resultState);
  const stats = resultState === "current" ? result?.statistics : undefined;
  return (
    <div className={`calculation-row ${selectedCalculationAreaId === area.id ? "selected" : ""}`} key={area.id}>
      <strong>{area.name} · {area.classification}</strong>
      <span>
        {resultState === "current" && stats
          ? `${stats.point_count} points · Eavg ${formatLuxWithUnit(stats.average_illuminance_lux)} · Emin ${formatLuxWithUnit(stats.minimum_illuminance_lux)} · Emax ${formatLuxWithUnit(stats.maximum_illuminance_lux)}`
          : resultState === "stale"
            ? "Stale — recalculate"
            : "Not calculated"}
      </span>
      {resultState === "current" && stats && result && (
        <small>Emin/Eavg {stats.emin_over_eavg?.toFixed(3) ?? "—"} · Emin/Emax {stats.emin_over_emax?.toFixed(3) ?? "—"} · {result.contributing_fixture_count} fixtures</small>
      )}
      <div>
        <button className="quiet-button" onClick={() => setSelectedCalculationAreaId(area.id)}>Select</button>
        <button
          type="button"
          className="quiet-button"
          disabled={!showResults}
          title={resultState === "current" ? "Show stored results" : resultState === "stale" ? "Stored result is stale; recalculate" : "No stored result"}
          onClick={() => showLightingResults(area.id)}
        >
          Show results
        </button>
        <button className="quiet-button" onClick={() => editCalculationArea(area.id)}>Edit</button>
        <button className="quiet-button" onClick={() => editCalculationArea(area.id, true)}>Redraw</button>
        <button className="quiet-button" onClick={() => deleteCalculationArea(area.id)}>Delete</button>
      </div>
      {resultState === "current" && result && (
        <>
          <p className="lighting-disclaimer">{result.disclaimer}</p>
          <p className="helper">Approved simplified direct-light model; not a standards-compliance determination.</p>
          <details className="lighting-provenance">
            <summary>Calculation and fixture provenance</summary>
            <p>Model {result.calculation_model_version} · CRS {result.projected_crs} · polygon r{result.polygon_revision}<br />Grid {result.statistics.grid_spacing_m} m · origin {result.grid_origin_m.join(", ")} m · {result.grid_anchor_policy}<br />Boundary {result.boundary_policy} · plane {area.calculation_plane_elevation_m} m · maintenance factor {area.maintenance_factor}</p>
            {result.fixture_provenance.map((fixture) => (
              <p key={fixture.pole_id}>
                <strong>{fixture.pole_id}</strong><br />
                {fixture.fixture_model_id} r{fixture.fixture_model_revision} · {fixture.ies_original_filename} r{fixture.ies_file_revision}<br />
                SHA-256 {fixture.ies_sha256} · parsed Type {fixture.ies_parsed_metadata.photometric_type ?? "—"}, {fixture.ies_parsed_metadata.input_watts ?? "—"} W, {fixture.ies_parsed_metadata.vertical_angle_count ?? "—"}×{fixture.ies_parsed_metadata.horizontal_angle_count ?? "—"} angles<br />
                Height {fixture.mounting_height_m} m · azimuth {fixture.fixture_azimuth_deg}° · origin {fixture.origin_projected_m.join(", ")} m
                {fixture.warnings.length ? <><br />Warnings: {fixture.warnings.join(" ")}</> : null}
              </p>
            ))}
          </details>
          {result.warnings.map((warning) => <div className="warning-card" key={warning}>{warning}</div>)}
        </>
      )}
    </div>
  );
})}
```

4. In the `LightingResultCard` render, resolve the session through the helper and never label a missing/stale result current:

```tsx
const session = resolveLightingCardSession(
  lightingCardSessions,
  lightingCardAreaId,
  ringAnchorLngLat(area.wgs84_coordinates),
);
const result = project.lighting_calculations.results[lightingCardAreaId] ?? null;
const resultState = lightingAreaResultState(area, result);
return (
  <LightingResultCard
    map={mapInstance}
    areaName={area.name}
    result={resultState === "current" ? result : null}
    unavailableReason={resultState === "current" ? null : "Lighting result unavailable or invalidated for this area."}
    anchorLngLat={session.anchorLngLat}
    draggedPosition={session.draggedPosition}
    onDraggedPosition={(position) => setLightingCardSessions((sessions) => ({
      ...sessions,
      [lightingCardAreaId]: {
        anchorLngLat: sessions[lightingCardAreaId]?.anchorLngLat ?? ringAnchorLngLat(area.wgs84_coordinates),
        draggedPosition: position,
      },
    }))}
    onClose={() => setLightingCardAreaId(null)}
  />
);
```

Do not change `startCalculationArea`, `cancelCalculationArea`, or `deleteCalculationArea` unless tests prove they now mutate results/sessions. They already match Task 4's assertions.

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tests/lighting-areas.test.mjs tests/lighting-area-result-state.test.mjs tests/lighting-card-position.test.mjs tests/rendered-html.test.mjs`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add frontend/app/components/EngineeringWorkspace.tsx frontend/tests/lighting-areas.test.mjs frontend/tests/rendered-html.test.mjs
git commit -m "feat: reopen stored lighting results without recalculating"
```

---

### Task 5: CAP primary-action helper

**Files:**
- Create: `frontend/app/lib/cap-primary-action.mjs`
- Test: `frontend/tests/cap-primary-action.test.mjs`

**Interfaces:**
- Consumes: `capOperationEnabled(project, "recommend")` from `frontend/app/lib/phase6-cap-workflows.mjs`.
- Produces:

```js
CAP_PRIMARY_ACTION_LABEL // "Calculate CAP recommendation"
capPrimaryAction(project) // { operation: "recommend", label: string, enabled: boolean }
```

- [ ] **Step 1: Write the failing test**

Create `frontend/tests/cap-primary-action.test.mjs`:

```javascript
import test from "node:test";
import assert from "node:assert/strict";
import { capPrimaryAction, CAP_PRIMARY_ACTION_LABEL } from "../app/lib/cap-primary-action.mjs";
import { capOperationEnabled } from "../app/lib/phase6-cap-workflows.mjs";

function eligibleProject(operationMode = "recommend") {
  return {
    cap_planning_inputs: {
      profile: {
        product_mapping: { status: "known" },
        variant: { status: "known" },
        band_and_jurisdiction: { status: "known" },
        link_distance_m: { status: "known" },
        node_limit: { status: "known" },
        child_limit: { status: "known" },
        hop_limit: { status: "known" },
        gateway_appliance_counting: { status: "known" },
        colocated_fixture_counting: { status: "known" },
        redundancy: { status: "known" },
        node_policy: { LITE: "node", WIFI: "node", SMART: "node" },
        mode_permission: "recommend_from_approved_pool",
        operation_mode: operationMode,
      },
      candidates: [{
        prohibited: false,
        mounting_confirmed: true,
        power_confirmed: true,
        backhaul_confirmed: true,
        enclosure_confirmed: true,
        survey_status: "confirmed",
        indoor_outdoor: "outdoor",
      }],
    },
  };
}

test("primary action is recommend with the approved label", () => {
  assert.equal(CAP_PRIMARY_ACTION_LABEL, "Calculate CAP recommendation");
  const action = capPrimaryAction(eligibleProject());
  assert.equal(action.operation, "recommend");
  assert.equal(action.label, "Calculate CAP recommendation");
  assert.equal(action.enabled, true);
  assert.equal(action.enabled, capOperationEnabled(eligibleProject(), "recommend"));
});

test("primary action stays recommend and disabled when blockers exist", () => {
  const blocked = { cap_planning_inputs: { profile: { node_policy: { LITE: "unknown", WIFI: "unknown", SMART: "unknown" }, mode_permission: "unknown", operation_mode: "recommend" }, candidates: [] } };
  const action = capPrimaryAction(blocked);
  assert.equal(action.operation, "recommend");
  assert.equal(action.enabled, false);
  assert.equal(action.enabled, capOperationEnabled(blocked, "recommend"));
});

test("validate-only mode does not fake recommendation availability", () => {
  const project = eligibleProject("validate");
  const action = capPrimaryAction(project);
  assert.equal(action.operation, "recommend");
  assert.equal(action.enabled, false);
  assert.equal(capOperationEnabled(project, "validate"), true);
});

test("null project does not enable recommendation", () => {
  assert.deepEqual(capPrimaryAction(null), {
    operation: "recommend",
    label: "Calculate CAP recommendation",
    enabled: false,
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/cap-primary-action.test.mjs`

Expected: FAIL with missing module.

- [ ] **Step 3: Write minimal implementation**

Create `frontend/app/lib/cap-primary-action.mjs`:

```javascript
import { capOperationEnabled } from "./phase6-cap-workflows.mjs";

export const CAP_PRIMARY_ACTION_LABEL = "Calculate CAP recommendation";

/**
 * @param {object | null | undefined} project
 * @returns {{ operation: "recommend", label: string, enabled: boolean }}
 */
export function capPrimaryAction(project) {
  return {
    operation: "recommend",
    label: CAP_PRIMARY_ACTION_LABEL,
    enabled: capOperationEnabled(project, "recommend"),
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/cap-primary-action.test.mjs`

Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```powershell
git add frontend/app/lib/cap-primary-action.mjs frontend/tests/cap-primary-action.test.mjs
git commit -m "feat: select the CAP primary action from existing recommend eligibility"
```

---

### Task 6: Result-first CAP panel

**Files:**
- Modify: `frontend/app/components/CapPlanningPanel.tsx`
- Modify: `frontend/app/globals.css`
- Modify: `frontend/tests/left-panel-layout.test.mjs`
- Modify: `frontend/tests/rendered-html.test.mjs`
- Modify: `frontend/tests/cap-workflow-view.test.mjs` only if a string assertion breaks; keep `capResultSummary` states unchanged.

**Interfaces:**
- Consumes: `capPrimaryAction(project)`, `capResultSummary(project)`, `capBlockers`, `capOperationEnabled`, existing `runCap`, `onReviewInput`, `onFocusCandidate`, `onShowSelectedSites`.
- Produces: panel DOM order: result or not-calculated → primary action → blockers/unresolved → selected sites/map actions when a result exists → expandable required inputs, candidates/locks, secondary operations, topology/provenance.

- [ ] **Step 1: Write the failing tests**

Replace the CAP expandable assertion in `frontend/tests/left-panel-layout.test.mjs` with:

```javascript
test("CAP required inputs stay available and expandable rather than deleted", async () => {
  const capPanel = await readFile(new URL("../app/components/CapPlanningPanel.tsx", import.meta.url), "utf8");
  assert.match(capPanel, /CAP preflight blockers/);
  assert.match(capPanel, /<details className="cap-required-inputs">/);
  assert.doesNotMatch(capPanel, /<details className="cap-required-inputs" open>/);
  assert.match(capPanel, /Required CAP inputs/);
  assert.match(capPanel, /cap-field-operation_mode/);
  assert.match(capPanel, /id="cap-section-candidates"/);
  assert.match(capPanel, /Calculate \/ rank/);
  assert.match(capPanel, /Validate/);
});

test("CAP pane is result-first with one recommend primary action", async () => {
  const capPanel = await readFile(new URL("../app/components/CapPlanningPanel.tsx", import.meta.url), "utf8");
  const resultIdx = capPanel.indexOf("cap-result-summary");
  const primaryIdx = capPanel.indexOf("cap-primary-action");
  const blockerIdx = capPanel.indexOf("CAP preflight blockers");
  const inputsIdx = capPanel.indexOf("Required CAP inputs");
  const candidatesIdx = capPanel.indexOf("id=\"cap-section-candidates\"");
  const secondaryIdx = capPanel.indexOf("Advanced operations");
  assert.ok(resultIdx >= 0 && primaryIdx > resultIdx);
  assert.ok(blockerIdx > primaryIdx);
  assert.ok(inputsIdx > blockerIdx);
  assert.ok(candidatesIdx > inputsIdx);
  assert.ok(secondaryIdx > candidatesIdx);
  assert.match(capPanel, /runCap\(primary.operation\)/);
  assert.match(capPanel, /Calculate CAP recommendation/);
  assert.doesNotMatch(capPanel, /onClick=\{\(\) => runCap\("recommend"\)\}/);
  assert.match(capPanel, /runCap\("calculate"\)/);
  assert.match(capPanel, /runCap\("validate"\)/);
  assert.match(capPanel, /Current result has zero selected CAP sites/);
  assert.match(capPanel, /unresolved node/);
});
```

In `frontend/tests/rendered-html.test.mjs` CAP assertions, add:

```javascript
assert.match(capPanel, /Calculate CAP recommendation/);
assert.match(capPanel, /capPrimaryAction/);
assert.match(capPanel, /Advanced operations/);
```

Keep existing matches for `Show selected sites on map`, `Recommended CAP units`, `Review input`, `CAP_DISCLAIMER`, and `Advanced topology, score trace, and provenance`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test tests/left-panel-layout.test.mjs tests/rendered-html.test.mjs`

Expected: FAIL on missing `capPrimaryAction` / default-open required inputs / `Advanced operations`.

- [ ] **Step 3: Write minimal implementation**

Replace `frontend/app/components/CapPlanningPanel.tsx` with this complete file. Field ids, mutation recipes, and `runCap` operation names stay the same. The toolbar **Recommend CAP** control in `EngineeringWorkspace.tsx` stays as-is. This panel's only recommend control is the primary button.

```tsx
"use client";

import { useEffect, useRef } from "react";
import type { CapCandidateSite, EffectivePole, FixtureType, Project } from "../lib/types";
import { CAP_DISCLAIMER, capBlockers, capOperationEnabled } from "../lib/phase6-cap-workflows.mjs";
import { blockerFocusTarget, blockerLabel, candidateDisplayLabel, capResultSummary } from "../lib/cap-workflow-view.mjs";
import { capPrimaryAction } from "../lib/cap-primary-action.mjs";

type CapPlanningPanelProps = {
  project: Project | null;
  selected: EffectivePole | null;
  busy: boolean;
  focused: boolean;
  focusNonce: number;
  manualCapLongitude: string;
  manualCapLatitude: string;
  onManualCapLongitude: (value: string) => void;
  onManualCapLatitude: (value: string) => void;
  mutateProject: (recipe: (draft: Project) => void) => void;
  runCap: (operation: "calculate" | "validate" | "recommend") => void;
  addSelectedPoleCapCandidate: () => void;
  addManualCapCandidate: () => void;
  updateCapCandidate: (candidate: CapCandidateSite, patch: Partial<CapCandidateSite>) => void;
  removeCapCandidate: (candidateId: string) => void;
  onShowSelectedSites: () => void;
  onFocusCandidate: (candidateId: string) => void;
  onReviewInput: (elementId: string) => void;
};

export default function CapPlanningPanel({
  project,
  selected,
  busy,
  focused,
  focusNonce,
  manualCapLongitude,
  manualCapLatitude,
  onManualCapLongitude,
  onManualCapLatitude,
  mutateProject,
  runCap,
  addSelectedPoleCapCandidate,
  addManualCapCandidate,
  updateCapCandidate,
  removeCapCandidate,
  onShowSelectedSites,
  onFocusCandidate,
  onReviewInput,
}: CapPlanningPanelProps) {
  const panelRef = useRef<HTMLElement | null>(null);
  const summary = capResultSummary(project);
  const blockers = project ? capBlockers(project.cap_planning_inputs) : [];
  const primary = capPrimaryAction(project);

  useEffect(() => {
    if (focusNonce > 0 && panelRef.current) {
      panelRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
      panelRef.current.focus({ preventScroll: true });
    }
  }, [focusNonce]);

  return (
    <section
      ref={panelRef}
      id="cap-planning-panel"
      className={`section cap-planning-panel${focused ? " cap-planning-panel-focused" : ""}`}
      tabIndex={-1}
      aria-label="CAP Planning"
    >
      <div className="section-heading">
        <h3>CAP Planning</h3>
        <span className="helper">Phase 6 · JNET1 graph</span>
      </div>
      <p className="lighting-disclaimer">{CAP_DISCLAIMER}</p>

      {!project ? (
        <p className="helper">Import or create a project to preserve unknown CAP inputs and inspect blockers.</p>
      ) : (
        <>
          <div className="cap-result-summary" aria-live="polite">
            {summary.state === "not-calculated" && (
              <p className="helper">No current CAP result.</p>
            )}
            {summary.state === "error" && (
              <div className="warning-card"><strong>CAP calculation error</strong><p>The last operation failed. Review inputs and try again. This is not an installation-ready answer.</p></div>
            )}
            {(summary.state === "current" || summary.state === "current-with-unresolved") && (
              <p><strong>Current CAP result</strong></p>
            )}
          </div>

          <div className="cap-panel-block">
            <div className="button-row cap-primary-action">
              <button
                type="button"
                className="tool-button primary"
                onClick={() => runCap(primary.operation)}
                disabled={!primary.enabled || busy}
              >
                {primary.label}
              </button>
            </div>
            {!primary.enabled && (
              <p className="helper">Recommendation is unavailable until existing Phase 6 preflight permits it. Review the blockers below. Do not invent inputs or candidate coordinates.</p>
            )}
          </div>

          <div className="cap-panel-block">
            {blockers.length ? (
              <div className="warning-card">
                <strong>CAP preflight blockers</strong>
                <ul className="cap-blocker-list">
                  {blockers.map((key) => {
                    const target = blockerFocusTarget(key);
                    return (
                      <li key={key}>
                        <span>{blockerLabel(key)}</span>
                        {target && (
                          <button type="button" className="quiet-button" onClick={() => onReviewInput(target)}>Review input</button>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </div>
            ) : (
              <div className="warning-card info">Preflight complete for the selected test/project inputs.</div>
            )}
            {summary.state === "current-with-unresolved" && (
              <div className="warning-card"><strong>{summary.unresolvedIds.length} unresolved node{summary.unresolvedIds.length === 1 ? "" : "s"}</strong><p>Incomplete graph coverage — not an installation-ready answer.</p></div>
            )}
          </div>

          {(summary.state === "current" || summary.state === "current-with-unresolved") && (
            <div className="cap-panel-block">
              <p><strong>Recommended CAP units: {summary.selectedIds.length}</strong></p>
              {summary.selectedIds.length === 0 ? (
                <p className="helper">Current result has zero selected CAP sites.</p>
              ) : (
                <ul className="cap-selected-list">
                  {summary.selectedIds.map((id) => (
                    <li key={id}>
                      <span><code>{id}</code> · {candidateDisplayLabel(project, id)}</span>
                      <button type="button" className="quiet-button" onClick={() => onFocusCandidate(id)}>Locate</button>
                    </li>
                  ))}
                </ul>
              )}
              <button type="button" className="quiet-button" onClick={onShowSelectedSites} disabled={!summary.selectedIds.length}>
                Show selected sites on map
              </button>
              {project.cap_calculations.result?.warnings?.length ? (
                <div className="cap-result-warnings">
                  {project.cap_calculations.result.warnings.map((warning) => (
                    <div className="warning-card" key={warning}>{warning}</div>
                  ))}
                </div>
              ) : null}
              <p className="helper">{CAP_DISCLAIMER}</p>
            </div>
          )}

          <details className="cap-required-inputs">
            <summary>Required CAP inputs</summary>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="cap-field-operation_mode">Operation mode</label>
                <select id="cap-field-operation_mode" value={project.cap_planning_inputs.profile.operation_mode} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.operation_mode = event.target.value as "validate" | "recommend"; })}>
                  <option value="validate">Validate explicit CAP selection</option>
                  <option value="recommend">Recommend from approved pool</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="cap-field-mode_permission">Mode permission</label>
                <select id="cap-field-mode_permission" value={project.cap_planning_inputs.profile.mode_permission} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.mode_permission = event.target.value as "validate_only" | "recommend_from_approved_pool" | "unknown"; })}>
                  <option value="unknown">Unknown — blocks planning</option>
                  <option value="validate_only">Validate only</option>
                  <option value="recommend_from_approved_pool">Recommend from approved pool</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="cap-field-gateway_appliance_counting">Gateway appliance counting</label>
                <select id="cap-field-gateway_appliance_counting" value={String(project.cap_planning_inputs.profile.gateway_appliance_counting.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.gateway_appliance_counting; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}>
                  <option value="">Unknown — blocks planning</option>
                  <option value="included">Included in per-CAP node count</option>
                  <option value="excluded">Excluded from per-CAP node count</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="cap-field-colocated_fixture_counting">Co-located fixture counting</label>
                <select id="cap-field-colocated_fixture_counting" value={String(project.cap_planning_inputs.profile.colocated_fixture_counting.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.colocated_fixture_counting; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}>
                  <option value="">Unknown — blocks planning</option>
                  <option value="distinct_managed_node_once">Distinct managed fixture node once</option>
                  <option value="merged_not_separate">Merged, not a separate fixture node</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="cap-field-redundancy">Redundancy policy</label>
                <select id="cap-field-redundancy" value={String(project.cap_planning_inputs.profile.redundancy.value ?? "")} onChange={(event) => mutateProject((draft) => { const field = draft.cap_planning_inputs.profile.redundancy; field.value = event.target.value || null; field.status = event.target.value ? "known" : "unknown"; field.source = event.target.value ? "TEST-ONLY user-entered project input" : null; field.applicability = event.target.value ? "test-only" : null; field.classification = event.target.value ? "user_approved_assumption" : "unknown"; })}>
                  <option value="">Unknown — blocks planning</option>
                  <option value="single_allowed_with_warning">Single allowed with warning</option>
                  <option value="n_plus_one_validation">N+1 graph validation</option>
                  <option value="user_supplied_only">User supplied only</option>
                </select>
              </div>
            </div>

            <div className="form-grid">
              {(["LITE", "WIFI", "SMART"] as FixtureType[]).map((type) => (
                <div className="field" key={type}>
                  <label htmlFor={`cap-field-node-${type}`}>{type} node disposition</label>
                  <select id={`cap-field-node-${type}`} value={project.cap_planning_inputs.profile.node_policy[type]} onChange={(event) => mutateProject((draft) => { draft.cap_planning_inputs.profile.node_policy[type] = event.target.value as "node" | "non_node" | "unknown"; })}>
                    <option value="unknown">Unknown — blocks planning</option>
                    <option value="node">Node</option>
                    <option value="non_node">Non-node</option>
                  </select>
                </div>
              ))}
            </div>

            <div className="form-grid">
              {(["product_mapping", "variant", "band_and_jurisdiction", "link_distance_m", "node_limit", "child_limit", "hop_limit"] as const).map((field) => (
                <div className="field" key={field}>
                  <label htmlFor={`cap-field-${field}`}>{field.replaceAll("_", " ")} · provenance-bearing</label>
                  <input
                    id={`cap-field-${field}`}
                    value={String(project.cap_planning_inputs.profile[field].value ?? "")}
                    onChange={(event) => mutateProject((draft) => {
                      const value = event.target.value;
                      const target = draft.cap_planning_inputs.profile[field];
                      target.value = field.endsWith("limit") || field === "link_distance_m" ? (value === "" ? null : Number(value)) : value || null;
                      target.status = value ? "known" : "unknown";
                      target.source = value ? "user-entered project input" : null;
                      target.applicability = value ? "project planning" : null;
                      target.classification = value ? "user_approved_assumption" : "unknown";
                    })}
                  />
                </div>
              ))}
            </div>
          </details>

          <details className="cap-required-inputs" id="cap-section-candidates">
            <summary>Candidates and locks</summary>
            <div className="button-row">
              <button className="quiet-button" onClick={addSelectedPoleCapCandidate} disabled={!selected || busy}>Add selected pole as CAP site</button>
              <button className="quiet-button" disabled={!selected || busy} onClick={() => selected && mutateProject((draft) => {
                const nodeId = `fixture/${selected.id}`;
                const ids = draft.cap_planning_inputs.excluded_node_ids;
                draft.cap_planning_inputs.excluded_node_ids = ids.includes(nodeId) ? ids.filter((id) => id !== nodeId) : [...ids, nodeId];
              })}>
                {selected && project.cap_planning_inputs.excluded_node_ids.includes(`fixture/${selected.id}`) ? "Include current CAP node" : "Exclude current CAP node"}
              </button>
            </div>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="manual-cap-longitude">Manual non-pole longitude</label>
                <input id="manual-cap-longitude" type="number" min="-180" max="180" step="any" value={manualCapLongitude} onChange={(event) => onManualCapLongitude(event.target.value)} />
              </div>
              <div className="field">
                <label htmlFor="manual-cap-latitude">Manual non-pole latitude</label>
                <input id="manual-cap-latitude" type="number" min="-90" max="90" step="any" value={manualCapLatitude} onChange={(event) => onManualCapLatitude(event.target.value)} />
              </div>
            </div>
            <div className="button-row">
              <button className="quiet-button" onClick={addManualCapCandidate} disabled={busy}>Add distinct manual non-pole CAP site</button>
            </div>
            {project.cap_planning_inputs.candidates.map((candidate) => (
              <div className="priority-row" key={candidate.id}>
                <strong>{candidate.kind === "existing_pole" ? `Pole ${candidate.pole_id}` : "Manual non-pole site"}</strong>
                <span>mounting {String(candidate.mounting_confirmed)} · power {String(candidate.power_confirmed)} · backhaul {String(candidate.backhaul_confirmed)} · survey {candidate.survey_status} · priority {candidate.priority}</span>
                <div>
                  <button className="quiet-button" onClick={() => updateCapCandidate(candidate, { mounting_confirmed: true, power_confirmed: true, backhaul_confirmed: true, enclosure_confirmed: true, indoor_outdoor: "outdoor", survey_status: "confirmed", notes: "TEST-ONLY feasibility values; not approved site engineering." })}>Mark test-only feasible</button>
                  <button className="quiet-button" onClick={() => updateCapCandidate(candidate, { preferred: !candidate.preferred })}>{candidate.preferred ? "Remove preference" : "Prefer"}</button>
                  <button className="quiet-button" onClick={() => updateCapCandidate(candidate, { prohibited: !candidate.prohibited })}>{candidate.prohibited ? "Allow" : "Prohibit"}</button>
                  <button className="quiet-button" onClick={() => updateCapCandidate(candidate, { locked_selected: !candidate.locked_selected })}>{candidate.locked_selected ? "Unlock selected" : "Lock selected"}</button>
                  <button className="quiet-button" disabled={!selected} onClick={() => selected && mutateProject((draft) => {
                    const nodeId = `fixture/${selected.id}`;
                    const gatewayId = `gateway/${candidate.id}`;
                    const locks = draft.cap_planning_inputs.primary_assignment_locks;
                    if (locks[nodeId] === gatewayId) delete locks[nodeId]; else locks[nodeId] = gatewayId;
                  })}>{selected && project.cap_planning_inputs.primary_assignment_locks[`fixture/${selected.id}`] === `gateway/${candidate.id}` ? "Unlock current node assignment" : "Lock current node to this CAP"}</button>
                  <button className="quiet-button" disabled={!selected} onClick={() => selected && mutateProject((draft) => {
                    const nodeId = `fixture/${selected.id}`;
                    const gatewayId = `gateway/${candidate.id}`;
                    const locks = draft.cap_planning_inputs.parent_locks;
                    if (locks[nodeId] === gatewayId) delete locks[nodeId]; else locks[nodeId] = gatewayId;
                  })}>{selected && project.cap_planning_inputs.parent_locks[`fixture/${selected.id}`] === `gateway/${candidate.id}` ? "Unlock current parent" : "Lock current parent to this CAP"}</button>
                  <button className="quiet-button" onClick={() => mutateProject((draft) => {
                    const ids = draft.cap_planning_inputs.excluded_candidate_ids;
                    draft.cap_planning_inputs.excluded_candidate_ids = ids.includes(candidate.id) ? ids.filter((id) => id !== candidate.id) : [...ids, candidate.id];
                  })}>{project.cap_planning_inputs.excluded_candidate_ids.includes(candidate.id) ? "Include candidate" : "Exclude candidate"}</button>
                  <button className="quiet-button" onClick={() => onFocusCandidate(candidate.id)}>Locate</button>
                  <button className="quiet-button" onClick={() => removeCapCandidate(candidate.id)}>Delete site</button>
                </div>
              </div>
            ))}
            {!project.cap_planning_inputs.candidates.length && <p className="helper">No CAP candidates yet. Add an existing-pole or distinct manual non-pole site.</p>}
          </details>

          <details className="cap-required-inputs">
            <summary>Advanced operations</summary>
            <div className="button-row">
              <button className="quiet-button" onClick={() => runCap("calculate")} disabled={!capOperationEnabled(project, "calculate") || busy} title="Calculate / rank: inspect candidate ranking">Calculate / rank</button>
              <button className="quiet-button" onClick={() => runCap("validate")} disabled={!capOperationEnabled(project, "validate") || busy} title="Validate: check your explicit selection">Validate</button>
            </div>
            <p className="helper">Calculate / rank: inspect candidate ranking. Validate: check your explicit selection. Recommend: choose from the approved candidate pool.</p>
            <p>{project.cap_planning_inputs.candidates.length} explicit CAP candidate sites · {project.cap_recommendations.selected_candidate_ids.length} selected.</p>
          </details>

          <details className="lighting-provenance">
            <summary>Advanced topology, score trace, and provenance</summary>
            {project.cap_calculations.result ? (
              <>
                <p>Fingerprint {project.cap_calculations.calculation_input_sha256} · CRS {project.cap_calculations.result.projected_crs}</p>
                {project.cap_calculations.result.assignments.map((item) => (
                  <p key={item.node_id}>{item.node_id} → {item.parent_id} · hop {item.hop} · {item.distance_m.toFixed(6)} m · distance-qualified conceptual link; not RF-predicted</p>
                ))}
                {project.cap_calculations.result.warnings.map((warning) => <p key={warning}>{warning}</p>)}
              </>
            ) : (
              <p className="helper">No topology until a successful calculation exists.</p>
            )}
          </details>
        </>
      )}
    </section>
  );
}
```

In `frontend/app/globals.css`, after `.cap-required-inputs > summary`, add:

```css
.cap-required-inputs + .cap-required-inputs { margin-top: 8px; }
.cap-primary-action { display: flex; flex-wrap: wrap; gap: 8px; min-width: 0; }
```

Do not describe results as RF coverage, capacity, performance, installation feasibility, or compliance. Existing `CAP_DISCLAIMER` remains the only result qualifier.

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tests/left-panel-layout.test.mjs tests/cap-primary-action.test.mjs tests/cap-workflow-view.test.mjs tests/rendered-html.test.mjs`

Expected: PASS. `capResultSummary` states remain distinct.

- [ ] **Step 5: Commit**

```powershell
git add frontend/app/components/CapPlanningPanel.tsx frontend/app/globals.css frontend/tests/left-panel-layout.test.mjs frontend/tests/rendered-html.test.mjs
git commit -m "feat: present CAP results and recommend action before advanced inputs"
```

---

### Task 7: Camera projection-boundary explanation

**Files:**
- Create: `frontend/app/lib/camera-projection-legend.mjs`
- Test: `frontend/tests/camera-projection-legend.test.mjs`
- Modify: `frontend/app/components/EngineeringWorkspace.tsx` Camera pane
- Modify: `frontend/app/globals.css`
- Modify: `frontend/tests/rendered-html.test.mjs`

**Interfaces:**
- Consumes: existing Camera pane geometry summary only. No new geometry fields.
- Produces:

```js
CAMERA_PROJECTION_BOUNDARY_TITLE // "Projection boundary"
CAMERA_PROJECTION_BOUNDARY_EXPLANATION // approved paragraph
```

- [ ] **Step 1: Write the failing test**

Create `frontend/tests/camera-projection-legend.test.mjs`:

```javascript
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  CAMERA_PROJECTION_BOUNDARY_TITLE,
  CAMERA_PROJECTION_BOUNDARY_EXPLANATION,
} from "../app/lib/camera-projection-legend.mjs";

test("camera explanation uses the approved flat-ground meaning", () => {
  assert.equal(CAMERA_PROJECTION_BOUNDARY_TITLE, "Projection boundary");
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /intersection of the camera field-of-view corner rays/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /flat local ground plane/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /pinned camera\/lens FOV/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /mounting height/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /fixture azimuth/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /fixed relative camera azimuth/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /fixed downward tilt/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /Footprint area and overlap are geometric results only/);
  assert.match(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /not detection range, recognition performance, pixel density, terrain\/occlusion analysis, or proof of unobstructed visibility/);
});

test("camera explanation does not claim detection capability or calculated pixel density", () => {
  assert.doesNotMatch(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /detection range is/);
  assert.doesNotMatch(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /pixel density is calculated/);
  assert.doesNotMatch(CAMERA_PROJECTION_BOUNDARY_EXPLANATION, /recognition threshold/);
});

test("Camera pane renders the legend beside existing footprint metrics", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const map = await readFile(new URL("../app/components/EngineeringMap.tsx", import.meta.url), "utf8");
  assert.match(workspace, /CAMERA_PROJECTION_BOUNDARY_EXPLANATION/);
  assert.match(workspace, /geometry-metrics/);
  assert.match(workspace, /valid footprints/);
  assert.doesNotMatch(map, /pixel-density-layer/);
  assert.doesNotMatch(map, /projection-boundary-layer/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/camera-projection-legend.test.mjs`

Expected: FAIL with missing module.

- [ ] **Step 3: Write minimal implementation**

Create `frontend/app/lib/camera-projection-legend.mjs`:

```javascript
export const CAMERA_PROJECTION_BOUNDARY_TITLE = "Projection boundary";

export const CAMERA_PROJECTION_BOUNDARY_EXPLANATION =
  "The displayed boundary is the intersection of the camera field-of-view corner rays with the application's flat local ground plane. It depends on the pinned camera/lens FOV, mounting height, fixture azimuth, fixed relative camera azimuth, and fixed downward tilt. Footprint area and overlap are geometric results only. The boundary is not detection range, recognition performance, pixel density, terrain/occlusion analysis, or proof of unobstructed visibility.";
```

In `EngineeringWorkspace.tsx` add:

```tsx
import { CAMERA_PROJECTION_BOUNDARY_EXPLANATION, CAMERA_PROJECTION_BOUNDARY_TITLE } from "../lib/camera-projection-legend.mjs";
```

Immediately after the Camera pane `geometry-metrics` block, add:

```tsx
<div className="camera-projection-legend" role="note">
  <strong>{CAMERA_PROJECTION_BOUNDARY_TITLE}</strong>
  <p className="helper">{CAMERA_PROJECTION_BOUNDARY_EXPLANATION}</p>
</div>
```

Do not add the legend to invalid footprints as if they were calculated. Existing footprint warnings in the Validation list and inspector remain controlling. Do not change `EngineeringMap.tsx`.

In `frontend/app/globals.css`:

```css
.camera-projection-legend { margin-top: 8px; min-width: 0; }
.camera-projection-legend strong { display: block; color: #d9e2ec; font-size: 10px; }
.camera-projection-legend p { margin: 4px 0 0; }
```

Add to `frontend/tests/rendered-html.test.mjs`:

```javascript
assert.match(workspace, /CAMERA_PROJECTION_BOUNDARY_EXPLANATION/);
assert.match(workspace, /Projection boundary/);
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test tests/camera-projection-legend.test.mjs tests/rendered-html.test.mjs tests/left-panel-layout.test.mjs`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add frontend/app/lib/camera-projection-legend.mjs frontend/tests/camera-projection-legend.test.mjs frontend/app/components/EngineeringWorkspace.tsx frontend/app/globals.css frontend/tests/rendered-html.test.mjs
git commit -m "feat: explain camera projection boundary as flat-ground FOV geometry"
```

---

### Task 8: Frontend regression suite

**Files:**
- Test: existing Stage 2 files listed below. Modify only if a Stage 3 assertion needs to coexist with them.

**Interfaces:**
- Consumes: Tasks 2–7.
- Produces: green frontend typecheck, lint, test, and build on the Stage 3 product tree.

- [ ] **Step 1: Confirm Stage 2 contracts still match**

`frontend/tests/left-panel-layout.test.mjs` must still match the four-discipline switcher, default Lighting, overflow-x hidden, `minmax(0, 1fr)`, and `discipline-pane[hidden]`.

`frontend/tests/lighting-card-position.test.mjs` must still pass WA-05 clamp/offset tests.

`frontend/tests/lighting-labels.test.mjs` must still distinguish `0.00 lx`, `—`, and `<0.01 lx`.

`frontend/tests/polygon-draft.test.mjs` must still pass.

- [ ] **Step 2: Run the full frontend verification**

From `frontend/`:

```powershell
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm run test
corepack pnpm run build
```

From repo root:

```powershell
git diff --check
git diff --exit-code -- Input
```

Expected: all exit 0. `Input/` unchanged. No schema/catalog/lockfile edits. Record commands in `harness/logs/2026-09-16-stage3-p2-usability.md`.

- [ ] **Step 3: Repair ordinary failures**

If lint, types, or tests fail, diagnose and repair in-scope. Do not expand into BL-016 or a shell rewrite. Re-run the failing command after each repair.

- [ ] **Step 4: Commit remaining verification/docs notes if the user asked to commit**

```powershell
git add harness/logs/2026-09-16-stage3-p2-usability.md
git commit -m "docs: record Stage 3 deterministic frontend verification"
```

---

### Task 9: Isolated rendered production verification

**Files:**
- Create: `harness/verify/2026-09-16-stage3-p2-usability-verification.md`

**Interfaces:**
- Consumes: the implementation commit and an isolated production Vinext build plus isolated FastAPI store.
- Produces: PASS/FAIL evidence for the design's rendered matrix. This task does not create a seal or start Independent QA.

- [ ] **Step 1: Build and serve an isolated production UI of this checkout**

Do not reuse leftover UI on `:3000` / `:3012` or API on `:8000` as identity evidence. Import `Input/Miracle_Mile_Lighting_Poles.kml` and confirm SHA-256 `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.

- [ ] **Step 2: Verify BL-013**

Draw and calculate at least two lighting areas. Confirm:

- each row shows **Show results** only as enabled when that area has a current stored result;
- Show results reopens that area's card without a new calculate request;
- switching A → B → A restores independent dragged positions and keeps only one card visible;
- create then cancel a new polygon draft does not delete stored results or the other area's session position;
- delete removes that area's session and closes its card if it was active;
- stale/unavailable copy appears after the existing invalidation workflow, never as a current-result card.

- [ ] **Step 3: Verify BL-014**

On the CAP pane confirm:

- not-calculated / error / current / current-with-unresolved / zero selected sites are distinct;
- blockers appear before a valid recommend operation and Review input still focuses the existing field/section ids;
- required inputs and candidates remain present and expandable;
- the primary button is **Calculate CAP recommendation**, stays disabled when `recommend` is ineligible, and calls the existing recommend path when enabled;
- Calculate / rank and Validate remain available as secondary actions where Phase 6 already permits them;
- after a result, count, selected identities, Locate, Show selected sites on map, unresolved warning, and `CAP_DISCLAIMER` agree with the stored result.

- [ ] **Step 4: Verify BL-015 and Stage 2 regressions**

On the Camera pane confirm the approved projection-boundary paragraph sits beside the existing FOV/footprint summary. Invalid footprints still show existing warnings. No new map layer appears.

At 1920 px and 1024 px: no left-panel horizontal overflow, collapse rail still works, and switching Lighting/Camera/Wi-Fi/CAP preserves an active polygon draft. Browser console has no new errors attributable to Stage 3.

- [ ] **Step 5: Write the verification summary**

Use `harness/templates/verification-summary-template.md`. Record PASS only for checks actually run against this checkout. Independent QA and scoped master remain later gates. No phase seal.

---

## Independent QA launch prompt (do not run until implementation is handed off)

```text
Independently review authorized Stage 3 items BL-013, BL-014, and BL-015 only.

Create and activate a durable goal: complete independent QA of those three
items on the recorded implementation commit. Continue until
harness/verify/2026-09-16-stage3-p2-usability-independent-qa-review.md
records a supported PASS or FAIL for all three. Do not implement product
fixes. Do not merge, push, start BL-016, or create a seal.

Read AGENTS.md and its startup sequence, then:
- docs/superpowers/plans/2026-09-16-stage3-p2-usability.md
- docs/superpowers/specs/2026-09-16-stage3-p2-usability-design.md
- docs/web-app-review-2026-09-08.md WA-06, WA-07, WA-08
- the implementation work record and verification summary
- exact git status, HEAD, and diff

Live checks must use an isolated production Vinext build of THIS checkout
and an isolated FastAPI project store. Miracle Mile SHA-256 must be
2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328.

Re-run from frontend/:
  corepack pnpm run typecheck
  corepack pnpm run lint
  corepack pnpm run test
  corepack pnpm run build
Also: git diff --exit-code -- Input
```

## Proven-blocker rule

Ordinary failures are repaired in-session. Stop and ask only when the same condition still blocks after three materially different safe recoveries and needs new authority, a product decision, an external-state change, or a prohibited scope expansion.
