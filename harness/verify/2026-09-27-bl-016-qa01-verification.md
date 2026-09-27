# BL-016 QA-01 corrective verification — 2026-09-27

Corrective implementation: `f542b164c136e8224e55867ea3f016a6987f7a44`. This record covers the narrow production-browser API seam. The Independent QA report dated 2026-09-27 remains **FAIL** at `b237d9dceddd44005d42dab32935bda1f6eddd9d`; a new independent review is required. BL-016 is unaccepted.

## Cause and correction

The reviewer observed `Failed to fetch` at UI `http://127.0.0.1:3070`. The then-current backend regex already admitted that origin, so the report's CORS-only attribution was incomplete. It also admitted unrelated local ports. The existing compiled production client instead embedded API `http://127.0.0.1:8000`, while the isolated backend used `:8070`; setting `NEXT_PUBLIC_API_URL` only when starting Vinext did not change the compiled client. Commit `f542b164` replaces the broad regex with the existing two `:3000` development origins plus exact `http://127.0.0.1:3070`, and adds preflight/actual-response regression coverage including rejection of unrelated `:3071`. The production build set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8070` **before compilation**. The live runner now verifies that the compiled client contains this target before starting servers.

## Current checks on corrective implementation

All commands below ran on product commit `f542b164` with only corrective evidence edits uncommitted. Full exact commands, failed attempts, and warnings are in `harness/logs/2026-09-27-bl-016-qa01-cors.md`.

- `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` from `backend/`: exit 0, full suite passed, including four CORS cases. Two dependency deprecation warnings (Starlette/httpx, anyio). A prior root-cwd invocation had 12 import collection errors; no tests ran in that attempt.
- `.\.venv\Scripts\python.exe scripts\validate_engineering_data.py`: exit 0, eight catalogs and supplied-source hashes valid.
- `..\.venv\Scripts\python.exe -m scripts.export_schema` from `backend/`: exit 0, five generated contracts; `git diff --exit-code -- schemas`: exit 0.
- From `frontend/`: `corepack pnpm install --frozen-lockfile`, `corepack pnpm run test`, `corepack pnpm run typecheck`, `corepack pnpm run lint`, and `$env:NEXT_PUBLIC_API_URL='http://127.0.0.1:8070'; corepack pnpm run build`: each exit 0; 107/107 tests. Non-failing lock policy age, large chunk and dynamic-route advisories. The client and SSR chunks contain `http://127.0.0.1:8070`.
- `git diff --exit-code -- Input`: exit 0. `Get-FileHash Input\Miracle_Mile_Lighting_Poles.kml -Algorithm SHA256`: `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`.
- `git diff --check`: exit 0; Git reported only that LF in the edited live runner will become CRLF when touched. Final staged whitespace and clean-tree checks are required before handoff.

The first live run and retry02 each encountered a transient 3070 bind collision before server launch and are preserved as separate JSON files. Retry01 passed before the runner bundle check; retry03 passed after it, with all 12 API/shell assertions true, 8 valid cameras, 30 overlap regions, and `production_client_api_target.api_url` equal to `http://127.0.0.1:8070`. The live runner's headless browser covers the production shell only; its engineering assertions use direct API requests. See `harness/verify/2026-09-27-bl016-qa01-live-retry03.json`.

## Real production-browser smoke

The supervised Codex browser opened the production UI at `:3070`, uploaded the supplied KML through its file chooser, and showed `Miracle_Mile_Lighting_Poles.kml · 74 source poles`, LITE 74, WIFI 0, SMART 0, source CRS EPSG:4326, projected CRS EPSG:32617, and the import success message. The Camera pane opened with 0.5 / 2.0 / AUTO 1.25 / 50.0 defaults and a not-calculated state. Browser warning/error logs were empty. The isolated backend log records browser-session `OPTIONS /api/projects/import` 200 and `POST /api/projects/import` 201, plus successful browser preflight/POST pairs for report preview, fixture direction preview, and camera geometry recalculation. See `harness/verify/2026-09-27-bl-016-qa01-browser-smoke.json`. The browser tab and temporary servers were closed; no screenshot artifact was retained.

## Acceptance boundary

The original BL016-01–13 and BL016-18–19 deterministic/API evidence was rerun through the current full suites and live assertions, but prior Independent QA conclusions remain historical. QA-01's browser integration is corrected and directly observed. For BL016-14–17 and BL016-20, this smoke proves import, API access, project state, Camera pane entry, and profile defaults only. An independent reviewer must still exercise all three lenses, invalid-camera isolation, standard and satellite maps, band transparency, overlap labels and point inspection, interactive stale/save/reopen/recalculation, controlled UI failure, and prior-layer/export regressions. No full interactive acceptance or master decision is claimed.

No `Input/` bytes, customer pole coordinates, catalogs, source uploads, runtime projects, or generated contracts changed. No merge, push, later backlog work, or seal was performed.
