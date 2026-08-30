# Proven blocker record — YYYY-MM-DD — Phase N

Status: **INVALID — INCOMPLETE TEMPLATE**

This record supports a stop only when all required fields are complete, the same condition survived at least three materially different safe recovery attempts, and no meaningful in-scope work can continue.

## Condition

- Exact affected milestone/acceptance IDs:
- Exact command/action and exit state:
- First occurrence timestamp and exact commit/worktree:
- Preserved output/evidence path:
- Artifacts that may be partial or stale:

## Why this is not ordinary repair work

- Why it is not a failing/missing test, incomplete milestone/coverage, build/lint/typecheck/compiler failure, generated drift, runtime-path issue, occupied port, temporary lock/cache, recoverable dependency install, dirty file, missing report, or response-turn boundary:
- Why meaningful in-scope work cannot continue elsewhere:

## Recovery attempts

| Attempt | Materially different safe approach | Exact command/action | Result/evidence | Why it did not resolve the same condition |
|---:|---|---|---|---|
| 1 |  |  | not run |  |
| 2 |  |  | not run |  |
| 3 |  |  | not run |  |

Repeating the same command without a changed input, environment, or repair does not count as a different attempt.

## Required external decision or change

- Exact new user authority, product decision, external-state change, or prohibited scope expansion required:
- Smallest safe option that would unblock execution:
- Work that remains authorized and why it cannot proceed first:

## Validity checklist

- [ ] Three materially different safe recovery attempts are recorded with evidence.
- [ ] The same condition remains after all three attempts.
- [ ] No meaningful in-scope work can continue.
- [ ] The required new decision/change is exact and cannot be inferred safely.
- [ ] Worktree, logs, partial artifacts, and last verified state are preserved.
- [ ] `OPERATIONS.md`, the phase work record, and execution log link this record.

Change status to **VALID — USER DIRECTION REQUIRED** only when every item is true. Otherwise continue the durable goal.
