# Verification summary — 2026-09-07 — BL-004

**Item:** movable lighting-results card  
**Process:** item-based; independent QA pending

| ID | Result | Evidence |
|---|---|---|
| BL004-01 | PASS (code) | Calculate Lighting opens LightingResultCard for selected area near draft/ring anchor |
| BL004-02 | PASS (helper+UI) | clampCard tests; drag header + Reset/Close |
| BL004-03 | PASS (code) | unavailableReason when result missing; session-only state |
| BL004-04 | PASS | no schema/export mutation |

Frontend suite 49/49 + typecheck/lint/build PASS after wiring.
