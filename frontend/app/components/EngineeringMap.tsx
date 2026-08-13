"use client";

import { useEffect, useRef } from "react";
import maplibregl, { type GeoJSONSource, type Map as MapLibreMap, type StyleSpecification } from "maplibre-gl";
import type { Feature, FeatureCollection, Point } from "geojson";
import type { EffectivePole, FixtureType, Project } from "../lib/types";
import { effectivePole } from "../lib/types";

const BASE_STYLE: StyleSpecification = {
  version: 8,
  sources: {
    osm: { type: "raster", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], tileSize: 256, attribution: "© OpenStreetMap contributors" },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};
const EMPTY: FeatureCollection<Point> = { type: "FeatureCollection", features: [] };
const CLICKABLE_LAYERS = ["poles-lite", "poles-wifi", "poles-smart", "poles-original"];

function features(project: Project | null): FeatureCollection<Point> {
  if (!project) return EMPTY;
  return {
    type: "FeatureCollection",
    features: project.source.poles.map((source): Feature<Point> => {
      const pole = effectivePole(project, source);
      return {
        type: "Feature",
        id: source.id,
        properties: { id: source.id, name: pole.displayName, fixture_type: pole.fixtureType, active: pole.active, modified: pole.modified },
        geometry: { type: "Point", coordinates: [source.longitude, source.latitude] },
      };
    }),
  };
}

function selectedFeature(pole: EffectivePole | null): FeatureCollection<Point> {
  if (!pole) return EMPTY;
  return { type: "FeatureCollection", features: [{ type: "Feature", properties: { id: pole.id }, geometry: { type: "Point", coordinates: [pole.longitude, pole.latitude] } }] };
}

export function EngineeringMap({ project, selected, onSelect, resizeSignal }: { project: Project | null; selected: EffectivePole | null; onSelect: (id: string) => void; resizeSignal: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const onSelectRef = useRef(onSelect);
  const fittedProjectRef = useRef<string | null>(null);

  useEffect(() => { onSelectRef.current = onSelect; }, [onSelect]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new maplibregl.Map({ container: containerRef.current, style: BASE_STYLE, center: [-80.2586, 25.74955], zoom: 15.7, attributionControl: false });
    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
    map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");
    map.on("load", () => {
      map.addSource("poles", { type: "geojson", data: EMPTY });
      map.addSource("selection", { type: "geojson", data: EMPTY });
      map.addLayer({ id: "poles-original", type: "circle", source: "poles", paint: { "circle-radius": 7, "circle-color": "#7f8d9b", "circle-opacity": .34, "circle-stroke-width": 1, "circle-stroke-color": "#d8e1e9", "circle-stroke-opacity": .42 } });
      const layers: Array<[FixtureType, string]> = [["LITE", "#ef4444"], ["WIFI", "#facc15"], ["SMART", "#3b82f6"]];
      for (const [fixture, color] of layers) {
        map.addLayer({
          id: `poles-${fixture.toLowerCase()}`,
          type: "circle",
          source: "poles",
          filter: ["all", ["==", ["get", "fixture_type"], fixture], ["==", ["get", "active"], true]],
          paint: { "circle-radius": ["case", ["boolean", ["get", "modified"], false], 5.5, 4.5], "circle-color": color, "circle-opacity": .92, "circle-stroke-width": ["case", ["boolean", ["get", "modified"], false], 2, 1], "circle-stroke-color": "#071018" },
        });
      }
      map.addLayer({ id: "selected-pole", type: "circle", source: "selection", paint: { "circle-radius": 11, "circle-color": "rgba(0,0,0,0)", "circle-stroke-width": 2, "circle-stroke-color": "#5de2c2", "circle-blur": .1 } });
      for (const layer of CLICKABLE_LAYERS) {
        map.on("click", layer, (event) => {
          const id = event.features?.[0]?.properties?.id as string | undefined;
          if (id) onSelectRef.current(id);
        });
        map.on("mouseenter", layer, () => { map.getCanvas().style.cursor = "pointer"; });
        map.on("mouseleave", layer, () => { map.getCanvas().style.cursor = ""; });
      }
    });
    mapRef.current = map;
    return () => { map.remove(); mapRef.current = null; };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const update = () => {
      (map.getSource("poles") as GeoJSONSource | undefined)?.setData(features(project));
      (map.getSource("selection") as GeoJSONSource | undefined)?.setData(selectedFeature(selected));
      const states: Array<[string, boolean]> = [
        ["poles-original", project?.layer_state.original_customer_poles ?? true],
        ["poles-lite", project?.layer_state.lite_fixtures ?? true],
        ["poles-wifi", project?.layer_state.wifi_fixtures ?? true],
        ["poles-smart", project?.layer_state.smart_fixtures ?? true],
      ];
      for (const [layer, visible] of states) if (map.getLayer(layer)) map.setLayoutProperty(layer, "visibility", visible ? "visible" : "none");
      if (project && project.source.poles.length && fittedProjectRef.current !== project.id) {
        const bounds = project.source.poles.reduce((result, pole) => result.extend([pole.longitude, pole.latitude]), new maplibregl.LngLatBounds());
        map.fitBounds(bounds, { padding: 70, maxZoom: 18, duration: 700 });
        fittedProjectRef.current = project.id;
      }
    };
    if (map.isStyleLoaded()) update(); else map.once("load", update);
  }, [project, selected]);

  useEffect(() => {
    const timer = window.setTimeout(() => mapRef.current?.resize(), 180);
    return () => window.clearTimeout(timer);
  }, [resizeSignal]);

  return <div ref={containerRef} className="map-container" aria-label="Interactive pole map" />;
}
