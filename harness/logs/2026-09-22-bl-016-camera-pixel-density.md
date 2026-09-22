# Execution log — 2026-09-22 — BL-016 Camera Pixel-Density Map

## Scope and non-goals

- Phase work record: `harness/phases/2026-09-22-bl-016-camera-pixel-density.md`.
- Controlling contract and acceptance IDs: BL-016 engineering design and plan; `BL016-01` through `BL016-20`.
- Authorized work/milestone: Tasks 1–10 sequentially; currently M0 / Task 1.
- Non-goals and excluded phases: design section 19; BL-019/BL-020, merge, push, Phase 8, acceptance, and seals.
- Exact starting commit/worktree: `05257e87b4d6500146239f62f4ebafa4b2217b67`; detached linked worktree; clean; empty starting diff.
- Durable goal identifier/state: `01a0c847-9997-7f73-9beb-367bd8fcc463`, active.
- Implementation-readiness manifest: `harness/verify/2026-09-22-bl-016-camera-pixel-density-readiness.json` (not yet created).

## Environment and file-boundary preflight

| Check | Exact command/inspection | Result | Repository paths affected or required | Boundary disposition |
|---|---|---|---|---|
| Runtime discovery | `python --version`; `node --version`; `corepack pnpm --version`; browser path/port checks | PASS: Python 3.12.10, Node 24.19.0, pnpm 12.3.4, Chrome/Edge present, ports free | `.venv`, Node, Corepack/pnpm, browsers | authorized |
| Locked dependency materialization | `.venv\\Scripts\\python.exe -m pip install -r backend\\requirements.lock`; `corepack pnpm install --frozen-lockfile` | PASS after documented network/file-lock recovery; `pip check` clean | ignored `.venv/`, `frontend/node_modules/`; lock/workspace files unchanged | authorized |
| Build/test/lint/typecheck entry points | frontend test/typecheck/lint/build; backend pytest from `backend/` | PASS: frontend 102/102; backend 100%; typecheck/lint/build exit 0 | backend/frontend source and tests | authorized |
| Generated-artifact/validator entry points | validator and `python -m scripts.export_schema` | PASS; generated schemas byte-clean | generated schemas | authorized |
| Browser/local-server/port requirements | Chrome/Edge `Test-Path`; `Get-NetTCPConnection` 8070/3070 | PASS | ports 8070/3070, temp `LCWA_DATA_DIR`, ignored screenshots/temp evidence | authorized |

## Milestone and acceptance criteria

- Milestone being executed: M0 environment / Task 1.
- Objective completion condition: active durable goal, exact base/boundary, successful sequential preflight, active execution indexes, committed activation record.
- Evidence required: current command outputs, warnings, clean source/schema checks, activation commit.

## Execution entries

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Read mandatory startup sequence, BL-016 architecture/spec/plan, and relevant source/tests | `05257e87` | completed | this log and session output | no repository changes |
| 2026-09-22 Asia/Jerusalem | `git fetch` approved plan history from source task clone; `git switch --detach 05257e87...` | `05257e87` | exit 0 | Git history | source clone remained untouched |
| 2026-09-22 Asia/Jerusalem | Create durable goal | `05257e87` | active | goal `01a0c847-9997-7f73-9beb-367bd8fcc463` | none |
| 2026-09-22 Asia/Jerusalem | Bundled `sdd-workspace` helper attempts | `05257e87` | failed | ignored `.superpowers/.../progress.md` ruling | Windows `C:/` path incompatibility; tracked files unaffected |
| 2026-09-22 Asia/Jerusalem | Create `.venv`; install exact freeze-style `backend/requirements.lock`; `pip check`; pytest discovery | `05257e87` | PASS after recovery | session output | initial `--require-hashes` was incompatible with unhashed freeze lock; one transient FastAPI file lock; pip upgrade advisory |
| 2026-09-22 Asia/Jerusalem | `corepack pnpm install --frozen-lockfile` | `05257e87` | PASS | session output | sandbox network attempt failed; approved network retry reused 492 locked packages; no lockfile drift |
| 2026-09-22 Asia/Jerusalem | `corepack pnpm run test` before build | `05257e87` | expected preflight failure, 101/102 | session output | `dist/server/index.js` absent in clean worktree |
| 2026-09-22 Asia/Jerusalem | Prerequisite `corepack pnpm run build`, then exact test/typecheck/lint/build sequence | `05257e87` | PASS, 102/102 and all commands exit 0 | session output | known >500 kB chunk advisory; Vinext route-classification advisory |
| 2026-09-22 Asia/Jerusalem | root `.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider` | `05257e87` | expected preflight failure during collection | session output | root does not load backend `pythonpath`; 10 `app` import errors |
| 2026-09-22 Asia/Jerusalem | `Push-Location backend; ..\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider` | `05257e87` | PASS, 100% | session output | Starlette/httpx and anyio deprecation warnings |
| 2026-09-22 Asia/Jerusalem | validator; schema export; `git diff --check`; Input/schema diff checks | `05257e87` | PASS | session output | validator: seven catalogs; five generated schema paths; byte-clean |
| 2026-09-22 Asia/Jerusalem | browser/runtime/port discovery and exact `.pnpm-store` cache cleanup | `05257e87` | PASS | session output | Chrome/Edge present; 8070/3070 free; cache path verified within worktree before removal |

