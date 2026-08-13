# Camera conventions

## Coordinate and angle convention

Camera downward angle is measured from the horizontal plane toward the ground:

- `0 deg_from_horizontal_down` means the optical axis is horizontal.
- `35 deg_from_horizontal_down` is the company-provided default.
- `90 deg_from_horizontal_down` means vertically downward.

Positive downward angles must not be converted to a conventional mathematical pitch without an explicit sign conversion. Camera azimuth, fixture-relative mounting axes, and mounting offsets remain undefined and must be approved before Phase 3 geometry.

## Catalog organization

`data/cameras/camera-catalog.json` is authoritative for shared camera/sensor data, lens configurations, and SMART-fixture integration defaults. Shared sensor and resolution values are stored once at camera-model level. Lens-specific focal length and FOV are stored under the lens record.

The catalog uses traceable values with one of the approved statuses: `manufacturer_specification`, `company_provided_requirement`, `engineering_assumption`, `derived_value`, or `unknown`. A null engineering value must be `unknown` and must explain the downstream dependency.

## Verified and unresolved values

The supplied workbook confirms three IMX477 lens rows, 4056 x 3040 pixels, 4:3 aspect ratio, and these real-angle pairs:

| Lens | Focal length | Horizontal FOV | Vertical FOV | State |
|---|---:|---:|---:|---|
| JL-LN039 | 6 mm | 52 deg | 40 deg | Workbook and brief agree |
| JL-LN042 | 3.9 mm | 69 deg | 54 deg | Workbook and brief agree |
| JL-LN037 | 3.56 mm | unresolved | 68 deg | Workbook says 87 deg horizontal; session brief says 90 deg |

The JL-LN037 active horizontal FOV is deliberately null. Both candidates remain traceable in the catalog until the owner identifies the intended engineering value.

Camera manufacturer/enclosure model, quantity per SMART fixture, mounting position and offsets, azimuth convention, and supported analytics are unknown. The presence of a geometric FOV must never be treated as evidence of analytics-quality coverage.

## Future geometry prerequisites

Phase 3 must not start camera-footprint calculations until it has an approved lens selection per camera, pole/fixture mounting height, camera quantity, local mounting axes and offsets, azimuth convention, terrain assumption, and a decision on the 87/90 degree discrepancy.
