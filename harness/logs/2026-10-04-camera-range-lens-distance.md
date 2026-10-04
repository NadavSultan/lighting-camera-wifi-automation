# Execution log — 2026-10-04 — Camera range/lens/distance UX

## Scope and non-goals

Work record: `harness/phases/2026-10-04-camera-range-lens-distance.md`.
Contract, acceptance UX-01–09, commands and authorized boundary: approved 2026-10-04 spec/plan. Base `98ac861e5eb9bc1587604f3f43be61908baabfb2`, existing named worktree. Durable goal thread `01a10656-218f-7493-a7da-e7108defa48d` active. No merge/push/seal/acceptance.

## Environment and execution entries

- Startup read AGENTS.md's ten files in order, accepted gate and approved spec/plan; inspected exact HEAD, status/diff and sources/tests.
- `python -m venv .venv`: exit 0.
- `python --version`, `node --version`, `corepack pnpm --version`: 3.12.10 / 24.19.0 / 12.3.4.
- `.venv/Scripts/python.exe -m pip install -r backend/requirements.lock`: sandbox exit 1, forbidden socket access. Escalated locked retry active.
- `corepack pnpm install --frozen-lockfile` from frontend: sandbox exit 1, access denied removing module-directory contents. Escalated frozen retry active.
- `Get-NetTCPConnection -State Listen ... 8070,3070`: no entries; aggregate discovery command exit 1 due to empty Windows query, not proof of server failure.

Subsequent exact command transcripts are paired dated files under `harness/logs/2026-10-04-camera-ux/`; they record command, commit, output, warnings and exit. Nonzero expected RED tests are not verification PASS. Baseline and final runs are separate.

## Recovery and close state

Use AGENTS.md recovery protocol. Preserve failed outputs/diff, recover safely in scope and continue; no proven blocker. Current milestone M0; readiness not run.

M0 complete: both escalated installs exited 0. Baseline command evidence in paired files. Baseline build Satellite test skipped unconfigured (not an acceptance PASS); final configured build required. Full test counts: backend 367, frontend 113. Main checkout untouched.

M1 RED: 12 endpoint tests returned 404. First GREEN found test-only assumption: GET /projects recalculates camera geometry; corrected non-persistence assertion to compare stored bytes directly. Failed focused/full outputs retained; m1-green-02 passes. Further nonfinite/transform tests added; full rerun m1-full-02 pending. Git index sandbox denied preflight commit; authorized escalated retry committed ec446ea1. This does not expand product scope.

M4 regression repair: m4-frontend exit 1, sole historical source assertion expected camera_overlap in workspace. This contradicts approved removal of the raw overlap control; updated assertion to current density control. m4-frontend-02 exit 0, 125/125 tests. Checkpoint cde9b73f was committed before that regression repair; not final readiness.

## M5 verification and recoveries

- `final-*` deterministic checks passed at `4862f08f`; these are historical after the subsequent copy/raster fixes. Counts were backend 387 and frontend 125; configured Satellite build test ran, not skipped.
- `final-live` failed because port 3070 was occupied. Inspection afterward showed the legacy runner's unconditional port-based cleanup had stopped that listener although it did not start it. This was an execution error. Its owner was unknown, so no guessed restart was attempted. Port 3000 and its existing application remained running. Preserve the failure; do not use that runner again. The scoped replacement checks all ports before launching and verifies the manifest PID's worktree command identity before stopping only its own process tree. No user listener is part of replacement cleanup.
- `final2-backend-before` failed with Windows long-path `FileNotFoundError` in the new long basetemp path. The failed tree/output were retained. A fresh short worktree-local path `harness/tmp/f2b` passed all 387 tests. Subsequent runs use unique short paths; no deletion or destructive recovery occurred.
- Corrected the obsolete “displayed boundary” explanation to describe the stored Phase 3 boundary. `final2-frontend` exposed the historical case-sensitive copy assertion; updated that affected assertion and passed `final3-*` deterministic checks at `ac862309` (387/125). Those checks are historical after raster correction.
- The ownership-safe live runner at `ac862309` passed 20 API assertions: 74-pole import, original source hash, bounded 25/50/75 m envelopes, unchanged Phase 3 geometry/metrics, atomic failed calculation, retained-hidden stale state and successful recalculation, legend, KML, Phase 7 package, unchanged sources, known 50 m and read-only distance request.
- Real Chrome production browser at `ac862309`: default50, ranges25/75, grey preview beyond density, both pinned cards, Standard/Satellite, hide/show, two-contributor overlap, actual49.99288958546626 m clicks displaying49.99 m, Clear/Esc, drawing/pole/azimuth/density exclusion, controlled422 and delayed-response cancellation, save/export/reopen reset, 600/390px layouts. Direct independent PyProj comparison and exported model validation passed. Browser download-event observation timed out, but the actual JSON download was found at the expected Downloads filename, validated and reopened through the UI; no false claim that the observation API passed.
- The narrow-width run exposed eight transient MapLibre raster texture `.bind` errors. Saved in `harness/verify/2026-10-04-camera-ux-browser/resize-console-failure.json`; not a browser PASS. Safe reproductions on a fresh settled map, during a range calculation, and after stale invalidation did not repeat the error. The stack/source trace identifies raster drawing with a missing texture; source inspection found the lifecycle used `setTiles([])` despite MapLibre's one-or-more-tile contract. In-scope correction replaces raster sources/caches per fingerprint and removes them when no current visible result exists; ready source updates no longer wait on an already-fired map load event. No library, engine, dependency, or boundary expansion.
- Raster lifecycle RED missing helper, GREEN 11 focused tests; full frontend GREEN126 after updating the source assertion to the helper and testing linear resampling/opacity behavior. Typecheck PASS. Commit `fb1c522f2f14e2eebfa638f74af3cbde74920b1e` is the final implementation candidate; `final4-*` and the new production run must verify it. Independent QA/master remain pending.

