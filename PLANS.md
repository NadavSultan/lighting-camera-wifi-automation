# Plans

This is the execution plan index. The current proposed Phase 7 requirements, decisions, milestones, verification, and acceptance IDs are in `harness/phases/phase-07.md`.

## Active plan

Phase 7 planning is active under `harness/phases/phase-07.md`. Review and explicitly approve or replace planning decisions `P7-D01` through `P7-D15`. Phase 7 implementation must not begin without a separate explicit implementation authorization.

## Guardrails

- No Phase 7 implementation while planning decisions remain unapproved.
- No source-pole creation, movement, redistribution, optimization, or deletion.
- No invented CAP operational values, RF predictions, compliance claims, or reporting exports.
- Ordinary failures enter the logged repair/retry loop and do not stop the phase. Only a blocker proven under `AGENTS.md` may pause execution for user direction.
- Progress reports and response-turn boundaries do not end an unfinished durable goal.

## Bootstrap record

The durable workflow bootstrap was created against clean main-branch commit `72441d2c` on 2026-08-30. Phase 6 was subsequently implemented at `3a81f316`, independently passed at `f9dcea2f`, and formally closed by the 2026-09-03 master gate and seal. The bootstrap record remains historical workflow evidence.
