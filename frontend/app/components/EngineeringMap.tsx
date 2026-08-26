"use client";

import { useEffect, useRef } from "react";
import maplibregl, { type GeoJSONSource, type Map as MapLibreMap, type Marker, type StyleSpecification } from "maplibre-gl";
import type { Feature, FeatureCollection, Geometry, LineString, Point, Polygon } from "geojson";
import type { EffectivePole, FixtureType, Project } from "../lib/types";
import { effectivePole } from "../lib/types";
import { fixtureAzimuthFromHandle } from "../lib/phase3-workflows.mjs";

const BASE_STYLE: StyleSpecification = {
  version: 8,
  sources: {
    osm: { type: "raster", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], tileSize: 256, attribution: "© OpenStreetMap contributors" },
  },
  layers: [{ id: "osm", type: "raster", source: "osm" }],
};
const EMPTY: FeatureCollection<Point> = { type: "FeatureCollection", features: [] };
const EMPTY_GEOMETRY: FeatureCollection<Geometry> = { type: "FeatureCollection", features: [] };
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

function cameraFeatures(project: Project | null): FeatureCollection<Polygon> {
  return { type: "FeatureCollection", features: project?.camera_geometry.footprints.filter((item) => item.valid && item.wgs84_coordinates).map((item) => ({ type: "Feature", properties: { id: `${item.pole_id}/${item.camera_slot_id}`, slot: item.camera_slot_id }, geometry: { type: "Polygon", coordinates: [item.wgs84_coordinates!] } })) ?? [] };
}

function overlapFeatures(project: Project | null): FeatureCollection<Polygon> {
  return { type: "FeatureCollection", features: project?.camera_geometry.overlaps.flatMap((item) => item.wgs84_coordinates.map((ring) => ({ type: "Feature" as const, properties: { area_m2: item.intersection_area_m2 }, geometry: { type: "Polygon" as const, coordinates: [ring] } }))) ?? [] };
}

function priorityFeatures(project: Project | null): FeatureCollection<Polygon> {
  return { type: "FeatureCollection", features: project?.priority_areas.map((area) => ({ type: "Feature", id: area.id, properties: { id: area.id, name: area.name }, geometry: { type: "Polygon", coordinates: [area.wgs84_coordinates] } })) ?? [] };
}

function calculationAreaFeatures(project: Project | null): FeatureCollection<Polygon> {
  return { type: "FeatureCollection", features: project?.calculation_areas.map((area) => ({ type: "Feature", id: area.id, properties: { id: area.id, name: area.name, classification: area.classification, warning: area.calculation_state.warnings.length > 0 }, geometry: { type: "Polygon", coordinates: [area.wgs84_coordinates] } })) ?? [] };
}

function calculationPointFeatures(project: Project | null): FeatureCollection<Point> {
  const results = project ? Object.values(project.lighting_calculations.results) : [];
  return { type: "FeatureCollection", features: results.flatMap((result) => result.points.map((point) => ({ type: "Feature" as const, id: point.id, properties: { id: point.id, area_id: result.calculation_area_id, lux: point.maintained_horizontal_illuminance_lux }, geometry: { type: "Point" as const, coordinates: point.wgs84_coordinate } }))) };
}

function wifiFeatures(project: Project | null): FeatureCollection<Polygon> {
  return { type: "FeatureCollection", features: project?.wifi_coverage.result?.circles.map((circle) => ({ type: "Feature" as const, id: circle.id, properties: { id: circle.id, pole_id: circle.pole_id, radius_m: circle.effective_radius_m, conceptual: true }, geometry: { type: "Polygon" as const, coordinates: [circle.wgs84_ring] } })) ?? [] };
}

function wifiAreaFeatures(project: Project | null): FeatureCollection<Polygon> {
  return { type: "FeatureCollection", features: project?.wifi_analysis_areas.map((area) => ({ type: "Feature" as const, id: area.id, properties: { id: area.id, name: area.name }, geometry: { type: "Polygon" as const, coordinates: [area.wgs84_coordinates] } })) ?? [] };
}

function cameraWarningFeatures(project: Project | null): FeatureCollection<Point> {
  if (!project) return EMPTY;
  const warningPoleIds = new Set(project.camera_geometry.footprints.filter((item) => item.enabled && item.warnings.length > 0).map((item) => item.pole_id));
  return { type: "FeatureCollection", features: project.source.poles.filter((pole) => warningPoleIds.has(pole.id)).map((pole) => ({ type: "Feature", properties: { id: pole.id }, geometry: { type: "Point", coordinates: [pole.longitude, pole.latitude] } })) };
}