## Final current evidence and harness recovery
At fb1c522f final4 commands all exit0: backend387 before/after, frontend126, validator/schema/typecheck/lint/configured build/generated freshness. Safe-live-api-03 passed20 API assertions. Fresh final browser error/warning log empty after refresh/resize/Satellite.
Initial source comparison incorrectly included a different import timestamp; exact poles and filename/hash/size/content/CRS comparison passed. Initial280m sample was outside10m fixture envelope; retained failure, deliberate20m wide-lens UI fixture verifies1.424px/face inside preview/no band, then restored10m/6mm/50m. No engine change.
final-measurement-all whole-window hashes failed because event5 overlapped deliberate Open Project during delayed response. Raw evidence retained; final-measurement-scoped explicitly excludes event5 only from uncontended hash comparison. Seven uncontended windows and all independent references pass; endpoint tests prove read-only success/error. Concurrent reopen is not claimed byte-invariant.
Current artifacts use fb1c522f directory; earlier screenshots/passes and raster errors historical. Evidence/index packaging first attempt hit Windows default cp1255 decoding; resumed in explicit UTF8, no product changes. Independent QA NOT REVIEWED. Clean readiness remains final operational step.

Final boundary/whitespace exit0; 384 protected paths unchanged. First safe-live-stop-03 CIM lookup was sandbox denied but PowerShell returned0/empty, so no identity was proven and no process was stopped despite its final message. Corrected test harness lookup to fail on CIM errors, then escalated safe-live-stop-03-verified identified/stopped only owned66360/46040 trees successfully. Runtime evidence preserved.

Staged whitespace check found raw tool-output trailing spaces in newly added transcripts. Preserved exact original bytes in adjacent .raw.txt.gz and normalized trailing spaces in readable .txt views; output content, warnings, exit/HEAD retained. Staged check rerun required. Files: harness/logs/2026-10-04-camera-ux/final-build.txt, harness/logs/2026-10-04-camera-ux/final2-backend-before.txt, harness/logs/2026-10-04-camera-ux/final2-build.txt, harness/logs/2026-10-04-camera-ux/final2-frontend.txt, harness/logs/2026-10-04-camera-ux/final3-build.txt, harness/logs/2026-10-04-camera-ux/final4-build.txt, harness/logs/2026-10-04-camera-ux/raster-lifecycle-frontend.txt, harness/logs/2026-10-04-camera-ux/raster-lifecycle-red.txt, harness/logs/2026-10-04-camera-ux/safe-live-stop-03.txt

## Clean readiness and handoff
Readiness exit0 PASS at clean evidence commit0790f925 (productfb1c522f), six milestones/nine criteria. QA handoff NOT REVIEWED; master pending; no seal/merge/push. Main remains71d4d524 with original untracked items; port3000 HTTP200. Durable objective achieved; completion follows final clean recheck.
Work-record startup packaging introduced one cp1255 punctuation byte in the appended section; UTF8 read failed at checkpoint, corrected that byte to UTF8 without altering product or evidence output. Final evidence recheck required.

Durable service update_goal returned status COMPLETE after clean final verifier exit0 at892b26c. Final transcript retained. Scope objective achieved; QA/master pending. Subsequent changes only record this service closure; no product, integration or acceptance changes.
