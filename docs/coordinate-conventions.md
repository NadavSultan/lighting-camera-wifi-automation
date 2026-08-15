# Coordinate conventions

## Geographic interchange

- KML/KMZ input and output: WGS84 longitude, latitude, optional altitude (`EPSG:4326`).
- Map display: Web Mercator tiles with WGS84 GeoJSON coordinates.
- Source coordinate strings are retained exactly as imported; numeric longitude/latitude values are stored alongside them for display and validation.

KML order is `longitude,latitude,altitude`. Latitude and longitude are never used directly for engineering distance or area.

## Projected engineering CRS

For each imported project, Phase 1 chooses the UTM zone containing the median project longitude and latitude:

- zone = floor((longitude + 180) / 6) + 1
- northern hemisphere: EPSG `32600 + zone`
- southern hemisphere: EPSG `32700 + zone`

The supplied Miracle Mile project resolves to WGS84 / UTM zone 17N (`EPSG:32617`). The selected CRS is stored in project metadata and used for duplicate-distance and geographic-outlier checks. A later phase may allow an engineer to override it for sites crossing UTM boundaries or requiring a local grid.

## Phase 3 camera frame and orientation

- Azimuth: degrees clockwise from true north; 0 north, 90 east, 180 south, 270 west.
- Luminaire tilt: must be defined with the selected photometric orientation before Phase 5. No rotation order is assumed in Phase 1.
- Camera downward angle: degrees below horizontal; 0 horizontal and 90 vertically downward. Phase 3 SMART templates fix this at 35 degrees; it is not a user-editable camera field.
- Projected axes are X east, Y north, Z up. Camera azimuth is clockwise from true north and normalized to `[0,360)`.
- Camera forward is `(sin(a) cos(t), cos(a) cos(t), -sin(t))`; camera right is `(cos(a), -sin(a), 0)`; image up is `(-sin(a) sin(t), -cos(a) sin(t), cos(t))`.
- Each Phase 3 camera optical center uses approved offsets `(0,0,0)` at projected source-pole X/Y and configured fixture height Z. Fixture azimuth rotates the fixture and both fixed camera slots together.
- Ground footprints, overlaps, and priority intersections use projected metres and square metres. WGS84 output rings exist only for map display/interchange.

## Validation

- Longitude must be in [-180, 180].
- Latitude must be in [-90, 90].
- Exact duplicate coordinates are warned.
- Near duplicates within 0.50 m are warned but not merged.
- Points more than 5 km from the projected median centre are warned as suspicious but never moved or removed.
