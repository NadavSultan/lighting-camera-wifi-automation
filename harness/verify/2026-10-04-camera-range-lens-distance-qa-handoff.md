# Independent QA review — 2026-10-04 — Camera range/lens/distance UX
Verdict: NOT REVIEWED. This is a prepared handoff using `harness/templates/qa-review-template.md`, not an independent review.

## Scope, independence, and non-goals
- Exact product to review: `fb1c522f2f14e2eebfa638f74af3cbde74920b1e`, worktree `.worktrees/bl016-heatmap-correction`, base `98ac861e5eb9bc1587604f3f43be61908baabfb2`.
- Controlling approved design/plan: `docs/superpowers/specs/2026-10-04-camera-range-lens-distance-design.md`; `docs/superpowers/plans/2026-10-04-camera-range-lens-distance.md`.
- Work record: `harness/phases/2026-10-04-camera-range-lens-distance.md`; UX-01–09.
- Independence: reviewer/session not yet assigned. Implementation author cannot issue QA PASS. No agent/task messaging or parallel review performed.
- Non-goals: merge/push/acceptance/seal, Phase 8, engine changes, pole movement, catalog/dependency updates.

## QA milestones
All NOT RUN independently: repository/diff/authorization; deterministic verification; acceptance-matrix review; rendered workflow; source/prior-phase regression.

## Acceptance criteria and independent methods
All dispositions NOT RUN.
- UX-01: import original 74-pole KML, configure explicit SMART/lenses; default50, stale→calculate25/75; compare every projected preview vertex to radius.
- UX-02: inspect current/hidden/stale/missing gates and envelopes/holes; reproduce recorded 20 m/3.56 mm/300 m below-2 fixture and verify gray preview/no colour.
- UX-03: verify raw FOV/overlap fills absent and Phase 3 geometry/metrics identical across range changes.
- UX-04: inspect both cards before calculation; independently test historical revision vs newer current, missing explicit pin, unavailable and incompatibility.
- UX-05: independently project known endpoints in metre CRS, hypot to <1e-6 m; reject unsuitable CRS/invalid/transformation failures; hash stores before/after.
- UX-06: two/third clicks, Clear/Esc/error, late responses after Clear/project/CRS reset, reopen same-ID reset.
- UX-07: measurement vs all creation/redraw/selection/azimuth handlers; test desktop/600/390.
- UX-08: source bytes/poles/catalog/dependency/engine/base preservation; measure-complete save/export/reopen absent transient data; overlap winner/contributors retained.
- UX-09: rerun deterministic and real production browser on exact reviewed product, clean readiness; zero console/page errors.

## Verification requirements
Run the approved plan's exact final sequence with unique SHORT Windows basetemp (e.g. qa4b/qa4a), build before frontend test, configured EOX Satellite variables from `final4-build.txt`. Preserve all warnings/output/exits. Expected implementation counts387/126; not an independent PASS until rerun.
Use the ownership-safe scoped live runner. Do not rerun legacy port cleanup. Never stop user listeners; inspect fresh port availability. GUI browser must complement API checks.
Implementation evidence: summary, final4 transcripts, boundary JSON, current browser subdirectory `fb1c522f`, API/measurement JSON. Prior ac862309 screenshots and failed resize logs are historical. Whole-request observer hash event5 includes deliberate concurrent Open Project, not endpoint-isolated evidence; use uncontended requests/endpoint tests or improve independent observation.

## Findings
No independent findings yet. Mandatory scrutiny: raster source/cache replacement ordering and load listener; asynchronous measurement guards; exact inherited/explicit pin semantics; source preservation; retained observer limitation and legacy cleanup incident.

## Definition of Done
- [ ] Complete implementation diff and file boundary reviewed.
- [ ] All UX-01–09 independently disposed with evidence.
- [ ] Required deterministic and rendered checks on exact reviewed commit.
- [ ] Source/prior-phase preservation and excluded phases verified.
- [ ] Supported independent verdict recorded.

## Recovery protocol
Preserve exact identity and failures; invalidate affected results after product changes; resume from still-applicable evidence. Follow AGENTS.md proven-blocker rule. Never replace failed outputs or delete user data.

## Allowed stopping conditions
Reviewed commit changed/unidentifiable; required evidence/runtime truthfully unavailable; critical/major authority/source/boundary issue; completed supported QA verdict. QA cannot authorize another phase.

## Verdict and next gate
Verdict NOT REVIEWED. Master eligibility PENDING independent QA. Next action: a separate independent session reviews this product and records PASS/FAIL using the template. No merge/push/seal requested or performed.
