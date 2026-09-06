# Backlog live reproduction — 2026-09-06

Scope: user-authorized diagnosis of BL-002, BL-003, BL-006 and BL-008. No implementation, contract amendment, phase acceptance, or production regression claim.

Repository: nested clean-main baseline `8751714003bf09f39c217a5f26b9fd6056d2927b`. Starting diff: untracked `docs/post-roadmap-backlog.md` only. The parent checkout's unrelated work was preserved.

## Environment and isolation

- Windows, Python 3.12.10 from repository `.venv`, Node v24.19.0, existing locked frontend dependencies, real Chrome browser through the connected browser tool.
- API: `http://127.0.0.1:8048`; development frontend: `http://localhost:3048/`.
- Isolated project and catalog roots: `harness/tmp/backlog-repro-2026-09-06/projects` and `catalogs`. Frontend used copies of tracked frontend files under the same ignored test directory, with a dependency junction to the existing installation. No app-source edits were made.
- This was a genuine browser walkthrough of a development instance, not a production build. Browser accessibility observations and screenshots were inspected in the session.
- Test project: `dd3d8dfb-3405-4a43-aa50-132a3105b36c`, imported from the supplied 74-pole KML. One pole, Cobra Head 7 (`pole-443127e3a723e1b3`), was configured as Phoenix 1 WIFI in isolated test state.
- API-backed facts and preservation assertions: [observations JSON](2026-09-06-backlog-reproduction-observations.json).

## Setup commands and recovery

Executed from the nested repository unless otherwise stated:

1. `git status --short --branch`, `git rev-parse HEAD`: main baseline confirmed; backlog document was the only initial untracked change.
2. `.venv/Scripts/python.exe --version`, `node --version`: successful; versions above. Dependency directory and virtual environment were present.
3. In `backend`, set `LCWA_DATA_DIR` and `LCWA_CATALOG_DIR` to the isolated roots, then run `../.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8048`. Startup succeeded, process 37516, tool session 99210.
4. In normal `frontend`, set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8048`, then run `node node_modules/vinext/dist/cli.js dev --host 127.0.0.1 --port 3048`. Exit 1: Vinext reported an existing dev server, PID 3712. It was not stopped or altered.
5. Copied each `git ls-files frontend` path into `harness/tmp/backlog-repro-2026-09-06/frontend`, preserving its relative path, and created a node_modules junction. Ran the same frontend command there, session 66349. Startup succeeded at the reported `http://localhost:3048/`. Inspector-port 9229 was occupied; Vinext selected 9230. Dependency re-optimization messages were emitted.
6. Initial browser requests to `127.0.0.1:3048` were refused; navigation to the server-reported `localhost:3048` succeeded. No firewall or other security setting was changed.
7. One browser selector using uppercase `FIXTURE MODEL` did not match. After inspecting the page again, the observed `#fixture-model` selector worked. The user continuation arrived during the walkthrough; the ephemeral test tab was gone, so a new isolated test tab was opened. Catalog persistence was subsequently verified in that fresh tab.

These recoveries are environment/tool observations, not product bug findings.

## BL-003 — early polygon feedback defect reproduced

1. Import the supplied KML through Import KML/KMZ.
2. Click Draw Calculation Area with the map and both sidebars visible.
3. Click three map positions in turn (observed viewport coordinates approximately `(690,420)`, `(900,420)`, `(900,530)`).
4. After each click, inspect the vertex count and screenshot.

Observed: the count progressed 0 → 1 → 2 → 3. The first point had no visible vertex marker; two points had no visible connecting segment. At three points a faint teal triangular fill appeared. Drawing controls and next-step guidance were below the visible portion of the long left sidebar. The draft was cancelled without saving.

Source correlation: `EngineeringMap.tsx` `draftFeature` returns no geometry below two points, a LineString at two, and a Polygon from three; draft sources have fill-only map layers. This explains the reproduced missing early-stage feedback.

Disposition: classify BL-003 as a confirmed drawing-feedback bug, retaining the independently testable styling/guidance acceptance criteria. Lighting drawing was reproduced live; camera-priority and Wi-Fi drawing still need corresponding checks before a fix is verified across all tools. No fix was attempted.

## BL-002 — coverage exists; explicit display step is easy to miss

1. Select Phoenix 1 WIFI for Cobra Head 7; inherit the 30 m test radius.
2. Click Calculate conceptual Wi-Fi.
3. Observe status “Calculated 1 conceptual Wi-Fi circles” and sidebar area `2826.298041 m²`.
4. Observe Conceptual Wi-Fi remains unchecked and the map has no cyan coverage circle.
5. Enable the Conceptual Wi-Fi checkbox and inspect the settled screenshot.

