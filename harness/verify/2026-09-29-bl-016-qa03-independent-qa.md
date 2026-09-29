# Independent QA review — 2026-09-29 — BL-016 QA-03 corrective retest

Verdict: FAIL

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: product `ca7f46c57a28028bd96b8e40926f50e3e4932edc`; evidence tip `8cc7170fce880e9aff78d3558e4f9a8b647ba61b`; branch `codex/bl-016-qa03-independent-retest-2026-09-29`.
- Controlling contract and acceptance IDs: `docs/superpowers/specs/2026-09-22-bl-016-camera-pixel-density-engineering-design.md`; Task 10 in `docs/superpowers/plans/2026-09-22-bl-016-camera-pixel-density.md`; in particular `BL016-16`, plus Task 10 rendered Satellite, failure, persistence, and prior-layer checks.
- Reviewer/session independence: fresh production build and browser session in the separate QA worktree, at the handoff's exact clean evidence tip. Product paths match the named product commit. No product source edits were made.
- Review scope: QA-03 Satellite production configuration and rendered imagery; density legend/layer/opacity behavior; overlap display and point inspection; invalid-profile UI/API failures; project/source preservation; visible Phase 3 and Phase 7 regression signals.
- Non-goals and excluded phases: no product fixes, merge, phase acceptance, master gate, seal, or work beyond closed Phases 1–7 and the already authorized BL-016 retest.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | Exact HEAD/product commit, clean starting status, handoff and source boundary | PASS; starting worktree clean; product commit and evidence tip match handoff; no product changes |
| Deterministic verification | Fresh configured production build and source/hash check | PASS for fresh configured frontend build; full backend/catalog/schema/test matrix was not rerun in this independent browser retest (historical implementation evidence is not substituted) |
| Acceptance-matrix review | Task 10 browser workflows and `BL016-16` inspection | FAIL; overlap point popup does not expose the multiplicity or complete contributor list |
| Rendered/manual workflow | Real production browser, supplied KML, Satellite tiles/attribution, density styling, invalid-profile UI | PASS for Satellite seam and failure UI; FAIL for overlap inspection |
| Source/prior-phase regression review | Source hash/coordinates, Phase 3 camera geometry, Phase 7 report preview | PASS for reviewed regressions; report preview showed “Complete with warnings” |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| QA-03: public Satellite config survives production build | Fresh `corepack pnpm run build` with the five approved `NEXT_PUBLIC_SATELLITE_*` values | Configured client bundle test passed 1/1; production UI selected Satellite | PASS |
| Task 10 rendered Satellite and attribution | Real Chrome session at `http://127.0.0.1:3070/`, import supplied KML, select Satellite | Visible aerial/satellite imagery; EOX Cloudless attribution remained visible; density layer retained over imagery | PASS |
| Task 10 density bands, legend, and opacity | Production browser visual inspection; read source and committed frontend assertions | Ten-row legend visible; density fill translucent with satellite visible beneath; implementation and tests specify `0.58`. Direct runtime MapLibre paint-property inspection was unavailable. | PASS with runtime-property limitation |
| `BL016-16`: overlap labels and point inspection list winner, multiplicity, and all contributors | With 148 footprints and 4,233 persisted density overlap regions, inspect rendered 2×–10× labels and click density locations | Popup repeatedly reported `1×` and one contributor at positions in the dense overlap rendering; a single click generated duplicate identical popup copies (three observed). It did not provide the expected multi-camera contributor list. | FAIL |
| Task 10 controlled invalid-profile failure | Set lower plane above upper plane in UI; issue invalid-profile and geographic-engineering-CRS API requests | UI marked result stale, hid/disabled density display and disabled calculate with validation alert; both API requests returned 422. Project JSON hash stayed the same across the request-level failures. | PASS for controlled validation path |
| Source preservation and existing-pole boundary | Import exact KML and compare SHA-256; inspect source coordinates and mode | 74 source poles, Existing-Pole mode, source coordinates shown read-only; KML SHA-256 `2F89F9F2BE306C18221C643C98D5C1A9ABDB6449AAB8A77EA4B76B3694E8E328`; no `Input/` changes | PASS |
| Relevant prior-phase regression | Inspect populated camera configuration/geometry and report-package preview in the same production UI | 148 valid footprints; both camera slots rendered pinned provenance and FOV; report preview status `Complete with warnings` | PASS for these sampled surfaces; not a full prior-phase regression suite |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| `git status --short --branch`; `git rev-parse HEAD`; `git show --no-patch --format=%H ca7f46c57a28028bd96b8e40926f50e3e4932edc`; `git diff --stat`; `git status --short -- Input` | Evidence tip `8cc7170fce880e9aff78d3558e4f9a8b647ba61b` | PASS; clean starting status, expected branch/tip/product identity, no Input changes | Ignored temporary runtime data excluded from Git status |
| From `frontend/`: set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8070`, `NEXT_PUBLIC_SATELLITE_TILES=https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2025_3857/default/g/{z}/{y}/{x}.jpg`, `NEXT_PUBLIC_SATELLITE_TILE_SIZE=256`, `NEXT_PUBLIC_SATELLITE_MIN_ZOOM=0`, `NEXT_PUBLIC_SATELLITE_MAX_ZOOM=18`, `NEXT_PUBLIC_SATELLITE_ATTRIBUTION=EOxCloudless - https://cloudless.eox.at by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2025). Maps: https://maps.eox.at`; `corepack pnpm run build` | Evidence tip; independent QA worktree | PASS, exit 0; configured-client-bundle integration test 1/1 | Build advisories: Vinext plugin timing, >500 KB chunk, dynamic-route classification |
| `Get-FileHash Input/Miracle_Mile_Lighting_Poles.kml -Algorithm SHA256` | Evidence tip; independent QA worktree | PASS; exact hash recorded above | Source file remained byte-for-byte unchanged |
| Start isolated FastAPI on `127.0.0.1:8070` with `LCWA_DATA_DIR` at `backend/harness/tmp/bl016-qa04-2026-09-29/projects`; start production frontend with the same six public variables on `127.0.0.1:3070` using `corepack pnpm run start -- --host 127.0.0.1 --port 3070` | Evidence tip; isolated temporary project `82cf888d-88e3-4448-87e4-a1daa0ebbbc1` | PASS; browser import, camera density calculation, report preview, and API requests responded | Temporary app data only; no product files changed |
| Import `Input/Miracle_Mile_Lighting_Poles.kml`; configure 74 existing poles as Phoenix 1 SMART, 10 m, IMX477 / JL-LN037 3.56 mm on both slots; calculate density; switch Standard/Satellite; inspect labels and popups | Evidence tip; project `82cf888d-88e3-4448-87e4-a1daa0ebbbc1` | PASS for import, calculation and Satellite; FAIL for expected multi-contributor point popup | Backend logged camera-density calculate 200; UI showed current result, 148 valid footprints, 4,953 camera-footprint overlap pairs and 4,233 density overlap regions |
| API invalid-profile request (`lower_projection_plane_m` greater than `upper_projection_plane_m`) and request with `projected_crs=EPSG:4326` | Evidence tip; isolated project | Both returned 422; project JSON SHA before/after the request-level validation remained `DBD10143C058DCAE39B5F6B9E469F49FCA52ADC509A8F5280B810C0AEF6C87DA` | Controlled request validation only; this does not exercise an internal calculation exception path |
| Restore valid UI profile and recalculate; inspect isolated project JSON | Evidence tip; isolated project | PASS; UI returned to Current after 200; final JSON SHA-256 `B152CEF2AC9A77ADE62784E8FB67D920569E491B98AC8BA5B1B6FD287E3487D2` | UI configuration/recalculation occurred between the initial and final file hashes |

