# Calculation-area conventions

The authoritative definitions are in `data/standards/calculation-area-types.json`.

Four area types are available: Road, Sidewalk, Parking, and Other. Each polygon is an independent calculation/statistics unit. Defaults are a 0.00 m calculation plane and a 2.00 m by 2.00 m grid in the selected local projected CRS. Grid points are clipped to the polygon boundary.

Required per-polygon statistics are average, minimum, and maximum illuminance; uniformity `Emin / Eavg`; and calculation-point count. Illuminance is expressed in lux. Uniformity is dimensionless.

The grid-origin/phase convention, treatment of holes and multipolygons, inclusion tolerance for points exactly on a boundary, and behavior when a polygon contains zero points remain unresolved. Those choices can change point counts and statistics and must be frozen before Phase 5 validation.

No mandatory target illuminance or uniformity is present. Every target is null and `unknown` until an approved project standard or explicit company requirement is supplied.
