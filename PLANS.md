# Plans

This is the execution plan index. The current Phase 7 requirements, decisions, milestones, verification, and acceptance IDs are in `harness/phases/phase-07.md`.

## Active plan

Phase 7 implementation was authorized on 2026-09-04 and executed under `harness/phases/2026-09-04-phase-7-implementation.md`. Decisions `P7-D01` through `P7-D15` remain binding. Independent QA and master gate remain pending; no Phase 7 seal yet.

## Guardrails

- No source-pole creation, movement, redistribution, optimization, or deletion.
- No invented CAP operational values, RF predictions, compliance claims, or unsupported report claims.
- Ordinary failures enter the logged repair/retry loop and do not stop the phase. Only a blocker proven under `AGENTS.md` may pause execution for user direction.
- Progress reports and response-turn boundaries do not end an unfinished durable goal.
- Independent QA PASS and master PASS are required before sealing Phase 7.

## Bootstrap record

The durable workflow bootstrap was created against clean main-branch commit `72441d2c` on 2026-08-30. Phase 6 was subsequently implemented at `3a81f316`, independently passed at `f9dcea2f`, and formally closed by the 2026-09-03 master gate and seal. The bootstrap record remains historical workflow evidence.
