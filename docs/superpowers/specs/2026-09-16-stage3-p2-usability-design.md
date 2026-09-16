# Stage 3 P2 Usability Design

Date: 2026-09-16

Status: approved design; implementation remains separately gated

## Purpose and authority

Stage 3 is a post-roadmap, item-based usability stage. It does not create Phase 8 or reopen Phases 1–7. The user approved this design on 2026-09-16 after Stage 2 received Independent QA PASS and scoped master PASS.

Stage 3 contains exactly:

- BL-013 / WA-06 — revisit stored lighting results across multiple calculation areas;
- BL-014 / WA-07 — present the CAP result and primary action before advanced configuration;
- BL-015 / WA-08 — explain the camera footprint/projection boundary.

The controlling intake is `docs/web-app-review-2026-09-08.md`. Repository invariants and accepted calculation behavior remain controlled by `AGENTS.md`, the Phase 3, Phase 4, and Phase 6 records, and the current execution indexes.

## Non-goals

- No BL-016 camera pixel-density calculation, heat map, thresholds, recognition claim, or measurement-surface decision.
- No BL-019 or BL-020 correction.
- No multiple simultaneously pinned lighting-result cards.
- No persistence of card position or panel layout in project JSON.
- No lighting, camera, or CAP engine changes.
- No schemas, migrations, API contracts, catalogs, lockfiles, `Input/`, source poles, or saved engineering values changes.
- No invented CAP defaults, candidate locations, node policies, limits, feasibility, RF performance, or installation claims.
- No broad workspace or three-column shell redesign.
- No merge, push, Phase 8, or harness seal.

## Architecture and boundaries

Stage 3 is a frontend-only presentation change built on the current Stage 2 discipline switcher and existing persisted results.

- `EngineeringWorkspace.tsx` continues to own the active lighting area, the single open lighting-result card, and session-only per-area card positions.
- `LightingResultCard.tsx` continues to render one selected area result and its current/stale state. Stage 3 does not create a multi-window manager.
- `CapPlanningPanel.tsx` is reorganized around an outcome-first summary and one context-sensitive primary action. It continues to call the existing `runCap` operations and existing Phase 6 eligibility helpers.
- Camera explanatory content is placed in the Camera discipline UI and/or SMART camera inspector beside the existing footprint controls and metrics. It consumes existing geometry state only.
- Small pure presentation helpers may be added under `frontend/app/lib/` when they make state labels or action selection deterministic and directly testable.

No backend interface changes are expected or authorized.

## BL-013 — revisit lighting results

### User behavior

Each calculation-area row exposes a clear **Show results** action when a stored current result is available. Selecting it:

1. selects the calculation area;
2. opens that area's result card without recalculation;
3. restores that area's session-only dragged position when one exists;
4. otherwise anchors the card beside the area's final polygon vertex using the accepted Stage 2 positioning behavior.

Only one result card is open at a time. Opening another area's result replaces the visible card but does not delete, recalculate, or mutate either stored result.

The area row must distinguish these states without weakening existing invalidation rules:

- **Current result** — Show results is enabled.
- **Stale result** — displayed as stale/unavailable; it must not be presented as current and must require recalculation through the existing workflow.
- **Not calculated** — no result card can be opened.

Creating or cancelling a polygon draft must not delete stored results, clear another area's session position, or silently recalculate. Editing, deleting, or recalculating an area continues to use existing Phase 4 invalidation and lifecycle behavior. Deleting an area removes its session-only card state and closes its card if it was active.

### State model

The existing `lightingCardAreaId` remains the single visible-card identity. The existing area-keyed session map remains the owner of anchor and dragged position. Stage 3 may add a pure helper that derives the row state and action availability from the calculation area plus its stored result; it must not modify the `Project` object.

## BL-014 — result-first CAP workflow

### User behavior

The CAP pane presents information in this order:

1. current result or explicit “not calculated” state;
2. a primary next action;
3. blockers or unresolved-node guidance;
4. selected CAP count/sites and map actions when a result exists;
5. expandable required inputs, candidates/locks, secondary operations, and topology/provenance.

The primary action label is **Calculate CAP recommendation** when the existing project state and approved mode allow recommendation from the approved candidate pool. It calls the existing `recommend` operation and is enabled only when the existing Phase 6 preflight permits it.

When recommendation is not allowed, the panel must not fake availability. It shows concise blocker guidance and links or focuses the relevant existing input. Existing **Calculate / rank** and **Validate** operations remain available as clearly labelled secondary actions where the accepted Phase 6 rules permit them.