Observed: a cyan circle appeared around the yellow WIFI fixture once enabled, with no analysis polygon. This follows the accepted explicit-toggle rule. No missing-geometry failure was reproduced in this case. The checkbox resides far down the sidebar and calculation does not direct the user to it.

Disposition: usability improvement confirmed for this scenario. Do not claim to have disproved failures with other project states or large layouts. Automatically enabling the layer would still require an explicit Phase 5 contract decision.

## BL-006 — simultaneous associations succeed

1. Open Catalogs → Upload IES and upload supplied `JLED-SL-100W-PHOENIX1-40-D01.ies` into the isolated catalog.
2. Select that file and Phoenix 1 LITE, click Associate.
3. Select Phoenix 1 WIFI and click Associate; repeat for Phoenix 1 SMART.
4. Read `GET /api/catalogs/ies` and later reopen Catalogs in a fresh browser tab.
5. Inspect each compatible model selection; Remove association is enabled for the retained pairs.

Observed: the API returned three active associations for the same `ies-4a897fb04b6d8f6c` file. The fresh catalog showed the retained LITE association and explicit WIFI/SMART selection checks also confirmed theirs. The UI exposes one pair at a time and no per-file overview of all three assignments.

Disposition: usability improvement; no one-type restriction or loss-of-association bug reproduced. This test covers the supplied Phoenix 100 W file and its compatible family only. If the user's failure persists, the exact IES file, target model names, and displayed error are the next evidence needed. Do not relax approved family restrictions.

## BL-008 — recommendation executes, but count/sites are not prominent

Fresh import observation: Recommend CAP and the three sidebar actions were disabled, with a dense raw-name list of missing prerequisites. No real-site values were filled to bypass these gates.

For the successful-path test, a test-only JSON copy of the isolated project was prepared using the profile from `backend/tests/test_phase6_cap_planning.py::project_with_test_only_inputs`. It retained all 74 original source poles, with only the one WIFI fixture participating. The sole test candidate `repro-cap-one` referenced that existing pole. Profile and feasibility provenance explicitly identify test-only assumptions. The project name was `TEST ONLY - backlog CAP reproduction - not site design`. This is not approval of Miracle Mile operational inputs or a site design.

1. Open that JSON through Open Project.
2. Verify “Preflight complete for the selected test/project inputs” and enabled Recommend CAP.
3. Click Recommend CAP in the toolbar.
4. Observe “CAP recommend completed as conceptual graph planning”.
5. Locate the sidebar count “1 explicit CAP candidate sites · 1 selected.”
6. Enable CAP candidate / selected sites and CAP conceptual tree links; inspect the green selected-site marker at the existing test pole.

Observed: recommendation returned `status=calculated`, selected IDs `[repro-cap-one]`. The count is below the lengthy configuration form; topology is collapsed. CAP map layers remained off following recommendation until explicitly enabled. With the sites layer on, the green site marker appeared. The engine is present and executes; the workflow does not bring the count or selected locations prominently into view.

Disposition: usability improvement confirmed. A single-candidate example verifies the control/result path only, not capacity, optimality, multiple-site selection or all CAP branches.

### Separate diagnostic observation OBS-01

The current development browser emitted five React duplicate-key errors after the CAP recommendation and layer actions, all naming the warning `Single-CAP conceptual plan; single point of failure is not mitigated by this graph result.` Observed timestamps were 14:45:27.055Z and 14:45:50.642Z/.784Z/.909Z/.963Z on 2026-09-06.

No missing warning or erroneous CAP selection was established from this observation. Keep it separate from BL-008's usability objective: a focused diagnostic task should identify the affected rendered warning list and reproduce any user-visible effect before classifying or implementing a correction. No new work item is authorized by this finding; no zero-console-error claim is made.

## Preservation and limits

A read-only API/fixture assertion script exited 0 and wrote the linked observations JSON. It verified 74 source poles, unchanged source collection against the pre-CAP test snapshot, byte equality of the archived KML and the supplied KML, three active IES associations, and the expected selected test candidate.

Source SHA-256: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`. IES SHA-256: `4a897fb04b6d8f6c75c94a3ceba473391021aee6d506f05357f48bc01d26d363`.

The profile-setup helper emitted the existing Starlette/httpx deprecation warning. No full regression suite, production build, phase readiness verifier, or independent QA was run. Findings are diagnostic evidence only. The test runtime data remain under ignored `harness/tmp`; only backlog/evidence documents are deliverables.

Cleanup: sent Ctrl+C to the two agent-created server sessions (66349 and 99210); both exited with termination status 1. The pre-existing development server was not stopped. Final protected product/source/gate diff was empty; only the backlog and two diagnostic evidence files were untracked. Diagnostic Markdown whitespace and observations JSON parsing checks passed.
