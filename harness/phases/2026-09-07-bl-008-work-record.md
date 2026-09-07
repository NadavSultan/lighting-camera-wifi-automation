# Phase work record — 2026-09-07 — BL-008

Status: active

## Scope, authority, and non-goals

- Requested work: Deliver BL-008 CAP workflow and result clarity (BL008-01..BL008-05).
- Controlling documents: plan §9; `docs/post-roadmap-backlog.md` BL-008.
- Acceptance IDs: BL008-01 through BL008-05.
- Authorized file boundary: EngineeringWorkspace/Map, globals.css; create CapPlanningPanel.tsx, cap-workflow-view.mjs/.d.mts, test; harness evidence. Reuse phase6-cap-workflows. No CAP-service/model/schema changes. OBS-01 not in scope.
- Base: worktree after BL-002 on HEAD `71d4d5248f5460268b9993e9f405693b8aa2434e`.
- Non-goals: OBS-01, CAP algorithm/candidate inference, fixture movement, Phase 8.
- Durable goal: work-record based (CreateGoal not activated).
- Stopping condition: helper + frontend checks + Phase 6 pytest; verification summary ready.

## Milestones

| Milestone | Status |
|---|---|
| M1 capResultSummary helper + tests | in progress |
| M2 CapPlanningPanel extraction | not started |
| M3 map focus / show sites | not started |
| M4 verification | not started |