Ruling: Task 1 plan orders frontend tests before the build artifact that `rendered-html.test.mjs` imports — run one prerequisite build, then rerun the exact test/typecheck/lint/build sequence — preserves a clean-checkout representative preflight — cost if wrong: the preflight has one additional build invocation only.

Ruling: Task 1 invokes backend pytest from repository root, but `backend/pyproject.toml` defines `pythonpath=["."]` relative to `backend/` and the canonical `OPERATIONS.md` command changes there first — run pytest from `backend/` — preserves the repository test configuration — cost if wrong: command spelling differs while exercised tests are identical.

## Verification requirements

- Deterministic checks required for this milestone: every Task 1 preflight command, sequentially.
- Source/hash/generated-artifact checks: schema generator byte-clean; `git diff --check`; `git diff --exit-code -- Input`.
- Rendered/manual checks: runtime/browser discovery now; full rendered workflow is M9.
- Checks not run and reason: preflight begins after this activation record establishes the boundary.

## Definition of Done

- [x] The milestone's acceptance criteria have objective evidence.
- [x] Required checks passed on the recorded commit/worktree.
- [x] Changed files remain within the authorized boundary.
- [x] No source, prior-phase, dependency, migration, or later-phase violation occurred.

## Recovery protocol

Use the repository protocol verbatim; failures are logged and repaired without discarding work.

## Close state

- Last verified milestone/state: M0 preflight passed; activation commit pending.
- Open blockers: none.
- Blocker record, if any: none.
- Recovery-attempt count: ledger-helper portability issue resolved by exact-layout compatibility ruling; not a product blocker.
- Durable goal state: active.
- Implementation-readiness verifier result: not run.
- Next authorized action: activate indexes and commit Task 1.

## Task 2 — schema 2.8.0, canonical legend, and migration

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Add migration/profile/state/band/legend endpoint tests before implementation | `1c141d09` | RED: import error for missing `CameraPixelDensityBand` | session output | expected missing BL-016 models |
| 2026-09-22 Asia/Jerusalem | Implement strict models, 2.8.0/0.8.0 migration, canonical JSON/schema, endpoint, TypeScript mirrors, validator | `1c141d09` + working tree | GREEN after two minimal corrections | session output | migration initially emitted `{}` defaults; legend schema initially rejected `maximum`; both corrected at source |
| 2026-09-22 Asia/Jerusalem | backend selected tests + validator + schema export | `1c141d09` + working tree | PASS: 24 tests; 8 catalogs; five generated schema paths | session output | Starlette/httpx and anyio deprecation warnings |
| 2026-09-22 Asia/Jerusalem | `corepack pnpm run typecheck` | `1c141d09` + working tree | PASS after one transient modules-directory lock retry | session output | pnpm verified frozen lock and reran permitted esbuild postinstall; no lock drift |

Task 2 acceptance covered: `BL016-01`, `BL016-02`, `BL016-03`; foundational contracts for `BL016-06`, `BL016-10`, `BL016-11`, `BL016-12`, and `BL016-13` are present. Task 2 remains unaccepted pending the full BL-016 gate.

