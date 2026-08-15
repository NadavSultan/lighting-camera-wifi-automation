export function normalizeFixtureAzimuth(value) {
  const normalized = ((value % 360) + 360) % 360;
  return Object.is(normalized, -0) ? 0 : normalized;
}

export function fixtureAzimuthFromHandle(poleLongitude, poleLatitude, handleLongitude, handleLatitude) {
  const east = (handleLongitude - poleLongitude) * Math.cos(poleLatitude * Math.PI / 180);
  const north = handleLatitude - poleLatitude;
  return normalizeFixtureAzimuth(Math.atan2(east, north) * 180 / Math.PI);
}

export function closePriorityRing(points) {
  if (points.length < 3) throw new Error("A priority area requires at least three vertices");
  return [...points, points[0]];
}
