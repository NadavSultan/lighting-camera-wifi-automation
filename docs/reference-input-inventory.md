# Reference input inventory

## Customer KML

`Miracle_Mile_Lighting_Poles.kml` declares WGS84 and contains 74 valid Point placemarks in five folders:

- Cobra Head (40)
- Other (14)
- Decorative (10)
- Lighting and Camera (8)
- Environmental, Lighting and Camera (2)

Five source styles are present. Initial inventory found no exact coordinate duplicates, duplicate names, or unsupported placemarks. Bounding box: longitude -80.2627880119207 to -80.2548386156343; latitude 25.7491623586885 to 25.7498784611578. Folder names do not authorize fixture-type assignment; every pole defaults to LITE until edited.

## IES files

All four files declare `IESNA:LM-63-2002`, `TILT=NONE`, one lamp, 73 vertical angles, 145 horizontal angles, Type C photometry, and watts in the numeric header.

| File | Internal luminaire | Header watts | Note |
|---|---|---:|---|
| JLED-SL-100W-PHOENIX1-40-D01.ies | JLED-SL-100W-PHOENIX1-40-D01 | 100 | Naming aligns |
| JLED-SL-120W-PHOENIX1-40-D01.IES | JLED-SL-120W-PHOENIX1-40-D01 | 120 | Naming aligns |
| JLED-GL-050W-SOLITAIRE 3B-D01.IES | JLED-GL-60W-SOLITAIRE-D01 | 50 | Filename, internal model, and watts conflict |
| JLED-GL-050W-SOLITAIRE 3B-D02.ies | JLED-GL-60W-SOLITAIRE-D02 | 50 | Filename, internal model, and watts conflict; negative dimensions require review |

The files are now represented in `data/luminaires/ies-inventory.json` and `data/luminaires/luminaire-catalog.json`. Photometric coordinate/orientation approval and verified luminaire mapping remain required Phase 2/5 inputs.

## Camera workbook

`VideoCAD Camera Models - Juganu.Xlsx`, Sheet1, contains three Sony IMX477-family 4056 x 3040 (approximately 12.3 MP), 4:3 camera/lens rows:

- JL-LN039: 6 mm; real FOV 52 degrees horizontal / 40 degrees vertical.
- JL-LN042: 3.9 mm; real FOV 69 degrees horizontal / 54 degrees vertical.
- JL-LN037: 3.56 mm; real FOV 87 degrees horizontal / 68 degrees vertical. The user approved the workbook-backed value on 2026-08-14.

The workbook rows are now represented in `data/cameras/camera-catalog.json`. Camera quantity per fixture, mounting offsets, model naming, and analytics criteria remain unresolved; the earlier 87/90-degree FOV discrepancy is closed at 87/68 degrees.

## CAP datasheet

Source: `CAP datasheet.pdf`, Juganu `JL-DS-GC JNET1 GW _2308`, Rev 1.2, five pages. It describes a JNET1 Gateway/Group Controller rather than using the term CAP.

Explicit manufacturer statements:

- Page 1: up to 1000 nodes; claimed coverage up to 10 km open air and 8 km dense urban; wired RJ-45 or cellular IP backhaul; indoor 5 V/0.5 A USB; outdoor pole/wall enclosure; node roaming between gateways.
- Page 2: 433.05-434.79 MHz and 902-928 MHz bands; 100/500 kbps data rates; 10 dBm maximum output; source-routing tree; 64 hops maximum; IPv4; AES128-related security; indoor 2.5 W/IP20 and outdoor 20 W/IP65; -40 to +55 C.
- Page 4: 1000 nodes per gateway; maximum 16 children per parent; 60/300 ms minimum/maximum hop delay; aggregate goodput 40 kbps at 433 MHz and 200 kbps at 915 MHz; performance timing examples.
- Page 5: indoor/outdoor 433/915 MHz ordering variants.

Missing or ambiguous for recommendation logic:

- Which LITE/WIFI/SMART fixtures are JNET1 nodes.
- Recommended design range versus marketing maximum and the propagation assumptions behind either range.
- Line-of-sight, antenna pattern/height, mounting separation, interference margin, and region-specific legal band.
- Required redundancy, overlap, acceptable hop target, load/latency target, preferred/prohibited locations, electrical/backhaul availability, and field version applicability.

Traceable source-backed constraints and explicit missing information are now encoded in `data/network/cap-constraints.json`. No CAP recommendation logic is implemented or used in Phase 1.
