import type { FeatureCollection, LineString, Point, Polygon } from "geojson";

export type LngLat = [number, number];

export type PolygonDraftCollections = {
  vertices: FeatureCollection<Point>;
  edges: FeatureCollection<LineString>;
  fill: FeatureCollection<Polygon>;
  preview: FeatureCollection<LineString>;
};

export function buildPolygonDraft(
  points: LngLat[],
  cursor?: LngLat | null,
): PolygonDraftCollections;

export function polygonDraftGuidance(vertexCount: number): string;