After a successful result, the top summary shows:

- recommended CAP unit count;
- selected candidate names/identities;
- unresolved-node count and warning when applicable;
- **Locate** and **Show selected sites on map** actions;
- the permanent Phase 6 conceptual graph disclaimer.

### Safety constraints

The reorganization must not:

- bypass `capOperationEnabled` or `capBlockers`;
- change node/candidate selection, scoring, validation, or recommendation semantics;
- auto-populate unknown inputs;
- convert test-only values into defaults;
- generate unrestricted candidate coordinates;
- hide required inputs or provenance;
- describe results as RF coverage, capacity, performance, installation feasibility, or compliance.

Required inputs and candidates remain editable in expandable advanced sections. Missing prerequisites produce specific guidance rather than a number.

## BL-015 — camera projection-boundary explanation

The Camera discipline presents a short help/legend adjacent to the existing camera layers or geometry summary. The exact approved meaning is:

- the displayed boundary is the intersection of the camera field-of-view corner rays with the application's flat local ground plane;
- it depends on the pinned camera/lens FOV, mounting height, fixture azimuth, fixed relative camera azimuth, and fixed downward tilt;
- footprint area and overlap are geometric results only;
- the boundary is not detection range, recognition performance, pixel density, terrain/occlusion analysis, or proof of unobstructed visibility.

When camera geometry is unavailable, the existing warnings remain controlling; the explanation must not turn an invalid or missing footprint into a calculated result. No new map layer or stored field is introduced.

## Error and edge-state handling

- A missing project keeps the existing create/import guidance.
- Missing or stale lighting results never produce a current-result card.
- A CAP error remains visually distinct from not-calculated and from current-with-unresolved.
- Zero selected CAP sites is shown as an explicit result, not hidden or treated as an exception.
- Missing CAP prerequisites retain their exact blocker identities and review-input focus behavior.
- Invalid or warning-bearing camera footprints continue to display existing warnings; the explanatory legend remains general and does not override them.
- Switching Lighting/Camera/Wi-Fi/CAP disciplines must preserve an active polygon draft as required by Stage 2.

## Verification design

### Deterministic frontend checks

Add focused tests proving:

- the lighting-area state helper distinguishes current, stale, and not-calculated;
- Show results opens the selected stored result without invoking calculation;
- switching between at least two areas restores their independent session positions while keeping only one card visible;
- draft creation/cancellation does not discard stored results or session positions;
- deletion removes the deleted area's session state;
- the CAP primary action is selected from existing eligibility, never bypasses blockers, and calls the existing operation;
- result-first CAP content appears before advanced inputs while required inputs/candidates remain present and expandable;
- zero selected sites, unresolved nodes, error, and not-calculated states remain distinct;
- the camera explanation contains the approved flat-ground and non-performance limitations and does not claim pixel density or detection capability;
- existing Stage 2 discipline-switcher, overflow, card positioning, lux formatting, and draft-preservation tests remain green.

Run from `frontend/`:

```powershell
corepack pnpm run typecheck
corepack pnpm run lint
corepack pnpm run test
corepack pnpm run build
```

Also run from the repository root:

```powershell
git diff --check
git diff --exit-code -- Input
```

### Rendered production verification

Use an isolated production frontend built from the tested checkout and an isolated FastAPI store. Import the 74-pole Miracle Mile KML and confirm its SHA-256 remains `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.

Verify:

- two or more calculation areas can be calculated, revisited without recalculation, switched repeatedly, dragged independently, and reopened at their session positions;
- create/cancel draft, edit, delete, and recalculate transitions show the correct result state;
- the CAP pane shows blockers before a valid operation, exposes all required inputs/candidates, executes the existing eligible recommendation path, and displays count/sites/unresolved/map actions consistently with the stored result;
- the Camera pane exposes the approved explanation beside the existing FOV/footprint presentation;
- 1920 px and 1024 px layouts have no horizontal overflow, the collapse rail works, and discipline switching preserves active drafts;
- the browser console contains no new errors attributable to Stage 3.

## Acceptance

Stage 3 is implementation-ready only when an execution plan maps BL-013, BL-014, and BL-015 to independent milestones, exact changed paths, focused automated checks, and the rendered matrix above. Implementation completion will require an implementation commit, clean worktree, evidence record, independent QA, and a later scoped master decision. No phase seal is used for this post-roadmap item stage.
