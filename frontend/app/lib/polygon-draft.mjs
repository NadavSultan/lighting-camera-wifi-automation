/**
 * Pure GeoJSON draft builders for in-progress polygon drawing.
 * Transient presentation only — never mutates inputs or saved rings.
 */

function emptyCollection() {
  return { type: "FeatureCollection", features: [] };
}

function isFiniteCoordinate(coordinate) {
  return Array.isArray(coordinate)
    && coordinate.length >= 2
    && Number.isFinite(coordinate[0])
    && Number.isFinite(coordinate[1]);
}

function sameCoordinate(a, b) {
  return a[0] === b[0] && a[1] === b[1];
}

function copyPoints(points) {
  return points.map((point) => [point[0], point[1]]);
}

/**
 * @param {Array<[number, number]>} points placed vertices (WGS84 lng/lat)
 * @param {[number, number] | null | undefined} cursor optional map cursor
 * @returns {{ vertices: object, edges: object, fill: object, preview: object }}
 */
export function buildPolygonDraft(points, cursor) {
  const placed = Array.isArray(points) ? points.filter(isFiniteCoordinate) : [];
  const vertices = {
    type: "FeatureCollection",
    features: placed.map((coordinate, index) => ({
      type: "Feature",
      properties: { index, last: index === placed.length - 1 },
      geometry: { type: "Point", coordinates: [coordinate[0], coordinate[1]] },
    })),
  };

  const edges = emptyCollection();
  if (placed.length >= 2) {
    edges.features.push({
      type: "Feature",
      properties: {},
      geometry: { type: "LineString", coordinates: copyPoints(placed) },
    });
  }

  const fill = emptyCollection();
  if (placed.length >= 3) {
    const ring = copyPoints(placed);
    ring.push([placed[0][0], placed[0][1]]);
    fill.features.push({
      type: "Feature",
      properties: {},
      geometry: { type: "Polygon", coordinates: [ring] },
    });
  }

  const preview = emptyCollection();
  if (placed.length >= 1 && isFiniteCoordinate(cursor)) {
    const last = placed[placed.length - 1];
    if (!sameCoordinate(last, cursor)) {
      preview.features.push({
        type: "Feature",
        properties: {},
        geometry: {
          type: "LineString",
          coordinates: [[last[0], last[1]], [cursor[0], cursor[1]]],
        },
      });
    }
  }

  return { vertices, edges, fill, preview };
}

/**
 * Map-local drawing guidance copy for the active vertex count.
 * @param {number} vertexCount
 * @returns {string}
 */
export function polygonDraftGuidance(vertexCount) {
  if (vertexCount <= 0) return "Click to add the first point";
  if (vertexCount === 1) return "Click to add the next point";
  if (vertexCount === 2) return "Click to add the next point";
  return "Add another point or finish polygon";
}
