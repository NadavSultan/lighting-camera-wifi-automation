# BL-016 QA03-IA-01 scoped implementation verification — 2026-09-29

Implementation commit: `5656da555f9614a2be614738ccf699ce2d58f609` (detached worktree). Starting clean commit: `8cc7170fce880e9aff78d3558e4f9a8b647ba61b`. This verifies only overlap inspection correction under `BL016-16`/`QA03-IA-01`; BL-016 remains unaccepted and prior Independent QA FAIL remains intact.

## Diagnosis, repair, and failing-first coverage

MapLibre exposed nested overlap contributor IDs as a serialized JSON property, which the old array-only inspector ignored. The map also registered eleven delegated click handlers for layered density hits; a single pointer event could produce several popups. The fix parses either array or serialized overlap IDs, uses a full transparent overlap hit polygon, queries all density layers through one click handler, selects the stored overlap winner and complete contributors, derives the displayed interval from the winning camera's persisted band, and replaces any prior popup. The production screenshot exposed light-on-white text and overflow, then caption collision; the final popup is dark-on-white, bounded, scrollable, and visibly below the caption at the test point.

Focused tests failed before each correction: the original overlap tests produced three then four failures; the readability helper test failed 7/8 before implementation; the caption-clearance expectation failed 7/8 before height adjustment. All focused tests finished GREEN 8/8, with complete full frontend tests below. Product edits are only the original four authorized frontend files across three scoped commits (`86cc838a`, `57287255`, `5656da55`).

## Current deterministic checks on final implementation commit

| Exact command/action | Result | Warnings or limit |
|---|---|---|
| `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` (cwd `backend`) | exit 0, 364 tests | Starlette/httpx and AnyIO deprecations |
| `.\.venv\Scripts\python.exe scripts\validate_engineering_data.py` (root) | exit 0, eight catalogs/source hashes valid | none |
| `corepack pnpm install --frozen-lockfile` (cwd `frontend`) | exit 0, lockfile unchanged | supply-chain policy metadata 23 days old |
| `corepack pnpm run test` / `typecheck` / `lint` (cwd `frontend`) | exit 0 each, 112/112 tests, no type/lint errors | none |
| `..\.venv\Scripts\python.exe -m scripts.export_schema` (cwd `backend`); `git diff --exit-code 5656da55 -- schemas` (root) | exit 0, generated schemas byte-fresh | none |
| `corepack pnpm run build` with `NEXT_PUBLIC_API_URL=:8070` and all five approved EOX public Satellite variables set first (cwd `frontend`) | exit 0; integrated configured bundle test 1/1 | plugin timing, >500 KB chunk, Vinext dynamic-route classification advisories |
| `git diff --exit-code 5656da55 -- Input frontend/pnpm-lock.yaml`; `Get-FileHash Input/Miracle_Mile_Lighting_Poles.kml -Algorithm SHA256`; `git diff --check` (root) | exit 0; source SHA `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328` | no source/lockfile diff |
| `.\.venv\Scripts\python.exe harness\verify\run_bl016_camera_pixel_density_live.py --output harness/verify/2026-09-29-bl-016-qa03-ia01-base-live.json` (root) | exit 0, 12/12 assertions, head exactly `5656da55` | Chrome headless shell and API regression, not the focused interactive overlap test |

The exact live-harness output is `harness/verify/2026-09-29-bl-016-qa03-ia01-base-live.json`. Its expected invalid-input request returned 422 while the project stayed unchanged; no browser console/page errors or harness warnings were reported. Intermediate commit gates are historical and do not substitute for the final-commit checks above.

## Production browser and canonical overlap

`harness/verify/2026-09-29-bl-016-qa03-ia01-browser.json` records a fresh configured production Vinext/FastAPI instance, unchanged 74-pole KML upload, all 74 poles set to Phoenix 1 SMART/10 m/IMX477/JL-LN037, 148 camera results and 4,233 overlap regions. One click at `[620,370]` on Standard and another after selecting Satellite each yielded exactly one 7× popup. Both displayed `px-face-15`/15–20 px/face, winner `pole-f80ddce879ccf3d1/camera-2`, all seven stored contributors, freshness, and the geometric-density disclaimer. The complete contributor set/winner/band matched exactly one persisted region, `density-overlap-65b588cac503a8918fa5bce4`.

The final screenshot and computed style showed text RGB 23/33/44 on white, popup top 150 px below caption bottom 141.5 px and inside map bounds; its 300 px content is scrollable within 180 px, and scrolling reached the remaining contributors/disclaimer. Browser warning/error log was empty. Screenshots were inspected inline but not persisted as files. This is an implementation smoke; independent QA must still re-run its full interactive workflow.

## Boundary and gate

Only `frontend/app/components/EngineeringMap.tsx`, `frontend/app/lib/camera-pixel-density-map.mjs`, its `.d.mts`, and `frontend/tests/camera-pixel-density-map.test.mjs` changed as product code. Evidence-only records are under `harness/`. Input, frozen catalogs, backend geometry/calculation, generated schemas, lockfile, Satellite implementation, and the separate QA worktree were not edited. Independent QA is still FAIL on its last report; master gate pending; no phase seal, merge, push, acceptance, or later-phase authorization is claimed.