function draftFeature(points: Array<[number, number]>): FeatureCollection<LineString | Polygon> {
  if (points.length < 2) return { type: "FeatureCollection", features: [] };
  return { type: "FeatureCollection", features: [{ type: "Feature", properties: {}, geometry: points.length >= 3 ? { type: "Polygon", coordinates: [[...points, points[0]]] } : { type: "LineString", coordinates: points } }] };
}

export function EngineeringMap({ project, selected, onSelect, onFixtureAzimuthChange, drawingPriorityArea, priorityDraft, onPriorityDraftPoint, onSelectPriorityArea, drawingCalculationArea, calculationDraft, onCalculationDraftPoint, onSelectCalculationArea, drawingWifiArea, wifiDraft, onWifiDraftPoint, resizeSignal }: { project: Project | null; selected: EffectivePole | null; onSelect: (id: string) => void; onFixtureAzimuthChange: (azimuth: number) => void; drawingPriorityArea: boolean; priorityDraft: Array<[number, number]>; onPriorityDraftPoint: (coordinate: [number, number]) => void; onSelectPriorityArea: (id: string) => void; drawingCalculationArea: boolean; calculationDraft: Array<[number, number]>; onCalculationDraftPoint: (coordinate: [number, number]) => void; onSelectCalculationArea: (id: string) => void; drawingWifiArea: boolean; wifiDraft: Array<[number, number]>; onWifiDraftPoint: (coordinate: [number, number]) => void; resizeSignal: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const onSelectRef = useRef(onSelect);
  const fittedProjectRef = useRef<string | null>(null);
  const azimuthMarkerRef = useRef<Marker | null>(null);
  const drawingRef = useRef(drawingPriorityArea);
  const onDraftPointRef = useRef(onPriorityDraftPoint);
  const onPrioritySelectRef = useRef(onSelectPriorityArea);
  const drawingCalculationRef = useRef(drawingCalculationArea);
  const onCalculationDraftPointRef = useRef(onCalculationDraftPoint);
  const onCalculationSelectRef = useRef(onSelectCalculationArea);
  const drawingWifiRef = useRef(drawingWifiArea);
  const onWifiDraftPointRef = useRef(onWifiDraftPoint);

  useEffect(() => { onSelectRef.current = onSelect; }, [onSelect]);
  useEffect(() => { drawingRef.current = drawingPriorityArea; onDraftPointRef.current = onPriorityDraftPoint; onPrioritySelectRef.current = onSelectPriorityArea; drawingCalculationRef.current = drawingCalculationArea; onCalculationDraftPointRef.current = onCalculationDraftPoint; onCalculationSelectRef.current = onSelectCalculationArea; drawingWifiRef.current = drawingWifiArea; onWifiDraftPointRef.current = onWifiDraftPoint; }, [drawingPriorityArea, onPriorityDraftPoint, onSelectPriorityArea, drawingCalculationArea, onCalculationDraftPoint, onSelectCalculationArea, drawingWifiArea, onWifiDraftPoint]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = new maplibregl.Map({ container: containerRef.current, style: BASE_STYLE, center: [-80.2586, 25.74955], zoom: 15.7, attributionControl: false });
    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
    map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");
    map.on("load", () => {
      map.addSource("poles", { type: "geojson", data: EMPTY });
      map.addSource("selection", { type: "geojson", data: EMPTY });
      map.addSource("camera-fov", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("camera-overlap", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("priority-areas", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("priority-draft", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("calculation-areas", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("wifi-coverage", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("wifi-analysis-areas", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("calculation-draft", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("wifi-draft", { type: "geojson", data: EMPTY_GEOMETRY });
      map.addSource("lighting-points", { type: "geojson", data: EMPTY });
      map.addSource("camera-warnings", { type: "geojson", data: EMPTY });
      map.addLayer({ id: "priority-area-fill", type: "fill", source: "priority-areas", paint: { "fill-color": "#f59e0b", "fill-opacity": .15 } });
      map.addLayer({ id: "priority-area-line", type: "line", source: "priority-areas", paint: { "line-color": "#fbbf24", "line-width": 2, "line-dasharray": [2, 1] } });
      map.addLayer({ id: "calculation-area-fill", type: "fill", source: "calculation-areas", paint: { "fill-color": "#14b8a6", "fill-opacity": .13 } });
      map.addLayer({ id: "calculation-area-line", type: "line", source: "calculation-areas", paint: { "line-color": ["case", ["boolean", ["get", "warning"], false], "#ff7a59", "#2dd4bf"], "line-width": 2.5 } });
      map.addLayer({ id: "wifi-coverage-fill", type: "fill", source: "wifi-coverage", paint: { "fill-color": "#06b6d4", "fill-opacity": .16, "fill-outline-color": "#67e8f9" } });
      map.addLayer({ id: "wifi-analysis-area-line", type: "line", source: "wifi-analysis-areas", paint: { "line-color": "#a3e635", "line-width": 2, "line-dasharray": [3, 2] } });
      map.addLayer({ id: "camera-1-fov", type: "fill", source: "camera-fov", filter: ["==", ["get", "slot"], "camera-1"], paint: { "fill-color": "#a78bfa", "fill-opacity": .27, "fill-outline-color": "#c4b5fd" } });
      map.addLayer({ id: "camera-2-fov", type: "fill", source: "camera-fov", filter: ["==", ["get", "slot"], "camera-2"], paint: { "fill-color": "#22d3ee", "fill-opacity": .24, "fill-outline-color": "#67e8f9" } });
      map.addLayer({ id: "camera-overlap-fill", type: "fill", source: "camera-overlap", paint: { "fill-color": "#ec4899", "fill-opacity": .48, "fill-outline-color": "#f9a8d4" } });
      map.addLayer({ id: "priority-draft-fill", type: "fill", source: "priority-draft", paint: { "fill-color": "#fb923c", "fill-opacity": .2, "fill-outline-color": "#fdba74" } });
      map.addLayer({ id: "calculation-draft-fill", type: "fill", source: "calculation-draft", paint: { "fill-color": "#14b8a6", "fill-opacity": .24, "fill-outline-color": "#5eead4" } });
      map.addLayer({ id: "wifi-draft-fill", type: "fill", source: "wifi-draft", paint: { "fill-color": "#06b6d4", "fill-opacity": .24, "fill-outline-color": "#67e8f9" } });
      map.addLayer({ id: "lighting-heat-points", type: "circle", source: "lighting-points", paint: { "circle-radius": ["interpolate", ["linear"], ["zoom"], 14, 2, 19, 7], "circle-color": ["interpolate", ["linear"], ["get", "lux"], 0, "#172554", 1, "#2563eb", 5, "#22d3ee", 15, "#facc15", 30, "#f97316", 60, "#ef4444"], "circle-opacity": .76, "circle-stroke-width": .4, "circle-stroke-color": "#ffffff" } });
      map.addLayer({ id: "lighting-calculation-points", type: "circle", source: "lighting-points", paint: { "circle-radius": 1.4, "circle-color": "#f8fafc", "circle-opacity": .9 } });
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
      map.addLayer({ id: "camera-warning-indicator", type: "circle", source: "camera-warnings", paint: { "circle-radius": 12, "circle-color": "rgba(0,0,0,0)", "circle-stroke-width": 4, "circle-stroke-color": "#ff7a59", "circle-opacity": .95 } });
      map.addLayer({ id: "selected-pole", type: "circle", source: "selection", paint: { "circle-radius": 11, "circle-color": "rgba(0,0,0,0)", "circle-stroke-width": 2, "circle-stroke-color": "#5de2c2", "circle-blur": .1 } });
      for (const layer of CLICKABLE_LAYERS) {
        map.on("click", layer, (event) => {
          const id = event.features?.[0]?.properties?.id as string | undefined;
          if (id) onSelectRef.current(id);
        });
        map.on("mouseenter", layer, () => { map.getCanvas().style.cursor = "pointer"; });
        map.on("mouseleave", layer, () => { map.getCanvas().style.cursor = ""; });
      }
      map.on("click", "camera-warning-indicator", (event) => { const id = event.features?.[0]?.properties?.id as string | undefined; if (id) onSelectRef.current(id); });
      map.on("click", "priority-area-fill", (event) => { const id = event.features?.[0]?.properties?.id as string | undefined; if (id) onPrioritySelectRef.current(id); });
      map.on("click", "calculation-area-fill", (event) => { const id = event.features?.[0]?.properties?.id as string | undefined; if (id) onCalculationSelectRef.current(id); });
      map.on("click", (event) => { if (drawingRef.current) onDraftPointRef.current([event.lngLat.lng, event.lngLat.lat]); else if (drawingCalculationRef.current) onCalculationDraftPointRef.current([event.lngLat.lng, event.lngLat.lat]); else if (drawingWifiRef.current) onWifiDraftPointRef.current([event.lngLat.lng, event.lngLat.lat]); });
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
      (map.getSource("camera-fov") as GeoJSONSource | undefined)?.setData(cameraFeatures(project));
      (map.getSource("camera-overlap") as GeoJSONSource | undefined)?.setData(overlapFeatures(project));
      (map.getSource("priority-areas") as GeoJSONSource | undefined)?.setData(priorityFeatures(project));
      (map.getSource("priority-draft") as GeoJSONSource | undefined)?.setData(draftFeature(priorityDraft));
      (map.getSource("calculation-areas") as GeoJSONSource | undefined)?.setData(calculationAreaFeatures(project));
      (map.getSource("wifi-coverage") as GeoJSONSource | undefined)?.setData(wifiFeatures(project));
      (map.getSource("wifi-analysis-areas") as GeoJSONSource | undefined)?.setData(wifiAreaFeatures(project));
      (map.getSource("calculation-draft") as GeoJSONSource | undefined)?.setData(draftFeature(calculationDraft));
      (map.getSource("wifi-draft") as GeoJSONSource | undefined)?.setData(draftFeature(wifiDraft));
      (map.getSource("lighting-points") as GeoJSONSource | undefined)?.setData(calculationPointFeatures(project));
      (map.getSource("camera-warnings") as GeoJSONSource | undefined)?.setData(cameraWarningFeatures(project));
      const states: Array<[string, boolean]> = [
        ["poles-original", project?.layer_state.original_customer_poles ?? true],
        ["poles-lite", project?.layer_state.lite_fixtures ?? true],
        ["poles-wifi", project?.layer_state.wifi_fixtures ?? true],
        ["poles-smart", project?.layer_state.smart_fixtures ?? true],
        ["camera-1-fov", project?.layer_state.camera_fov ?? true],
        ["camera-2-fov", project?.layer_state.camera_fov ?? true],
        ["camera-overlap-fill", project?.layer_state.camera_overlap ?? true],
        ["priority-area-fill", project?.layer_state.priority_areas ?? true],
        ["priority-area-line", project?.layer_state.priority_areas ?? true],
        ["calculation-area-fill", project?.layer_state.calculation_areas ?? true],
        ["calculation-area-line", project?.layer_state.calculation_areas ?? true],
        ["lighting-calculation-points", project?.layer_state.calculation_points ?? true],
        ["lighting-heat-points", project?.layer_state.lighting_heat_map ?? true],
        ["wifi-coverage-fill", Boolean(project?.layer_state.wifi_coverage && project?.wifi_coverage.result)],
        ["wifi-analysis-area-line", project?.layer_state.wifi_coverage ?? false],
        ["camera-warning-indicator", project?.layer_state.warnings ?? true],
      ];
      for (const [layer, visible] of states) if (map.getLayer(layer)) map.setLayoutProperty(layer, "visibility", visible ? "visible" : "none");
      if (project && project.source.poles.length && fittedProjectRef.current !== project.id) {
        const bounds = project.source.poles.reduce((result, pole) => result.extend([pole.longitude, pole.latitude]), new maplibregl.LngLatBounds());
        map.fitBounds(bounds, { padding: 70, maxZoom: 18, duration: 700 });
        fittedProjectRef.current = project.id;
      }
    };
    if (map.isStyleLoaded()) update(); else map.once("load", update);
  }, [project, selected, priorityDraft, calculationDraft, wifiDraft]);

  useEffect(() => {
    azimuthMarkerRef.current?.remove();
    azimuthMarkerRef.current = null;
    const map = mapRef.current;
    const config = selected?.fixtureConfiguration;
    if (!map || !selected || selected.fixtureType !== "SMART" || !config) return;
    const radians = config.fixture_azimuth_deg * Math.PI / 180;
    const latitudeScale = 1 / 111320;
    const longitudeScale = 1 / (111320 * Math.cos(selected.latitude * Math.PI / 180));
    const position: [number, number] = [selected.longitude + 14 * Math.sin(radians) * longitudeScale, selected.latitude + 14 * Math.cos(radians) * latitudeScale];
    const element = document.createElement("div"); element.className = "azimuth-handle"; element.title = "Drag to rotate the fixture and both cameras";
    const marker = new maplibregl.Marker({ element, draggable: true }).setLngLat(position).addTo(map);
    marker.on("dragend", () => {
      const point = marker.getLngLat();
      onFixtureAzimuthChange(fixtureAzimuthFromHandle(selected.longitude, selected.latitude, point.lng, point.lat));
    });
    azimuthMarkerRef.current = marker;
    return () => { marker.remove(); if (azimuthMarkerRef.current === marker) azimuthMarkerRef.current = null; };
  }, [selected, onFixtureAzimuthChange]);

  useEffect(() => {
    const timer = window.setTimeout(() => mapRef.current?.resize(), 180);
    return () => window.clearTimeout(timer);
  }, [resizeSignal]);

  return <div ref={containerRef} className="map-container" aria-label="Interactive pole map" />;
}
