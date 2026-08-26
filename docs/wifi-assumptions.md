# Wi-Fi assumptions

The authoritative conceptual configuration is `data/network/wifi-defaults.json`.

The current default is a 30 m radius circle around WIFI and SMART fixtures. LITE fixtures have no Wi-Fi circle. The radius is an `engineering_assumption` for early planning visualization, not measured, simulated, manufacturer-rated, or verified RF coverage.

The model deliberately excludes trees, buildings, terrain, antenna pattern and mounting height, frequency band, interference, channel planning, client density, required throughput, construction materials, seasonal foliage, and backhaul limitations.

Future Wi-Fi work must label outputs as conceptual until an approved RF design method and project inputs exist. A circle must not be described as service availability, signal level, throughput, capacity, or compliance. Distances and area operations must use the selected local projected CRS in metres, never raw WGS84 degrees.

Phase 5 implements model `conceptual-circle-1.0.0`: a deterministic 128-sided projected-plane buffer (`quad_segs=32`) around an effective existing-pole coordinate. It persists separately transformed WGS84 display rings, aggregate union/overlap statistics, and optional statistics for explicitly user-drawn `wifi_analysis_areas`. It does not persist pair geometries or multiplicity histograms. Safety limits are 500 eligible circles, 64,500 circle-ring vertices, 50,000 indexed candidate/intersection operations, 200 analysis areas, 10,000 vertices per area, and 250,000 total persisted geometry vertices. The exact disclaimer shown with results is: “Conceptual geometric visualization only; not verified RF coverage, performance, capacity, service quality, or standards compliance.”
