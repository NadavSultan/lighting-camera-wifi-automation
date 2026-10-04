// Transient measurement interaction; no Project fields or persistence.
export function initialMeasurementState() {
  return { status: "idle", start: null, end: null, distanceM: null, error: null };
}
export function startMeasurement() {
  return { ...initialMeasurementState(), status: "first-point" };
}
export function clearMeasurement() { return startMeasurement(); }
export function measurementBlocksMapInteractions(state) {
  return ["first-point", "second-point", "pending", "error"].includes(state.status);
}
export function mapInteractionBlocked(state, drawing) {
  return drawing || measurementBlocksMapInteractions(state);
}
export function cancelMeasurement(state) {
  return measurementBlocksMapInteractions(state) ? initialMeasurementState() : state;
}
export function addMeasurementPoint(state, coordinate) {
  if (!["first-point", "second-point"].includes(state.status)) return state;
  if (!Array.isArray(coordinate) || coordinate.length !== 2 || !coordinate.every(Number.isFinite)
    || Math.abs(coordinate[0]) > 180 || Math.abs(coordinate[1]) > 90) {
    return { ...initialMeasurementState(), status: "error", error: "Invalid measurement coordinate." };
  }
  if (state.status === "first-point") return { ...state, status: "second-point", start: [...coordinate] };
  return { ...state, status: "pending", end: [...coordinate] };
}

export function createMeasurementController(request, onChange) {
  let state = initialMeasurementState(), projectId = null, crs = null;
  let generation = 0, abort = null;
  const publish = (next) => { state = next; onChange(state); };
  const invalidate = () => { generation += 1; abort?.abort(); abort = null; };
  return {
    getState: () => state,
    setContext(id, projectedCrs) {
      if (projectId === id && crs === projectedCrs) return;
      invalidate(); projectId = id; crs = projectedCrs; publish(initialMeasurementState());
    },
    start(allowed) {
      if (!allowed || !projectId || !crs) return;
      invalidate(); publish(startMeasurement());
    },
    clear() { invalidate(); publish(clearMeasurement()); },
    cancel() {
      if (!measurementBlocksMapInteractions(state)) return;
      invalidate(); publish(cancelMeasurement(state));
    },
    async click(coordinate) {
      const next = addMeasurementPoint(state, coordinate);
      if (next === state) return;
      publish(next);
      if (next.status !== "pending") return;
      const token = ++generation;
      abort = new AbortController();
      try {
        const result = await request(crs, next.start, next.end, { signal: abort.signal });
        if (token !== generation) return;
        if (!Number.isFinite(result.distance_m) || result.distance_m < 0) throw new Error("Invalid distance response.");
        abort = null;
        publish({ ...next, status: "complete", distanceM: result.distance_m });
      } catch (caught) {
        if (token !== generation) return;
        abort = null;
        publish({ ...initialMeasurementState(), status: "error", error: caught instanceof Error ? caught.message : "Could not measure distance." });
      }
    },
  };
}

export function measurementFeatures(state) {
  const features = [];
  if (state.start && state.status !== "error") {
    features.push({ type: "Feature", properties: { endpoint: "start" }, geometry: { type: "Point", coordinates: state.start } });
    if (state.end) {
      features.push({ type: "Feature", properties: { endpoint: "end", label: state.distanceM == null ? "" : `${state.distanceM.toFixed(2)} m` }, geometry: { type: "Point", coordinates: state.end } });
      features.push({ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: [state.start, state.end] } });
    }
  }
  return { type: "FeatureCollection", features };
}
