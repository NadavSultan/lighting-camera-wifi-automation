# Independent QA review — 2026-10-04 — Camera range/lens/distance UX

Verdict: **PASS** for the separately approved UX correction. This is an independent QA disposition, not a scoped master decision or phase seal.

## Scope, independence, and non-goals

- Exact product commit reviewed: `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`; base `98ac861e5eb9bc1587604f3f43be61908baabfb2`; clean evidence tip before QA `e0eef26befa914a714d67fbcfc1d69ba06a25ea2` in `.worktrees/bl016-heatmap-correction`.
- Contract: approved `docs/superpowers/specs/2026-10-04-camera-range-lens-distance-design.md` and plan of the same date; work record `harness/phases/2026-10-04-camera-range-lens-distance.md`; UX-01–UX-09.
- Reviewer: separate independent QA session from the implementation author, using fresh current-commit checks and real Chrome production interaction. Implementation transcripts were orientation only.
- Scope: complete scoped code/test/generated diff; 74-pole production workflow; range, preview/raster lifecycle, pinned cards, transient measurement, source/engine/catalog/dependency preservation.
- Excluded: product fixes, merge, push, scoped master acceptance, Phase 8, and seal.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Exact commits, approved design/plan, scoped diff, protected base paths | PASS |
| Deterministic verification | Backend before/after export, validator, generated freshness, frontend typecheck/lint/build/tests | PASS |
| Acceptance-matrix review | UX-01–UX-09 below, implementation and independent edge review | PASS |
| Rendered/manual workflow | Chrome production, original KML, stable 50/25/75 and 300 m views, measurement and error/race paths | PASS |
| Source/prior-phase regression review | Source SHA, 20 API assertions, Phase 3 metrics, report/KML, frozen engines/catalogs/deps/seals | PASS |

## Acceptance criteria

| ID | Independent method and evidence | Result |
|---|---|---|
| UX-01 | Browser default 50 m, one range field/action, stale→current at 25/75 m; safe live API runner checked every projected envelope vertex within selected 25/50/75 m radius. | PASS |
| UX-02 | Reviewed `visibleResult` gating, holes and no-band helper tests; browser hide/stale/current; independent 280 m projected sample 1.424015746905178 px/face inside 300 m preview and outside all density bands. `2026-10-04-camera-ux-independent-preview.jsonl`. | PASS |
| UX-03 | Reviewed map source/layer diff: no raw Phase 3 FOV or overlap fill; browser Camera controls omit them; live runner checked byte-equivalent Phase 3 footprints, overlaps and priority summaries at 25/50/75 m. | PASS |
| UX-04 | Both selected SMART slots showed pinned r1 camera/lens names, IDs, 6 mm, 52°/40° and 4056×3040 px. Reviewed exact revision resolver and current tests for historical r1 versus current r2, missing explicit pins, unassigned, unavailable, incompatible and nullable fields. | PASS |
| UX-05 | PyProj inverse-generated 30/40 m endpoints returned 50 m within 1e-6; real 49.94 m click response independently matched projected hypot within 1e-6. Rejected invalid/non-metre CRS, coordinates, nonfinite and transform failures; stores unchanged for successful and rejected endpoint requests. | PASS |
| UX-06 | Real two clicks, ignored third click, Clear/new, Esc, visible 422/no invented value, delayed response after Clear and same-ID reopen reset. Deferred response after project/CRS replacement checked in current tests and controller code. | PASS |
| UX-07 | While measuring, pole selection stayed fixed, azimuth drag marker was removed and area entry buttons disabled; each priority/calculation/Wi-Fi draft disabled measurement. Lower-left control stayed separate from attribution at desktop/600/390 with no horizontal overflow. | PASS |
| UX-08 | Source KML SHA and source poles unchanged; export while measurement complete had exactly Project fields and no measurement keys, then reopened. Frozen catalogs, Phase 3/density engines, dependencies, four non-OpenAPI schemas and prior seals match base. BL-016 winner/contributor helper tests reran. | PASS |
| UX-09 | Fresh full deterministic checks, configured production build before rendered tests, 20/20 live API assertions, real Chrome workflows, zero warning/error log entries after corrected QA bundle, and clean readiness rerun listed below. | PASS |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp "$env:TEMP\qa4b104a"` from `backend` | `e0eef26` containing product `fb1c522` | 0, 387 passed | `backend-before.txt`; non-failing Starlette/httpx and AnyIO deprecations |
| `.\.venv\Scripts\python.exe scripts\validate_engineering_data.py` | same | 0 | Eight catalogs and supplied-source hashes |
| `..\.venv\Scripts\python.exe -m scripts.export_schema` then backend pytest with `--basetemp "$env:TEMP\qa4a104a"` | same | 0; 0, 387 passed | Five generated outputs; no current diff |
| `corepack pnpm run typecheck`, `lint`, configured `build`, then `test` from `frontend` | same | all 0; 126 passed | EOX Satellite assertion passed; non-failing Vinext/Vite advisories |
| Safe scoped runner `serve`/`verify` on fresh ignored runtime 01 | same | 0; 20/20 | `2026-10-04-camera-ux-independent-api.json` |
| Chrome production browser runtimes 02/03 | same | PASS | `2026-10-04-camera-ux-independent-browser.json`; copied measurement/preview data; CUA screenshots in session, no saved PNG path from browser tool |
| Safe runner `analyze`/`preview` on ignored runtime 02 | same | 0; 6/6 and analytic 280 m sample | `2026-10-04-camera-ux-independent-measurement.json`, `2026-10-04-camera-ux-independent-preview.jsonl` |
| Current generated/source diff, base protected-path comparison, KML SHA | same | clean/no paths/hash matched | Exact commands and outputs in command log |
| `.\.venv\Scripts\python.exe harness/verify/verify_phase_readiness.py --manifest harness/verify/2026-10-04-camera-range-lens-distance-readiness.json` | QA evidence commit, clean worktree | PASS | Clean rerun transcript appended after evidence commit |

Detailed exact command order, failures, recovery and warning locations: `harness/logs/2026-10-04-camera-ux-independent-qa/command-log.md` and adjacent transcripts. Browser observations: `harness/verify/2026-10-04-camera-ux-independent-browser.json`.

## Findings

No open product findings.

QA setup/recovery limits were kept separate from product disposition: the first browser bundle used the default API port and showed `Failed to fetch`; rebuilding with the isolated API URL and rerunning the rendered tests resolved it. The browser download-event observer timed out; the actual downloaded JSON was present, validated and reopened. An initial preview analyzer call lacked its expected ignored baseline file; copying the pre-edit browser export to that location made the independent analytic check pass. The sandboxed ownership-safe stop could not read CIM process identities; approved elevated retries checked command lines and stopped only manifest-owned server trees. Early raster screenshots during map fit/tile transition were not used; settled 50/25/75/300 m browser views and current backend tiles supported the verdict. The implementation's concurrent-reopen whole-request hash limitation remains explicitly excluded from endpoint-isolated read-only proof; this QA run's uncontended requests and endpoint tests provide that proof.

## Definition of Done

- [x] Complete scoped diff and file boundary reviewed.
- [x] Every UX-01–UX-09 independently disposed.
- [x] Required deterministic and production-browser checks completed on the reviewed product history.
- [x] Source, prior-phase and excluded-path preservation verified.
- [x] Independent PASS supported without treating implementation evidence as current QA.

## Verdict and next gate

**PASS**. Open product findings: none. Eligible for a separate scoped master review of this exact product and QA evidence history. No merge, push, gate decision or seal was performed here.
