# Phase 2 corrective contract ratification

Ratification date: 2026-08-15

Authority: the user explicitly authorized corrective implementation of every approved Major finding IR-01 through IR-11 after the independent QA FAIL.

This is a retrospective ratification. The three Phase 2 operational contracts were not available as committed pre-implementation artifacts, which is the provenance failure recorded as IR-11 in `docs/phase-2-integration-review-and-qa.md`. This document does not backdate approval, assert that the original gate was satisfied, or modify the QA report.

The ratified corrective scope is:

- preserve the seven approved Phase 1 engineering catalogs unchanged at `1.0.0`;
- preserve all source poles, raw coordinate strings, numeric coordinates, and Phase 1 behavior;
- retain explicit Phoenix 1/Solitaire model selection with no family inference;
- retain the three Phase 2 operational catalog identities, advance them to `1.1.0`, and advance the project schema to `2.1.0` with compatibility migrations;
- add immutable fixture/camera/lens revision history and exact assignment pins;
- add safe lifecycle, IES, compatibility, bulk-selection, override-reset, and domain validation behavior required by IR-01 through IR-10;
- update generated Draft 2020-12 schemas and repository documentation; and
- exclude Phase 3 and all later calculations, projections, recommendations, and pole generation.

Acceptance remains pending independent QA retesting.
