"use client";
import type { MeasurementState } from "../lib/map-distance-workflow.mjs";

export function MapDistanceControl({ state, disabledReason, onStart, onClear, onCancel }: {
  state: MeasurementState; disabledReason: string | null;
  onStart: () => void; onClear: () => void; onCancel: () => void;
}) {
  const active = state.status !== "idle";
  const message = state.status === "first-point" ? "Click the start point. Esc cancels."
    : state.status === "second-point" ? "Click the end point. Esc cancels."
    : state.status === "pending" ? "Measuring… Esc cancels."
    : state.status === "complete" ? `${state.distanceM?.toFixed(2)} m · straight line in projected metres`
    : state.status === "error" ? state.error : disabledReason;
  return <div className="map-distance-control">
    <button type="button" className="quiet-button" disabled={Boolean(disabledReason)} title={disabledReason ?? undefined} onClick={active ? onClear : onStart}>{active ? "Clear measurement" : "Measure distance"}</button>
    {active && state.status !== "complete" && <button type="button" className="quiet-button" onClick={onCancel}>Cancel</button>}
    {message && <p role={state.status === "error" ? "alert" : "status"}>{message}</p>}
  </div>;
}