## Task 3 — deterministic camera-plane geometry and density bands

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Add analytic lens, basis, threshold, plane, cap, and band-partition tests before implementation | `6263451d` | RED: missing `app.services.camera_pixel_density` | session output | expected absent Task 3 module |
| 2026-09-22 Asia/Jerusalem | Implement locked basis, density equation, projection plane, 128-gon cap, depth clipping, and canonical polygon primitives | `6263451d` + working tree | first GREEN attempt found one test-only over-assertion | session output | approved signed image-up convention retained; test narrowed to contracted forward-depth behavior |
| 2026-09-22 Asia/Jerusalem | `.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py -q -p no:cacheprovider -k "reference_lens or threshold or camera_coordinates or midpoint or cap or band"` | `6263451d` + working tree | PASS: 17 selected tests | session output | Starlette/httpx and anyio deprecation warnings only |
| 2026-09-22 Asia/Jerusalem | `.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py -q -p no:cacheprovider` | `6263451d` + working tree | PASS: 45 tests | session output | same two dependency deprecation warnings |

Task 3 establishes the deterministic numerical primitives for `BL016-04`, `BL016-05`, and `BL016-06`. BL-016 remains unaccepted pending the complete gate.

## Task 4 — pinned input resolution, per-camera provenance, and fingerprint

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Add pinned/historical revision, disabled-slot, invalid-camera isolation, fingerprint, and 201-camera tests | `e157449a` + working tree | initial run exposed two test/boundary issues | session output | catalog history needed atomic construction; non-finite profile needed controlled service error |
| 2026-09-22 Asia/Jerusalem | Implement ordered resolution, canonical fingerprint, profile/envelope/band persistence, warnings, and 200-enabled-camera guard | `e157449a` + working tree | GREEN after minimal corrections | session output | Task 5 overlap/serialized-limit seam intentionally remains empty until next task |
| 2026-09-22 Asia/Jerusalem | `.\.venv\Scripts\python.exe -m pytest backend/tests/test_bl016_camera_pixel_density.py -q -p no:cacheprovider -k "pinned or disabled or invalid_camera or fingerprint or camera_limit or per_camera"` | `e157449a` + working tree | PASS: 5 selected tests | session output | Starlette/httpx and anyio deprecation warnings only |
| 2026-09-22 Asia/Jerusalem | full BL-016 test file | `e157449a` + working tree | PASS: 50 tests | session output | same dependency deprecations |
| 2026-09-22 Asia/Jerusalem | Phase 3 regression file | `e157449a` + working tree | 37 pass, 4 stale-version assertions fail | session output | assertions expect retired `2.7.0`; scheduled for full regression update after BL-016 tasks; geometry behavior unaffected |

Task 4 covers the per-camera and fingerprint portions of `BL016-04`, `BL016-06`, `BL016-07`, `BL016-08`, `BL016-10`, `BL016-11`, and `BL016-12`. BL-016 remains unaccepted pending the complete gate.

## Task 5 — deterministic overlap partitioning and output limits

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Add analytic two-/three-camera overlap, tie-break, repeat-order, vertex-count, and result-limit tests | `007efba4` | RED: missing `count_persisted_vertices` | session output | expected Task 5 seam |
| 2026-09-22 Asia/Jerusalem | Implement STRtree candidate discovery, polygonized contributor partitions, rank/tie winner selection, canonical IDs/rings, and exact limits | `007efba4` + working tree | first run found analytic test undercount only | session output | test expected 15 m² but omitted a 3 m² B/C-only strip; corrected to 18 m² |
| 2026-09-22 Asia/Jerusalem | exact Task 5 focused pytest selector | `007efba4` + working tree | PASS: 3 selected tests | session output | Starlette/httpx and anyio deprecation warnings only |
| 2026-09-22 Asia/Jerusalem | full BL-016 test file | `007efba4` + working tree | PASS: 53 tests | session output | same dependency deprecations |

Task 5 covers deterministic overlap and safety-limit portions of `BL016-07`, `BL016-08`, `BL016-11`, `BL016-12`, and `BL016-13`. BL-016 remains unaccepted pending the complete gate.

