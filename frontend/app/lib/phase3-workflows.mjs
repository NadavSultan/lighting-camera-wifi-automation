export function normalizeFixtureAzimuth(value) {
  const normalized = ((value % 360) + 360) % 360;
  return Object.is(normalized, -0) ? 0 : normalized;
}

export function fixtureAzimuthFromHandle(poleLongitude, poleLatitude, handleLongitude, handleLatitude) {
  const east = (handleLongitude - poleLongitude) * Math.cos(poleLatitude * Math.PI / 180);
  const north = handleLatitude - poleLatitude;
  return normalizeFixtureAzimuth(Math.atan2(east, north) * 180 / Math.PI);
}

function orientation(a, b, c) {
  return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
}

function segmentsIntersect(a, b, c, d) {
  const values = [orientation(a, b, c), orientation(a, b, d), orientation(c, d, a), orientation(c, d, b)];
  const onSegment = (start, end, point) => point[0] >= Math.min(start[0], end[0]) && point[0] <= Math.max(start[0], end[0]) && point[1] >= Math.min(start[1], end[1]) && point[1] <= Math.max(start[1], end[1]);
  if (values[0] === 0 && onSegment(a, b, c)) return true;
  if (values[1] === 0 && onSegment(a, b, d)) return true;
  if (values[2] === 0 && onSegment(c, d, a)) return true;
  if (values[3] === 0 && onSegment(c, d, b)) return true;
  return Math.sign(values[0]) !== Math.sign(values[1]) && Math.sign(values[2]) !== Math.sign(values[3]);
}

export function validateAndClosePriorityRing(points) {
  if (!Array.isArray(points) || points.length < 3) throw new Error("A priority area requires at least three distinct vertices.");
  for (const point of points) {
    if (!Array.isArray(point) || point.length !== 2 || !point.every(Number.isFinite)) throw new Error("Priority-area coordinates must be finite numbers.");
    if (point[0] < -180 || point[0] > 180 || point[1] < -90 || point[1] > 90) throw new Error("A priority-area coordinate is outside WGS84 bounds.");
  }
  if (new Set(points.map(([x, y]) => `${x},${y}`)).size < 3) throw new Error("A priority area requires at least three distinct vertices.");
  for (let first = 0; first < points.length; first += 1) {
    const firstNext = (first + 1) % points.length;
    for (let second = first + 1; second < points.length; second += 1) {
      const secondNext = (second + 1) % points.length;
      if (first === second || firstNext === second || secondNext === first) continue;
      if (segmentsIntersect(points[first], points[firstNext], points[second], points[secondNext])) throw new Error("The replacement priority area is self-intersecting.");
    }
  }
  const area2 = points.reduce((sum, point, index) => { const next = points[(index + 1) % points.length]; return sum + point[0] * next[1] - next[0] * point[1]; }, 0);
  if (Math.abs(area2) <= 1e-18) throw new Error("The replacement priority area is degenerate and has no usable area.");
  return [...points, points[0]];
}

export function closePriorityRing(points) {
  return validateAndClosePriorityRing(points);
}

export function emptyPriorityRedrawDraft() {
  return [];
}

export function renamePriorityArea(area, name, modifiedAt) {
  const trimmed = name.trim();
  if (!trimmed) throw new Error("Priority-area name is required.");
  return { ...area, name: trimmed, modified_at: modifiedAt, wgs84_coordinates: area.wgs84_coordinates };
}

export function formatEngineeringAzimuth(value) {
  if (!Number.isFinite(value)) return "—";
  return normalizeFixtureAzimuth(value).toFixed(3).replace(/\.?0+$/, "");
}
