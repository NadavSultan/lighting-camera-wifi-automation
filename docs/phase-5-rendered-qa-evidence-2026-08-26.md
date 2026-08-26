# Phase 5 rendered 74-pole workflow evidence

Date: 2026-08-26  
Disposition: implementation evidence only; awaiting master re-review and independent QA.

## Environment and commands

- Backend: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
- Frontend: production `node node_modules/vinext/dist/cli.js start --host 127.0.0.1 --port 3000`, after `node node_modules/vinext/dist/cli.js build`
- Browser: Codex in-app Browser via the repository-required browser-control workflow.
- Input: `Input/Miracle_Mile_Lighting_Poles.kml`
- Input SHA-256: `2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328`
- Input byte length: `34385`

## Observed rendered workflow

1. Imported the supplied KML through the visible Import KML/KMZ control. The rendered workspace reported `74 source poles`, `0` LITE, `0` WIFI, and `0` SMART before configuration; the validation card reported 74 point placemarks without geometry or coordinate errors. The first inspector showed the locked raw coordinate `-80.26234411,25.74920999,0`.
2. Applied Phoenix 1 WIFI to all 74 poles, set a 35 m Wi-Fi override, explicit enabled, and a bulk note. The rendered counters changed to WIFI `74`, with LITE and SMART remaining `0`. Then changed the project default to 40 m and applied bulk clear-radius plus clear-enabled-to-inherit. The inspector visibly reported `Inherit (true)`, no radius override, and `Effective radius: 40 m · project default inherited`.
3. Drew a separate four-vertex Wi-Fi area, named it `Rendered QA Coverage`, saved it, and calculated. The rendered result reported:
   - 74 circles
   - individual area `371815.208984 m²`
   - union `91075.840279 m²`
   - aggregate overlap `280739.368704 m²`
   - pairwise overlap `783037.421624 m²`
   - multiply-covered union `80211.336769 m²`
   - 467 overlap pairs
   - area covered `31094.635513 m²` (50.2%), uncovered `30814.201133 m²` (49.8%), boundary `214.692032 m` (21.3%).
4. Used the visible rename, redraw-from-empty, cancel, and delete controls. A bow-tie redraw was rejected with `Wi-Fi analysis area is self-intersecting`; the previously calculated 74-circle result and saved area revision remained present. A temporary separate area was created and deleted. The final valid area was named `Rendered QA Final`.
5. The visible map layer list kept `Conceptual Wi-Fi P5` separate from camera FOV/overlap, priority areas, and lighting calculation areas. Fixture counters and the rendered map retained the existing LITE/WIFI/SMART color mapping; the conceptual overlay was cyan and distinct. CAP controls remained disabled and labeled Phase 6.
6. Saved the project, exported project JSON and updated KML, and reopened `Miracle-Mile-Lighting-Poles.lighting-project.json` through the visible Open Project control. After reopen the rendered workspace still reported 74 source poles, 74 circles, `Rendered QA Final`, the conceptual disclaimer, the conceptual Wi-Fi overlay, and disabled CAP controls.
7. The exported updated KML contained 74 placemarks, contained no Wi-Fi coverage geometry markers, and retained the checked source coordinate. The source file was not edited.
8. Browser console diagnostics after the complete run reported zero error-level entries.

## Evidence boundaries

The browser-control session is genuine rendered UI evidence, not a static source assertion or backend-only probe. The repository's automated frontend suite remains SSR/helper based because the project does not include a browser-driver test harness; it ran 12 tests successfully. The rendered observations above are recorded separately so they are not misrepresented as those automated tests. Screenshot capture was not persisted because the deterministic DOM state, export artifacts, source hash, and browser diagnostics provide the relevant acceptance evidence without adding generated binary files to the repository.

