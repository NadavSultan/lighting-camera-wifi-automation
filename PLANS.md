# Plans

This is the execution plan index. Detailed requirements and acceptance IDs remain in `docs/phase-6-cap-planning-and-implementation-contract.md`; implementation instructions remain in `docs/phase-6-master-implementation-prompt.md`.

## Active plan: Phase 6

1. Re-read the required startup documents and the Phase 6 controlling contract; inspect the actual worktree before changing code.
2. Create a durable implementation goal and a dated Phase 6 work record. Complete the environment/file-boundary preflight and record unresolved real-site inputs and document conflicts before product changes.
3. Implement only the approved Phase 6 work packages and file boundary. Keep unknown operational values explicit and preserve Phases 1-5.
4. Regenerate only the approved generated contracts, then run and record the repository verification commands.
5. Produce durable implementation and rendered-QA evidence, pass the implementation-readiness verifier on the recorded commit, and request independent QA. Do not seal or close Phase 6 without its required evidence and master gate decision.

## Guardrails

- No Phase 7 work.
- No source-pole creation, movement, redistribution, optimization, or deletion.
- No invented CAP operational values, RF predictions, compliance claims, or reporting exports.
- Ordinary failures enter the logged repair/retry loop and do not stop the phase. Only a blocker proven under `AGENTS.md` may pause execution for user direction.
- Progress reports and response-turn boundaries do not end an unfinished durable goal.

## Bootstrap record

The durable workflow bootstrap was created against clean main-branch commit `72441d2c` on 2026-08-30. That commit remains the accepted Phase 5 application baseline: the planned Phase 6 service, tests, frontend workflow helper, and `0.6.0`/`2.6.0` version changes are not present in this checkout. This repository observation does not negate work that may exist in a separate, unintegrated worktree, and it is not Phase 6 completion evidence.
