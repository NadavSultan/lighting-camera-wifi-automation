# Camera range preview, lens details, and map distance measurement

Date: 2026-10-04

Status: design for user review; implementation not yet authorized by this document

Base: `codex/bl016-heatmap-correction` at `47f4e1805b08e04ef22e02dc73a424d9408bd8d4`

## Intent and boundaries

The engineer should see the requested camera preview distance together with the pixel-density heat map, verify which pinned lens is actually assigned to each camera slot, and measure a straight-line map distance. This is a post-roadmap user-requested UX correction, not a new calculation engine or a revision of accepted Phase 3 geometry.

The stored `camera_geometry` footprints, overlap metrics, provenance, and Phase 3 calculation remain unchanged. BL-016 pixel density keeps its approved maximum-contributor overlap rule, 0.16 m reference face, fixed legend, and informational disclaimer. Customer poles and immutable input files remain unchanged.

## Camera range preview

The existing project-level **Maximum visible distance (m)** in the Camera pixel-density panel is the only range control. Its default remains 50 m. Changing it makes the density result stale under the existing fingerprint rules; pressing the existing **Calculate camera density** action refreshes both the distance-limited preview and the heat map. No second range setting or calculate button is introduced.

The map's primary Camera view no longer displays the uncapped Phase 3 ground-FOV fills or their broad raw-overlap fill. Their stored data and metrics remain available for existing workflows and reports. The **Camera pixel density** layer instead displays each valid camera's existing BL-016 `projection_envelope` as a subdued, distance-capped preview, with the continuous pixel-density raster over it. The preview envelope remains visible where the density is below the first 2 px/face legend threshold; those locations do not acquire a fabricated density color. The static color legend, bounded-density overlap treatment, multiplicity labels, and click inspection retain their current meanings.

When density is hidden, stale, invalid, or not calculated, neither its heat map nor its bounded preview is shown. The UI explains that the user must calculate or recalculate. Range control affects presentation through the BL-016 derived result; it does not clip or rewrite Phase 3 persisted geometry or alter Phase 3 overlap metrics. The map must never show an uncapped fill as though it were within the requested range.

## Lens and camera specification display

For each selected pole's camera slot, the Properties inspector shows a read-only specification card resolved from the slot's **pinned** camera and lens revisions: camera and lens names/IDs, revisions, focal length in millimetres, horizontal and vertical FOV in degrees, and camera resolution in pixels. The existing selector remains the only way to change a lens. Current catalog values must not silently replace pinned historical revision values. An unassigned, incompatible, or unavailable lens is called out explicitly rather than showing guessed specifications. No catalog record, assignment, or project schema is changed merely by viewing the card.

## Two-click distance tool

A single **Measure distance** control sits at the lower-left of the map, clear of MapLibre attribution and existing controls. Activating it starts an exclusive map interaction: the first click marks a start point; the second marks the end point, draws one straight line, and labels its distance in metres. Distance is calculated from the two WGS84 click coordinates in the project's selected projected CRS via the backend's PyProj authority, not from screen pixels or an unapproved browser approximation. The result is session-only UI state and is not written into the project, exports, or calculation layers.

After a completed measurement, the same control offers **Clear measurement**; using it removes the line and result and allows a new measurement. Esc cancels an unfinished measurement. Starting another polygon-drawing workflow and measuring at the same time is disallowed; map clicks in measure mode must not select poles, edit azimuth, or add area vertices. Invalid coordinates, an unavailable projected CRS, or a failed distance request produce a visible error and no fabricated distance. Source coordinates and pole positions never move.

## Component and data flow

- Reuse the current BL-016 density result and its distance-clipped projection envelopes in `EngineeringMap`; keep backend-owned geometry authoritative.
- Update Camera layer controls in `EngineeringWorkspace` so the bounded density preview is the primary camera visualization, without presenting raw uncapped FOV as the default.
- Resolve lens/card data from pinned catalog revisions already used for per-pole camera configuration; render it in `PoleInspector` without editable specification copies.
- Add a small read-only distance endpoint/service that transforms both clicked WGS84 points to the selected project CRS and returns Euclidean distance in metres; keep the line, points, and interaction state in the frontend only.
- Keep existing OpenAPI generation and backend/frontend validation commands as the verification baseline. An endpoint addition updates OpenAPI but does not by itself require a persisted project-schema migration.

## Verification and acceptance

Automated tests cover 50 m default and changed-range preview bounds, stale/recalculate and hide/show behavior, no raw FOV/overlap fills in the primary Camera view, unchanged Phase 3 geometry/metrics, unchanged highest-contributor density semantics, pinned historical lens details, and two-click projected-distance accuracy and non-persistence. Frontend tests cover measurement start/end/clear/Esc, conflict with area drawing and pole selection, and responsive lower-left placement. Run the full backend and frontend tests, engineering-data validator, schema exporter/freshness, typecheck, lint, and production build.

Rendered QA uses the preserved 74-pole Miracle Mile KML on the production app: verify range 50 m and one shorter/longer requested value, preview plus heat colors, no uncapped background fill, selected lens details for both slots, a known-distance two-click measurement, clear/cancel, save/reopen without measurement persistence, and zero browser console errors. Verify the supplied KML hash and `Input/` diff remain unchanged. Independent QA and a scoped master decision are separate from implementation readiness.

## Non-goals

No edit to Phase 3 FOV calculations or overlap metrics; no new camera/lens defaults or automatic selection; no per-camera distance setting; no detection/recognition/visibility claim; no terrain or occlusion model; no multi-segment route measurement; no measurement persistence; no customer-pole movement; no Phase 8 or phase seal.
