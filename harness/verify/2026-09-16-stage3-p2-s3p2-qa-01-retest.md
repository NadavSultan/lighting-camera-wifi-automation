# Independent QA addendum — 2026-09-16 — S3P2-QA-01 focused retest

Verdict: **PASS**

This addendum retests only `S3P2-QA-01`. It does not rewrite, replace, or amend
`harness/verify/2026-09-16-stage3-p2-usability-independent-qa-review.md`.
That original Independent QA review remains evidence as written (overall PASS;
BL-014 PASS with `S3P2-QA-01` Important and `S3P2-QA-02` Info). The original
review file hash at this writing is `40575df4fbf982628af9a134cca668feed1a8926`
(`git hash-object`). Original live JSON
`harness/verify/2026-09-16-stage3-p2-usability-independent-qa-live.json` and
scoped master `docs/post-roadmap-stage3-p2-scoped-master-decision-2026-09-16.md`
were not rewritten.

## Scope, independence, and non-goals

- Exact implementation commit/worktree reviewed: HEAD
  `fa1cbcadda93a0fb2ac0b31fdf1023a3ff5688d6` on `codex/bl-006-ies-associations`;
  dirty checkout including the implementer open-then-focus correction
  (`frontend/app/lib/cap-review-input.mjs`, `EngineeringWorkspace.tsx`).
- Controlling requirement: plan Task 9 / design Review-input guidance; master
  correction item 6 in
  `docs/post-roadmap-stage3-p2-scoped-master-decision-2026-09-16.md`.
- Reviewer/session independence: focused retest after implementer correction;
  no product files were edited in this retest session.
- Review scope: with Required CAP inputs collapsed, click the Product mapping
  **Review input** button and prove it opens that owning `<details>` and focuses
  `#cap-field-product_mapping`.
- Non-goals: no BL-013/BL-015 retest; no stored CAP recommend path; no product
  fixes; no commit/merge/push/seal; no BL-016/019/020; Phases 1–7 remain closed.

## QA milestones

| Milestone | Required evidence | Result |
|---|---|---|
| Repository/diff and authorization review | HEAD match; original QA/master files untouched; product correction present as dirty files | PASS |
| Deterministic verification | not re-run in this focused addendum (original QA already recorded) | not run |
| Acceptance-matrix review | only `S3P2-QA-01` | PASS |
| Rendered/manual workflow | isolated Vinext production UI `:3063` + isolated FastAPI `:8063` | PASS |
| Source/prior-phase regression review | Miracle Mile SHA-256; existing-pole import; no `:3000`/`:3012`/`:8000` reuse | PASS |

## Acceptance criteria

| Acceptance ID / criterion | Independent method | Evidence | Result |
|---|---|---|---|
| S3P2-QA-01 — Review input opens collapsed Required CAP inputs and focuses `#cap-field-product_mapping` | Playwright against isolated production Vinext of this checkout; click Product mapping Review input only (not `.first` after profile fill) | `harness/verify/2026-09-16-stage3-p2-s3p2-qa-01-retest.json`; screenshots `harness/tmp/stage3-p2-qa01-retest/screenshots/01-before-review.png` and `02-after-review.png` | **PASS** |

## Verification requirements

| Exact command/workflow | Commit/worktree | Exit/result | Notes |
|---|---|---|---|
| Isolated Vinext rebuild with `$env:NEXT_PUBLIC_API_URL="http://127.0.0.1:8063"` | `fa1cbca` dirty | 0 (historical in this session; dist already baked) | UI identity is `:3063`, not leftover `:3000`/`:3012`/`:3042` |
| `.\.venv\Scripts\python.exe harness\verify\run_stage3_p2_s3p2_qa01_retest.py` | `fa1cbca` dirty | 0 | Isolated `LCWA_DATA_DIR`; API `:8063`; UI `:3063`; system Chrome after bundled Chromium missing |

## Live probe

Started collapsed (`before.requiredOpen=false`,
`before.productMappingDetailsOpen=false`). Clicked the Product mapping
**Review input** (`review_button_count=1`). After:

- `requiredOpen=true`
- `productMappingDetailsOpen=true`
- `productMappingDetailsIsRequired=true`
- `activeId=cap-field-product_mapping`
- `activeTag=INPUT`
- `fieldVisible=true`
- page errors: none
- import SHA-256 `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`; 74 poles; `existing-poles`

The after screenshot shows Required CAP inputs expanded with the Product mapping
control ringed as focused.

## Findings

| ID | Severity | Requirement/evidence | Finding | Required correction |
|---|---|---|---|---|
| S3P2-QA-01 | closed on this dirty checkout | Plan Task 9 Review input; master correction item 6 | Product mapping Review input opens Required CAP inputs and focuses `#cap-field-product_mapping` | none for this item |

`S3P2-QA-02` and `S3P2-QA-03` were not retested. They remain as recorded in the
original Independent QA review.

## Definition of Done

- [x] Focused `S3P2-QA-01` live check completed on this dirty HEAD.
- [x] Started collapsed, opened owning `<details>`, focused `#cap-field-product_mapping`.
- [x] Original Independent QA review not rewritten.
- [x] No product fix, commit, merge, push, seal, or BL-016/019/020 work.

## Recovery protocol

1. First live launch failed because Playwright bundled Chromium was absent.
2. Recovered with system Chrome at `C:\Program Files\Google\Chrome\Application\chrome.exe`.
3. Same isolated ports and store; no product change.

## Verdict and next gate

- Verdict: **PASS** for `S3P2-QA-01` on this dirty checkout.
- Open findings from this addendum: none.
- Master gate eligibility: this addendum is independent retest evidence only.
  It does not rewrite the scoped master **NOT APPROVED** record and does not
  authorize merge, push, later backlog, or a seal.
- Exact next action: return to scoped master review using this addendum plus
  the preserved original Independent QA review.
