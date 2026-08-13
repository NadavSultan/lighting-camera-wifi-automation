# Wi-Fi assumptions

The authoritative conceptual configuration is `data/network/wifi-defaults.json`.

The current default is a 30 m radius circle around WIFI and SMART fixtures. LITE fixtures have no Wi-Fi circle. The radius is an `engineering_assumption` for early planning visualization, not measured, simulated, manufacturer-rated, or verified RF coverage.

The model deliberately excludes trees, buildings, terrain, antenna pattern and mounting height, frequency band, interference, channel planning, client density, required throughput, construction materials, seasonal foliage, and backhaul limitations.

Future Wi-Fi work must label outputs as conceptual until an approved RF design method and project inputs exist. A circle must not be described as service availability, signal level, throughput, capacity, or compliance. Distances and area operations must use the selected local projected CRS in metres, never raw WGS84 degrees.
