# Engineering assumptions

This register distinguishes governing conventions from temporary assumptions. Machine-readable values remain authoritative in the referenced catalogs.

## Approved project conventions

- Source technical files under `Input/` are immutable and retained byte-for-byte.
- WGS84 is for interchange/display; distance, area, coverage, and calculation grids use a selected local projected CRS in metres.
- Camera downward angle is measured below horizontal: 0 degrees horizontal and 90 degrees vertically down.
- LITE, WIFI, and SMART capabilities follow `data/fixtures/fixture-types.json`; CAP participation remains independently unresolved for each type.
- Unknown engineering values are null, carry `status: unknown`, and are not silently promoted to verified values.
- Calculation statistics are reported separately per polygon and grid points are clipped to the polygon boundary.

## Company-provided requirements

- SMART provides lighting and Wi-Fi and includes at least one integrated camera; WIFI provides lighting and Wi-Fi without cameras; LITE provides lighting only.
- Camera nominal class is Sony IMX477, 12 MP, 4:3, with a default 35-degree downward angle.
- Calculation defaults are a 0.00 m plane and 2.00 m X/Y grid spacing, with average/minimum/maximum illuminance, `Emin/Eavg`, and point count.
- Conceptual Wi-Fi circles apply only to WIFI and SMART.

## Temporary MVP assumptions

| Assumption | Authoritative record | Consequence |
|---|---|---|
| Conceptual Wi-Fi radius is 30 m | `data/network/wifi-defaults.json` | Enables later conceptual visualization only; not RF design. |
| Proposed photometric rotation order is local tilt followed by world-vertical azimuth | `docs/photometric-conventions.md` | Documentation proposal only; calculations remain blocked pending AGi32 validation. |
| Camera optical centers use immutable X/Y/Z=0 m offsets at the fixture origin | Mounting contract `fixed-zero-origin-1.0.0` | Approved for Phase 3 MVP; future authoritative mechanical offsets require a new pinned template revision. |
| Camera footprints intersect flat local ground at Z=0 | Geometry model `flat-ground-pinhole-1.0.0` | Approved for Phase 3 MVP; future authoritative terrain requires a separately reviewed model. |

No temporary CAP range, load, hop, redundancy, or fixture-compatibility assumption has been introduced.

## Values requiring future validation

- Camera manufacturer/enclosure identity and analytics capability. Phase 3 slot quantity, fixed relative azimuth, tilt, and zero-origin offsets are approved and operational.
- Solitaire 50 W filename/header versus `60W` internal luminaire identifier; D02 negative dimensions.
- Luminaire flux, CCT, mounting height, fixture-type compatibility, and C0-plane/housing orientation.
- CAP-to-JNET1 terminology, fixture/node applicability, recommended range/load/hops, antenna/LOS, redundancy, band, and site utilities.
- Wi-Fi RF inputs and performance criteria.
- Calculation-grid origin/boundary rules and approved lighting targets.

Values in this section must remain non-operational until resolved through the sources named in `docs/engineering-open-questions.md`.
