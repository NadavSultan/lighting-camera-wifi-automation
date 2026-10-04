# Independent QA execution log — 2026-10-04

Scope: product `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`, evidence tip before QA `e0eef26befa914a714d67fbcfc1d69ba06a25ea2`, isolated worktree `.worktrees/bl016-heatmap-correction`. All commands below ran in that worktree. This is QA evidence only; no product edit, merge, push, gate, or seal.

| Local order | Workdir / exact command or action | Exit / result | Evidence / warning |
|---|---|---|---|
| 1 | `backend`: `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp "$env:TEMP\qa4b104a"` | 0, 387 passed | `backend-before.txt`; Starlette/httpx and AnyIO deprecations |
| 2 | root: `.\.venv\Scripts\python.exe scripts\validate_engineering_data.py` | 0 | `validator.txt`; eight catalogs and source hashes |
| 3 | `backend`: `..\.venv\Scripts\python.exe -m scripts.export_schema` | 0 | `schema.txt`; five generated outputs |
| 4 | `backend`: `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp "$env:TEMP\qa4a104a"` | 0, 387 passed | `backend-after.txt`; same deprecations |
| 5 | `frontend`: `corepack pnpm run typecheck` | 0 | `frontend-typecheck.txt` |
| 6 | `frontend`: `corepack pnpm run lint` | 0 | `frontend-lint.txt` |
| 7 | `frontend`: configured EOX environment from implementation `final4-build.txt`; `corepack pnpm run build` | 0 | `frontend-build.txt`; non-failing Vite/Vinext advisories; Satellite bundle assertion passed |
| 8 | `frontend`: `corepack pnpm run test` | 0, 126 passed | `frontend-test.txt`; after build |
| 9 | root: `.\.venv\Scripts\python.exe harness\verify\run_camera_range_lens_distance_live.py serve --runtime harness/tmp/camera-ux-qa-20261004-01` | 0 | `live-serve.txt`; fresh ports 8070/3070 and ignored runtime |
| 10 | root: same runner `verify --runtime harness/tmp/camera-ux-qa-20261004-01` | 0, 20/20 assertions | `live-verify.txt`, independent API JSON |
| 11 | root: same runner `stop --runtime harness/tmp/camera-ux-qa-20261004-01` | first attempt 1 under restricted CIM; approved elevated retry 0 | `live-stop-01.txt`; retry verified worktree-specific command lines and stopped only manifest-owned trees |
| 12 | `frontend`: `NEXT_PUBLIC_API_URL=http://127.0.0.1:8070` plus the same EOX variables; `corepack pnpm run build` | 0 | `browser-build.txt`; fixes initial browser setup's default-port `Failed to fetch` toast |
| 13 | `frontend`: `corepack pnpm run test` | 0, 126 passed | `browser-build-tests.txt`; after isolated-API build |
| 14 | root: safe runner `serve --runtime harness/tmp/camera-ux-qa-20261004-02` | 0 | `live-serve-02.txt`; fresh ignored runtime |
| 15 | Chrome production UI: import original KML, bulk configure eight SMART poles, calculate 50/25/75 m, inspect both pinned cards, measure/Clear/Esc/error/delay/export/reopen, test area exclusion and responsive 600/390 | PASS with stated limits | `harness/verify/2026-10-04-camera-ux-independent-browser.json`; zero warning/error logs after rebuild |
| 16 | root: safe runner `analyze --runtime harness/tmp/camera-ux-qa-20261004-02 --export harness/tmp/camera-ux-qa-20261004-02/qa-export.json` | 0, 6/6 assertions | `live-analyze.txt`, independent measurement JSON; no concurrent reopen hash event in this run |
| 17 | root: same runner `preview --runtime harness/tmp/camera-ux-qa-20261004-02 --project 0da0f38d-a45d-4cd2-9ff4-aaa7ba382630` | first attempt 1 because browser-project baseline absent; safe copy of the pre-edit exported project to that ignored path, retry 0 | `live-preview.txt`, `live-preview-retry.txt`, independent preview JSONL; 280 m sample 1.424015746905178 px/face inside envelope and outside bands |
| 18 | root: safe runner `stop --runtime harness/tmp/camera-ux-qa-20261004-02` | 0 under approved elevation | manifest identity checked; only owned trees stopped |
| 19 | root: safe runner `serve --runtime harness/tmp/camera-ux-qa-20261004-03` | 0 | `live-serve-03.txt`; independent stable-view 50/25/75 browser retest |
| 20 | Chrome production UI: reopen original QA export and rerun 25/75 m from default 50 m | PASS | Stable views showed bounded coloured previews after each current result; initial in-flight fit/tile screenshots excluded from final disposition |
| 21 | root: safe runner `stop --runtime harness/tmp/camera-ux-qa-20261004-03` | 0 under approved elevation | manifest identity checked; only owned trees stopped |
| 22 | root: `git diff --exit-code -- schemas Input frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml`; `git diff --check`; `Get-FileHash -Algorithm SHA256 Input/Miracle_Mile_Lighting_Poles.kml` | 0; 0; SHA-256 `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328` | clean generated/source current diff |
| 23 | root: `git diff --name-only 98ac861e..HEAD -- data Input backend/app/services/camera_geometry.py backend/app/services/camera_pixel_density.py backend/requirements.lock frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml frontend/package.json harness/seals schemas/project.schema.json schemas/fixture-model-catalog.schema.json schemas/ies-library.schema.json schemas/camera-equipment-catalog.schema.json` | 0, no paths | frozen catalogs, engines, dependency/configuration, accepted seals and four non-OpenAPI schemas preserved |
| 24 | root at clean QA evidence commit `0a88c47b3bd2421d734f7d32986851b409f63a53`: `.\.venv\Scripts\python.exe harness/verify/verify_phase_readiness.py --manifest harness/verify/2026-10-04-camera-range-lens-distance-readiness.json` | 0, IMPLEMENTATION READINESS: PASS; 6 milestones/9 acceptance criteria | `readiness-qa-01.txt`; verifier is an implementation-readiness check and does not issue QA or master acceptance |

Recovery notes: Two initial command wrappers used an incorrect relative log directory and one wrong Python path; neither produced a test result. The actual backend run starts at row 1. The browser download observer timed out, but the downloaded 280425-byte JSON was located, copied to ignored runtime, validated against the Project model and reopened. Historical `git diff --check 98ac861e..HEAD` reports trailing whitespace inside preserved implementation command transcripts; current `git diff --check` is clean and no product file is implicated. Whole-request hash observation during a concurrent reopen is a known limitation of the implementation run and is not used as endpoint-isolated evidence here.
