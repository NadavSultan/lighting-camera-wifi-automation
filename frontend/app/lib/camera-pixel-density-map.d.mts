import type { FeatureCollection, Polygon } from "geojson";
import type { PixelDensityLegendDefinition, Project } from "./types";
export type DensityOverlapLabelPoint = { id: string; coordinate: [number, number]; label: string };
export type DensityInspection = { contributors: string[]; winner: string; winningBandId: string; multiplicity: number };
export function densityBandFeatures(project: Project): FeatureCollection<Polygon>;
export function densityOverlapFeatures(project: Project): FeatureCollection<Polygon>;
export function densityOverlapLabelPoints(project: Project): DensityOverlapLabelPoint[];
export function densityInspectionAt(features: Array<{ properties: unknown }>): DensityInspection | null;
export function densityLayerDefinitions(legend: PixelDensityLegendDefinition): Array<{ rank: number; token: string; colour: string; opacity: number }>;