## Task 6 — atomic calculation API and freshness lifecycle

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Add apply/stale retention, success/identity, missing-project, and byte-preserving invalid-request tests | `6ee9fe73` + working tree | tests added before route verification | session output | none |
| 2026-09-22 Asia/Jerusalem | Implement apply/invalidate functions, atomic POST route, and ordinary-save/bulk/open invalidation | `6ee9fe73` + working tree | GREEN | session output | calculation completes and validates before the sole save operation |
| 2026-09-22 Asia/Jerusalem | exact Task 6 two-file pytest command | `6ee9fe73` + working tree | PASS: 62 tests | session output | Starlette/httpx and anyio deprecation warnings only |
| 2026-09-22 Asia/Jerusalem | full backend pytest before compatibility regeneration | `6ee9fe73` + working tree | behavioral tests pass; stale `2.7.0` assertions and OpenAPI freshness fail | session output | compatibility-only failures routed to Task 7 |
| 2026-09-22 Asia/Jerusalem | schema export plus full backend pytest with Task 7 compatibility changes present | `6ee9fe73` + working tree | PASS: 100% | session output | generated contracts and version-only assertions remain unstaged for Task 7; dependency deprecations only |

Task 6 covers atomic/current/stale lifecycle portions of `BL016-09`, `BL016-10`, `BL016-11`, `BL016-12`, and `BL016-13`. BL-016 remains unaccepted pending the complete gate.

## Task 7 — report and generated-contract compatibility

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Update prior-phase current-version assertions to schema `2.8.0`; add calculated BL-016 report archive/no-visual-output test | `6692ab3b` + working tree | GREEN without reporting service changes | session output | historical `2.7.0` migration fixture remains intact |
| 2026-09-22 Asia/Jerusalem | report + engineering-data tests | `6692ab3b` + working tree | PASS: 79 tests | session output | Starlette/httpx and anyio deprecation warnings only |
| 2026-09-22 Asia/Jerusalem | schema export; engineering validator; report + engineering tests; `git diff --check` | `6692ab3b` + working tree | PASS: five schema paths, 8 catalogs, 79 tests, clean diff | generated contract evidence | only `schemas/openapi.json` changed for the new route; no report service or density visual output change |

Task 7 proves Phase 7 packages archive the BL-016 project result while existing KMZ/PDF/XLSX/presentation visualization contracts remain unchanged. BL-016 remains unaccepted pending the complete gate.

## Task 8 — frontend state, API, profile panel, and legend

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Add pure view/current-stale and significant/presentation-only invalidation tests | `987a0c7b` | RED: missing view helper module | session output | expected Task 8 module seam |
| 2026-09-22 Asia/Jerusalem | Implement view helper/declarations, API methods, profile panel, ten-row legend, session legend state, and layer gating | `987a0c7b` + working tree | first source assertion corrected to inspect helper owning stale copy | session output | no engineering calculation added to frontend |
| 2026-09-22 Asia/Jerusalem | focused node tests; `pnpm run typecheck`; `pnpm run lint` | `987a0c7b` + working tree | PASS: 25 tests; typecheck/lint exit 0 | session output | none |

Task 8 covers frontend workflow and immediate-staleness portions of `BL016-01`, `BL016-02`, `BL016-03`, `BL016-09`, and `BL016-10`. BL-016 remains unaccepted pending the complete gate.

## Task 9 — map rendering, overlap labels, and safe inspection

| UTC/local timestamp | Exact command or action | Commit/worktree | Exit/result | Durable evidence | Warnings / affected files |
|---|---|---|---|---|---|
| 2026-09-22 Asia/Jerusalem | Add current/visibility GeoJSON, hole preservation, winner/contributor, and rank/style tests | `129eda85` | RED: missing map helper module | session output | expected Task 9 module seam |
| 2026-09-22 Asia/Jerusalem | Implement band/overlap helpers, ten ascending fills, generated dot pattern, dashed outline, canvas `2×/3×` labels, and text-only popup | `129eda85` + working tree | GREEN | session output | popup uses `setDOMContent` and project values use `textContent` |
| 2026-09-22 Asia/Jerusalem | focused tests; full frontend test/typecheck/lint/build | `129eda85` + working tree | PASS: focused 25, full 107, typecheck/lint/build exit 0 | session output | standard build advisory behavior only |

Task 9 covers rendered vector, overlap, label, visibility, and inspection portions of `BL016-04`, `BL016-05`, `BL016-06`, `BL016-07`, `BL016-08`, and `BL016-09`. BL-016 remains unaccepted pending the complete gate.
