import type { FeatureCollection, Point, LineString } from "geojson";
export type MeasurementState = {
  status: "idle" | "first-point" | "second-point" | "pending" | "complete" | "error";
  start: [number, number] | null;
  end: [number, number] | null;
  distanceM: number | null;
  error: string | null;
};
export function initialMeasurementState(): MeasurementState;
export function startMeasurement(state?: MeasurementState): MeasurementState;
export function clearMeasurement(): MeasurementState;
export function cancelMeasurement(state: MeasurementState): MeasurementState;
export function addMeasurementPoint(state: MeasurementState, coordinate: [number, number]): MeasurementState;
export function measurementBlocksMapInteractions(state: MeasurementState): boolean;
export function mapInteractionBlocked(state: MeasurementState, drawing: boolean): boolean;
export function measurementFeatures(state: MeasurementState): FeatureCollection<Point | LineString>;
export function createMeasurementController(
  request: (crs: string, start: [number, number], end: [number, number], init: RequestInit) => Promise<{ distance_m: number }>,
  onChange: (state: MeasurementState) => void,
): {
  getState(): MeasurementState;
  setContext(projectId: string | null, crs: string | null): void;
  start(allowed: boolean): void;
  clear(): void;
  cancel(): void;
  click(coordinate: [number, number]): Promise<void>;
};
