# LCWA web application review and usability report

Date: 2026-09-08. Status: findings and proposals only; this document does not authorize implementation.

## Conclusion

Fix display reliability first: workspace clipping, missing arrows, and lighting labels that do not follow the map. Then improve the results card and CAP workflow. A camera pixel-density map is a new engineering capability requiring a separate specification.

The review confirms several reported problems. Disappearance of the lighting card **while merely creating another polygon** was not conclusively reproduced: the first card remained during drawing and saving, then was replaced by the second card after another calculation. There is no evidence of lost stored calculation results.

## Tested version and environment

- Reviewed the work received from the second computer: branch `codex/bl-006-ies-associations`, commit `bc45b63da41092175f7fbda97bc4c24f1f39bfe9`. This is not `main`; findings apply to this version. No merge was performed.
- Chrome on Windows, 1920 x 855 CSS-pixel viewport, isolated local development frontend at `http://localhost:3058`, API on port 8058. Production and additional viewport testing remain required before accepting corrections.
- The environment used a copy of tracked frontend files and separate project/catalog storage under `harness/tmp/web-audit-2026-09-08`. User projects and product files were not edited.
- Opened a test project with 74 Miracle Mile poles. Configured Cobra Head 7 as Phoenix 1 SMART, height 8 m, fixture azimuth 0 degrees, two JL-LN039 lenses, and the Phoenix 100W IES. Created two lighting polygons and exercised calculation, zoom, CAP map focus, Wi-Fi, catalog association and background selection.
- CAP used **test-only inputs**, including one explicit candidate, 20 m link distance, 100-node limit, 16-child limit and 64-hop limit. These are not approved site-design values.
- Before/after `source` objects were equal. Original and archived KML SHA-256 matched: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`.
- Screenshots were inspected in the review conversation. Selected measurements and results are in the [evidence record](../harness/verify/2026-09-08-web-audit-observations.json). This is exploratory review, not full acceptance or reacceptance of Phases 1-7. Automated product test suites were not run during this review.

## Recommended order

| ID | Subject | Classification | Severity / priority | Route |
|---|---|---|---|---|
| WA-01 / BL-009 | Right inspector and toolbar clipping | Reproduced bug | High / P1 | Focused layout correction |
| WA-02 / BL-005 | Missing arrows and unavailable-direction badges | Reproduced bug | High / P1 | Diagnosis, then correction |
| WA-03 / BL-010 | Lux labels remain at old screen positions | Reproduced bug | High / P1 | Diagnosis, then correction |
| WA-04 / BL-011 | Lighting card hides core statistics | Reproduced usability bug | Medium / P1 | Focused correction |
| WA-05 / BL-012 | Initial lighting-card position | Bug with live positioning and code evidence | Medium / P2 | Focused correction |
| WA-06 / BL-013 | Revisit results across multiple areas | Usability improvement | Medium / P2 | Scoped task |
| WA-07 / BL-014 | Result-first CAP workflow | Usability improvement | Medium / P2 | Focused UI contract |
| WA-08 / BL-015 | Explain camera projection boundary | Usability improvement | Low / P2 | Explanation and legend task |
| WA-09 / BL-016 | Camera pixel-density map | New feature | Not a defect / P3 | Separate engineering contract |
| WA-10 / BL-017 | Tiny positive illuminance displayed as zero | Numeric presentation improvement | Medium / P2 | Focused presentation task |
| WA-11 / BL-018 | Left-panel overload and horizontal scrolling | Usability improvement | Medium / P2 | UI organization task |
| WA-12 / BL-019 | Phase messages contradict available capabilities | Content bug | Low / P3 | Focused content correction |
| WA-13 / BL-020 | Duplicate React warning keys | Technical bug observed in logs | Low / P3 | Focused correction |

P1: before expanding capabilities. P2: next usability round. P3: after stabilization or a product decision. This order does not authorize any item.

## Findings

### WA-01 — Right inspector clipping

- **Current behavior and reproduction:** Open a project and select a pole at 1920 x 855. `.workspace` measures 2045.78 px wide; the right inspector starts at 1727.78 and ends at 2045.78. About 126 px extend beyond the viewport. Fixture fields, the collapse button and part of the toolbar are clipped.
- **Expected:** All fields and actions remain accessible within the window; resizing must not hide essential controls.
- **Subsystem:** App shell, toolbar, CSS grid and properties inspector.
- **Dependencies and risks:** Intrinsic minimum widths and a long toolbar. Layout changes may require `map.resize` and affect overlay anchoring. Intrinsic sizing is a diagnostic lead, not a root cause proven through a correction.
- **Acceptance and verification:** Live checks at widths 1920, 1440, 1366 and 1024; collapse both side panels; browser zoom 100%/125%; keyboard access. No inaccessible off-screen controls or page-wide horizontal scrolling. Run relevant frontend layout checks.
- **Contract impact:** Phase 1 presentation correction; no data or calculation change.

### WA-02 — Missing fixture arrows

- **Current behavior and reproduction:** Open the test project, explicitly configure SMART and azimuth 0 degrees, wait and change zoom. Per-fixture arrows and `?` badges were not visible. The selected fixture's circular rotation handle was visible; it does not replace arrows for every fixture.
- **Evidence:** The display-preview endpoint returned one valid direction and 73 unavailable entries. Do not assume all imported poles have a configured direction; distinguish known direction from missing information.
- **Expected:** A readable arrow attached to each configured fixture, rotating correctly with the map, plus missing-information indications required by BL-005.
- **Subsystem:** `EngineeringMap.tsx`, direction canvas and preview request.
- **Dependencies and risks:** Canvas/requestAnimationFrame lifecycle. Cleanup cancels a frame without resetting its stored ID; a stalled scheduler is a plausible hypothesis requiring proof. Preserve LITE/WIFI/SMART colors, inactive styling and explicit direction inputs.
- **Acceptance and verification:** Azimuths 0/90/180/270, missing configuration, selection changes, rapid edits, reload, rotation/zoom/pan, layer toggles and both backgrounds. Test production as well as development. Prove canceled frames cannot disable later drawing; compare preview output with screenshot arrow positions.
- **Contract impact:** Complete BL-005 presentation behavior only. Do not invent azimuths or move poles. The original BL-005 improvement classification remains historical; this follow-up is a bug.

### WA-03 — Lux labels detach from their points

- **Current behavior and reproduction:** Calculate two areas, change zoom, then click CAP `Show selected sites on map`. A label cluster remained around screen x400/y480 while area geometry moved toward the map center. A later screenshot after movement settled showed the same issue. Labels also overlapped densely at this zoom.
- **Expected:** Every label stays attached to its point throughout map movement. Dense labels must not imply values at unrelated locations.
- **Subsystem:** `LightingPointLabels.tsx`; BL-007.
- **Dependencies and risks:** Scheduled canvas drawing, frame cleanup, transforms and DPR. The same cancellation-without-ID-reset pattern appears here. Do not conclude that arrows and labels share a root cause without proof.
- **Acceptance and verification:** Pan, zoom, fit/Locate, rotation, resize, recalculation, layer toggles and alternative background. After every action, labels align with their points. Define readable dense-grid behavior while retaining access to every exact point value.
- **Contract impact:** Phase 4 / BL-007 display correction. Do not change results or thin the calculation grid to simplify rendering.

### WA-04 — Lighting card hides uniformity and clips statistics

- **Current behavior and reproduction:** Calculate the first area. The card is 280 px wide and 220 px high, with 436 px of content. Eavg and Emin are visible, Emax is clipped, and Emin/Eavg and Emin/Emax require scrolling. The title wraps. Card-body CSS exists, but its match to the current markup needs inspection.
- **Expected:** Area name, average, minimum, maximum and uniformity are readable together. Details, assumptions and warnings remain accessible at a secondary level. Dragging the card must not accidentally move the map.
- **Subsystem:** `LightingResultCard.tsx` and styles; BL-004.
- **Dependencies and risks:** Limited map space; do not remove assumptions or present stale results as current.
- **Acceptance and verification:** Core metrics visible on opening; drag, Close, Reset, small viewport, long names and unavailable-result state. Drawing outside the card remains usable. Full drag verification was not completed in this review.
- **Contract impact:** Presentation only; preserve Phase 4 formulas and uniformity ratios.

### WA-05 — Card anchor is not beside the polygon finish point

- **Current behavior and reproduction:** The first area ended around screen 390,505; its card opened at 286,459 near the map's left edge. Code subtracts `container.left/top` from `map.project`, although the latter already returns map-container-relative coordinates. Verify the complete coordinate chain before correcting it.
- **Expected:** Open beside the final vertex, with a small offset and containment within the map. Reset returns to that anchor.
- **Subsystem:** Lighting-card anchoring and clamping.
- **Dependencies and risks:** WA-01; changing card dimensions, panel collapse and dragged versus anchored state.
- **Acceptance and verification:** Polygons near all four corners and the center; a map whose screen origin is not 0,0; pan/zoom, collapse and dragging. Measure card-to-anchor position in the browser. Resizing must keep dragged cards accessible.
- **Contract impact:** BL-004 only; no calculation change.

### WA-06 — Revisit results for several areas

- **Current behavior and reproduction:** Area 1's card remained during drawing and saving area 2. Another calculation opened area 2 and replaced the first card. Code stores a single open-card ID. Both results remained stored: 192 and 68 points. The user's disappearance-during-drawing report remains open for focused diagnosis if it recurs.
- **Proposed expected behavior:** A compact area list with `Show results` for each area; return without recalculation and retain each area's card position during the session. Pinning two cards for comparison is optional, not an assumed approved requirement.
- **Subsystem:** Workspace, area selection and result cards.
- **Dependencies and risks:** WA-04/05, invalidation rules and polygon edits. Never confuse historical results with current results.
- **Acceptance and verification:** Two or more areas; select and revisit, create/cancel a draft, edit/delete and recalculate. Each card identifies its area and freshness state.
- **Contract impact:** BL-004 improvement. Persisting window layout in project JSON is outside the basic proposal and would require a separate compatibility decision.

### WA-07 — CAP: a simple result above advanced settings

- **Current behavior and reproduction:** With a complete test profile and eligible candidate, `Recommend CAP` returned one CAP, the pole name, Locate and map-display controls. With SMART set to non-node and no eligible nodes, it returned zero. Explicitly changing SMART to Node returned one. Node dispositions materially affect the result.
- **Proposed expected behavior:** Configure an approved engineering profile and surveyed candidate pool once. Then a primary `Calculate CAP recommendation` action presents the recommended count, highlighted sites, unresolved nodes and a short explanation. Advanced inputs are expandable. Missing prerequisites produce specific guidance rather than a misleading number.
- **Subsystem:** CAP Planning panel and map actions; follow-up to BL-008.
- **Dependencies and risks:** Approved profile, product limits, node eligibility and surveyed sites. Do not remove inputs from the model or promote test values to real defaults. The engine selects from approved candidates; it does not generate unrestricted positions or predict RF.
- **Acceptance and verification:** Zero nodes, missing inputs, one/multiple candidates, unresolved nodes, limits and constraints. Map and list agree; input changes invalidate old results; unapproved inputs cannot bypass blockers.
- **Contract impact:** UI simplification can preserve Phase 6. Recommendations without a profile or outside an approved pool change its contract and require a separate engineering decision and authorization.

### WA-08 — Meaning of Projection boundary

- **Current:** No exact UI text named `Projection boundary` was found in the inspected code. This explanation concerns the displayed FOV polygon boundary. If another marking was intended, identify it before changing behavior.
- **Code meaning:** `project_ground_footprint` constructs four rays through the field-of-view corners using height, fixture azimuth, mounting angle and H/V FOV. Their intersections with the Z=0 ground plane define a polygon. Horizontal/upward or unstable rays do not yield a valid finite footprint. This is a geometric projection onto flat ground, not detection range, image quality, resolution limit or proof of no obstruction.
- **Live example:** At 8 m height, H52/V40 degrees and 35 degrees downward tilt, the inspector reported two footprints of about 154.7 square metres each, at azimuths 290 and 70 degrees according to the fixture template.
- **Expected:** Short legend/help describing flat-ground projection, lens/height/angle inputs, and the distinction between footprint, overlap and image quality.
- **Subsystem, dependencies and risks:** Camera display and legend; existing geometry and terminology. Avoid implying detection capability that is not calculated.
- **Acceptance and verification:** Compare explanation with engine results for different lenses/heights and invalid inputs. No unsupported quality or occlusion claims.
- **Contract impact:** Clarification only; preserve Phase 3.

### WA-09 — Color-coded camera pixel-density map

- **Type and current behavior:** New feature. Current outputs include FOV footprints and overlaps, but no usable pixel-density calculation. Its absence is not a defect in the accepted engine.
- **Objective and expected behavior:** A color layer per camera inside its footprint, a `px/m` legend and point inspection, showing where image detail becomes less dense.
- **Subsystem:** Camera model, derived calculation, map layer and legend; exports only if separately authorized.
- **Dependencies and decisions before implementation:** Effective image resolution after crop/resize; FOV/lens; measurement surface (ground or vertical target at a defined height); horizontal/vertical density or a conservative metric. Decide color thresholds, overlap handling and unknown-data behavior. Density is not merely fixed distance rings: orientation and measurement surface matter.
- **Risks:** False precision, perspective effects, confusing px/m with person recognition, lens distortion and occlusion. Do not invent recognition/standard thresholds or combine overlapping-camera densities without an approved model.
- **Acceptance and verification:** Specify units and formulas; independently calculated reference cases; height/resolution/lens changes; correct camera association; FOV masking; explicit unknown state; consistent thresholds; representative performance. Preserve the original footprint and store derived data separately.
- **Contract impact:** Explicit extension beyond Phase 3; requires a dedicated contract and authorization. No Phase 8 is opened and no implementation is authorized here.

### WA-10 — Nonzero values displayed as 0.00

- **Current behavior and reproduction:** Area 2 displayed Eavg/Emin/Emax as `0.00 lx`, alongside Emin/Eavg=0.632. Underlying values were respectively 0.0000359329, 0.0000227035 and 0.0000682324 lx. This evidence does not establish a calculation error; rounding hides information.
- **Expected:** For example, `<0.01 lx` for a positive value below display precision, with access to the detailed value. Distinguish zero, null and tiny positive values.
- **Subsystem:** Numeric formatting in cards, labels and summaries.
- **Dependencies and risks:** A consistent precision policy; never round stored results or derive ratios from formatted strings.
- **Acceptance and verification:** Exact zero, null, below-threshold, threshold and ordinary values. Uniformity ratios remain consistent with source values and explanation.
- **Contract impact:** Phase 4 presentation only.

### WA-11 — Organize the left workflow panel

- **Current behavior and reproduction:** Opening a project presents a long CAP form before Layers and Lighting. Left-panel content width measured 370 px against 262 px client width. Long controls clip and require horizontal scrolling. Part of the lighting drawing workflow is deep below CAP and reporting.
- **Proposed expected behavior:** Select a Lighting / Camera / Wi-Fi / CAP workspace with relevant controls, accessible layers and expandable advanced details. CAP survey and destructive actions should not have the same prominence as everyday results.
- **Subsystem, dependencies and risks:** Navigation/panels; WA-01 and CAP workflow. Do not hide blockers or essential inputs in an unclear tab.
- **Acceptance and verification:** Reach configuration, calculation and results for each discipline without searching through another discipline's form. Ordinary fields do not clip or require horizontal scrolling. Switching disciplines preserves selection/drafts or clearly explains the state change.
- **Contract impact:** UI improvement; no algorithm or mandatory-input change.

### WA-12 — Outdated phase messages

- **Current behavior and reproduction:** While Report Package is available, the inspector still says reporting remains gated. A Phase 4 map message also appears during camera/CAP work. Available capabilities contradict the text.
- **Expected:** Describe actual capabilities and limits. Keep phase history in project documentation rather than incorrect warnings about available actions.
- **Subsystem:** Workspace/inspector text.
- **Dependencies and risks:** Current acceptance records; do not broaden unsupported RF or professional-design claims.
- **Acceptance and verification:** Review discipline-specific text against Phase 1-7 gates. Describe available engineering reports accurately while preserving calculation limitations.
- **Contract impact:** Content correction only, not a gate change.

### WA-13 — Duplicate keys in warning lists

- **Current behavior and reproduction:** After CAP actions, the development-server log reported React children sharing the key `Single-CAP conceptual plan; single point of failure is not mitigated by this graph result.`. This review did not establish that a warning disappeared from the UI. The issue matches a technical observation already mentioned in earlier code review.
- **Expected:** Required warnings render consistently without duplicate keys when results update.
- **Subsystem:** React CAP/report warning lists. Low severity, P3.
- **Dependencies and risks:** Identify the exact list; do not delete warning data merely to silence the log.
- **Acceptance and verification:** Repeat recommendation and display the same warning from multiple sources. No duplicate-key error; all required warning text remains. Focused frontend check plus live verification.
- **Contract impact and route:** Small technical correction without changing Phase 6/7 or warning meaning.

## Working behavior and review limits

- Project JSON opened, source data remained unchanged, and an IES was uploaded and associated with SMART. Exhaustive three-type association combinations were not tested in this review.
- Two lighting areas calculated and retained their results; the first average was 13.0629037 lx. This is not professional photometric validation.
- Wi-Fi calculated a conceptual circle and displayed it after explicit Show coverage. No circle-rendering failure was found in this case.
- CAP returned a count and site from the test pool; real-site quality and optimality were not evaluated.
- Satellite returned `Satellite imagery is not configured` without provider environment variables. This is expected, not a provider bug. Actual imagery loading and live tile switching were not tested.
- No comprehensive export/report, drawing/Undo, touch, other viewport or production testing was performed. Unconfirmed findings remain labeled as such.

## Cursor handoff readiness

These two documents are ready for **intake, diagnosis and task preparation** in Cursor. They are not a complete implementation plan or blanket implementation authorization. Read them together with the repository, linked evidence and current controlling contracts; copying only these two files does not supply the full engineering context.

Before implementing a selected item:

1. Read the required repository startup documents and current scoped decisions. Inspect the actual branch, HEAD and diff on that computer; the review baseline may have changed. Do not overwrite newer work or silently merge the reviewed branch into main.
2. Obtain explicit authorization naming the item. Preserve each item's independent scope; authorization for translation or this report is not authorization for product changes.
3. Reproduce the issue on that checkout. Confirm suspected causes rather than treating the canvas lifecycle or coordinate hypotheses as proven.
4. Record a short item-specific execution plan: authorized file boundary, concrete changes, dependencies, acceptance criteria, exact applicable verification commands and live-browser scenarios. Follow the repository work-record and evidence requirements where applicable.
5. Implement and verify only the authorized item. Preserve Input, source bytes, pole coordinates, calculation semantics and existing gates. Record the tested commit, results, warnings and remaining limitations.

**Readiness by route:** The narrow corrective items have enough evidence to begin diagnosis once assigned; their exact patch plan must follow reproduction. BL-013, BL-014 and BL-018 require a settled UI scope before behavior changes. BL-016 requires an approved engineering contract covering resolution, measurement surface, density metric, thresholds and overlap semantics before implementation. Satellite remains a separate configuration-and-live-verification follow-up under BL-001; this review did not establish an imagery defect.

The existing 2026-09-06 implementation plan covers the earlier backlog round. It must not be treated as a ready-made execution plan for all findings added on 2026-09-08. Do not convert this exploratory review into a PASS for any accepted gate.
