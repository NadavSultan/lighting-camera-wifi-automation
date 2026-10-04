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
