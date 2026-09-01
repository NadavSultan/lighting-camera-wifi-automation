# Phase 6 production-rendered QA — 2026-09-01

Status: in progress; this is current rendered evidence, not a completion report or a phase gate.

## Environment

- Application commit under test: `35b20244`.
- Backend: bundled Python Uvicorn at `http://127.0.0.1:8026`, isolated `LCWA_DATA_DIR` under the local temporary directory.
- Frontend: production Vinext server at `http://127.0.0.1:3026` after a successful production build.
- Browser: Codex in-app browser, production page only.

## Current evidence

1. Imported `Input/Miracle_Mile_Lighting_Poles.kml` through the production UI. The UI reported `74 source poles`, `EPSG:32617`, preserved WGS84 source coordinates, and the original source coordinate for the selected pole.
2. Before test-only input, the CAP panel visibly preserved the full unknown-state blocker list and disabled planning controls.
3. Entered conspicuously test-only product, variant, band/jurisdiction, distance, node/child/hop limits, counting conventions, redundancy policy, and node dispositions through UI controls. These are test fixtures only, not Miracle Mile approvals.
4. Added an existing-pole CAP candidate through the UI, then explicitly marked it test-only feasible. The preflight became complete.
5. Explicitly changed the selected source pole to a test-only WIFI fixture through the production inspector, then ran `Calculate / rank` through the UI. The UI showed `1 explicit CAP candidate sites · 1 selected`, `73` LITE and `1` WIFI fixture, the CAP topology/provenance panel, and `CAP calculate completed as conceptual graph planning`. It retained the graph-only disclaimer: “Distance-qualified conceptual link; not RF-predicted. Graph-and-constraint planning only; not coverage, capacity, performance, service quality, installation feasibility, or compliance.”
6. Browser console query returned zero error entries.
7. Switched the production UI to Validate mode and `validate_only`, locked the explicit candidate, and ran `Validate`; the UI reported `CAP validate completed as conceptual graph planning` with zero console errors.
8. Added a distinct manual non-pole CAP site through the UI using test-only coordinates, marked it test-only feasible, applied preference and selected-CAP lock controls, then revalidated successfully. The manual site remained visibly separate from the customer-pole UI.
9. Used the UI Save Project, Undo, and Redo controls after CAP changes; Undo was enabled and the redo action completed. Console errors remained zero.

## Remaining required rendered evidence

- production reopen of the saved project and an explicit source-hash check;
- exercise prohibition and visible CAP layers/colors/symbol distinction through the production workflow;
- production KML export exclusion;
- capture all required prompt section-7 steps and final console check on the final implementation commit.
