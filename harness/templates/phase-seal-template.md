# Phase seal — Phase N

Seal status: **INVALID — TEMPLATE ONLY**

This file may be copied into `harness/seals/` only after all conditions below are satisfied. A missing, skipped, failed, stale, historical-only, or unrecorded required check keeps the seal invalid. Replace the status with **VALID — ACCEPTED** only when every row is PASS and the cited independent QA and master gate decisions both record PASS.

## Scope and non-goals

- Sealed phase and exact commit:
- Controlling contract/phase record:
- Accepted scope:
- Non-goals and later-phase exclusions:

## Milestones and acceptance criteria

- Implementation milestones record:
- Complete acceptance-matrix record:
- Every acceptance ID disposition:

## Deterministic verification requirements

| Required check | Exact command/workflow | Sealed commit/worktree | Evidence path | Result |
|---|---|---|---|---|
| Full backend tests |  |  |  | not run |
| Engineering/source validation |  |  |  | not run |
| Generated-contract freshness |  |  |  | not run |
| Frontend tests |  |  |  | not run |
| Strict typecheck |  |  |  | not run |
| Lint |  |  |  | not run |
| Production build |  |  |  | not run |
| Contract-required rendered/manual workflow |  |  |  | not run |
| Diff/file-boundary/source-preservation checks |  |  |  | not run |

Add contract-specific required checks; do not delete inapplicable rows without a controlling contract reference that explicitly excludes them.

## Definition of Done

- [ ] All authorized milestones complete.
- [ ] All mandatory acceptance criteria have objective PASS evidence.
- [ ] All deterministic verification rows pass on the exact sealed commit.
- [ ] Required rendered/manual evidence passes on that commit.
- [ ] Source and prior-phase invariants pass; later phase remains untouched.
- [ ] Independent QA decision is PASS:
- [ ] Master gate decision is PASS:

## Recovery protocol

If any cited evidence becomes stale, the commit changes, or a correction is made, set the seal to INVALID, preserve it as historical evidence, rerun all affected verification, obtain required independent/master decisions for the new commit, and issue a new dated seal. Never edit evidence to conceal the invalidation.

## Allowed stopping conditions

- Stop without sealing when any required evidence/check/decision is missing, failed, skipped, stale, or blocked.
- Stop after a valid seal is recorded; the seal does not authorize preparation or implementation of the next phase.

## Gate evidence

- Verification summary:
- Independent QA PASS:
- Master gate PASS:
- Seal author/date:
- Exact next action authorized by a separate decision, if any: none unless explicitly recorded elsewhere.
