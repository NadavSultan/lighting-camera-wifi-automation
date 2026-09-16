# Scoped master decision — post-roadmap Stage 3 P2 usability

Date: 2026-09-16

Decision: **PASS — Stage 3 P2 accepted**

This is the final item-based scoped master review for BL-013 / WA-06, BL-014 / WA-07, and BL-015 / WA-08 on the dirty implementation worktree at `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6`. It incorporates the preserved original Independent QA review and the focused `S3P2-QA-01` retest addendum. It is not a phase seal, does not create Phase 8, and does not authorize merge, push, later backlog items, or the next stage.

## Identity and evidence reviewed

- Branch: `codex/bl-006-ies-associations`
- Base HEAD: `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6`
- Implementation identity: uncommitted product, tests, execution-index, and harness records on that HEAD
- Controlling design: `docs/superpowers/specs/2026-09-16-stage3-p2-usability-design.md`
- Execution plan: `docs/superpowers/plans/2026-09-16-stage3-p2-usability.md`
- Independent QA: `harness/verify/2026-09-16-stage3-p2-usability-independent-qa-review.md`
- Focused Independent QA retest: `harness/verify/2026-09-16-stage3-p2-s3p2-qa-01-retest.md`

The dirty diff remains within the authorized frontend presentation, tests, and evidence boundary. No backend, schema, catalog, lockfile, or `Input/` changes were found. User-owned `.superpowers/` remains excluded.

## Acceptance disposition

| Item | Master result | Disposition |
|---|---|---|
| BL-013 / WA-06 | PASS | Stored lighting results can be revisited without recalculation; one card remains visible; per-area session positions restore; draft/edit/delete behavior is supported by independent rendered evidence. |
| BL-014 / WA-07 | PASS | The result-first layout and primary recommendation action are present. The corrected **Review input** action opens a collapsed Required CAP inputs section, reveals the exact blocker target, scrolls it into view, and moves keyboard focus without mutating CAP inputs or eligibility. |
| BL-015 / WA-08 | PASS | The camera projection-boundary explanation uses the approved flat-ground meaning and makes no pixel-density, detection, recognition, terrain, occlusion, or visibility claim. |

## Closure of S3P2-QA-01

The bounded correction is accepted:

1. `openAndFocusCapReviewTarget` opens the target's owning closed `<details>` element before attempting focus.
2. It waits for the revealed content, then scrolls and focuses the exact mapped target.
3. Existing blocker identities and `blockerFocusTarget` mappings remain unchanged.
4. The correction does not auto-fill inputs, change CAP eligibility, bypass `capOperationEnabled`, or alter Phase 6 calculations.
5. Focused automated coverage exercises closed and already-open sections and the workspace wiring.
6. Independent production-browser retest began with Required CAP inputs collapsed and proved that the Product mapping action opened the section and focused `#cap-field-product_mapping`, with zero captured page errors.

`S3P2-QA-01` is closed.

## Other QA findings

- `S3P2-QA-02` is accepted as non-blocking residual evidence. The stored CAP-result variants are covered by helper/source tests; no claim is made that Independent QA produced a live eligible recommendation.
- `S3P2-QA-03` is informational. Rendering `primary.label` instead of identical hardcoded copy is optional and is not authorized as required remediation.

## Fresh master verification

| Check | Result |
|---|---|
| `corepack pnpm run typecheck` | PASS |
| `corepack pnpm run lint` | PASS |
| `corepack pnpm run test` | PASS — 98 passed, 0 failed |
| `corepack pnpm run build` | PASS; existing advisories only |
| `scripts/validate_engineering_data.py` | PASS |
| `git diff --check` | PASS |
| `git diff --exit-code -- Input` | PASS |
| Protected backend/schema/catalog/lockfile diff | PASS; empty |
| Miracle Mile KML SHA-256 | PASS — `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328` |
| Independent live evidence | BL-013, BL-014, BL-015, and Stage 2 regression evidence reviewed; zero captured browser errors; `S3P2-QA-01` independently reproduced |
| Focused Independent QA retest | PASS — collapsed Required CAP inputs opened; `#cap-field-product_mapping` became visible and focused; zero captured page errors |

## Gate decision

| Question | Answer |
|---|---|
| BL-013 accepted | YES |
| BL-014 accepted | YES — `S3P2-QA-01` closed by focused retest |
| BL-015 accepted | YES |
| Overall Stage 3 P2 accepted | YES |
| Existing dirty worktree may be preserved | YES |
| One bounded implementation/evidence commit authorized | YES — include only Stage 3 P2 product, tests, execution-index, harness evidence, and this master decision |
| Merge, push, next stage, Phase 8, or seal authorized | NO |

## Exact next action

Create one bounded Stage 3 P2 implementation/evidence commit from this exact dirty worktree. Exclude `.superpowers/`, `docs/bl-016-camera-pixel-density-architecture.md`, caches, build output, runtime data, and every unrelated or user-owned file. After the commit, verify its identity and a clean scoped diff. Do not merge, push, prepare BL-016/019/020, begin another backlog stage, create Phase 8, or create a phase seal without separate authorization.