Historical implementation evidence in `harness/verify/2026-09-29-bl-016-qa03-verification.md` and `2026-09-29-bl-016-qa03-browser.json` guided setup only; it is not used as proof of the independent browser observations above. The browser screenshot was visually observed in-session but no screenshot file was saved. This review did not capture a separate browser console log artifact.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| QA03-IA-01 | Major | `BL016-16` / design criterion 13 requires a point-inspection popup containing displayed band, stored winner, all covering cameras, and multiplicity. Map rendered numerous 2×–10× labels and persisted thousands of overlap regions, while repeated clicks showed `1×` and only one camera in `Contributors`. Three identical popup copies were visible from a single click. | Interactive inspection did not report the multi-camera overlap represented by the rendered map, and duplicated event handling produced repeated popup DOM copies. | Correct the overlap hit testing/feature selection so a representative multi-camera point reports its actual band, deterministic winner, multiplicity, and complete contributor set once; ensure one click creates one popup. Independently rerun Task 10 overlap inspection on the corrected commit. |

## Definition of Done

- [x] Complete implementation diff and file boundary reviewed.
- [x] Every mandatory acceptance item in this review scope disposed as PASS or recorded as a blocking finding.
- [x] Required fresh configured production build and rendered checks in this review scope completed on the recorded evidence tip.
- [x] Source preservation, sampled prior-phase surfaces, and later-phase exclusion verified.
- [x] Verdict supported without relying on unverified claims.

## Recovery protocol

1. Preserve this report and exact reviewed commit identity.
2. The overlap failure was reproduced at multiple map positions after dismissing existing popups; current source was not changed.
3. If implementation changes, invalidate the affected overlap result and retest the new exact commit.
4. Resume only from evidence that remains applicable.

## Allowed stopping conditions

QA is complete and the supported FAIL verdict is recorded. BL-016 remains unaccepted; this report does not authorize the master gate, a phase seal, or post-roadmap work.

## Verdict and next gate

- Verdict: FAIL.
- Open findings: QA03-IA-01 (Major), overlap inspection does not expose complete contributor provenance/multiplicity and creates duplicate popups.
- Master gate eligibility: not eligible while this independent QA finding is open.
- Exact next action: correct the overlap point inspection and duplicate popup behavior within separately authorized BL-016 scope; issue a new clean evidence tip and request an independent retest.
