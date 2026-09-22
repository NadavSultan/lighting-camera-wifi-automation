import type { PixelDensityLegendDefinition } from "../lib/types";

export function CameraPixelDensityLegend({ legend }: { legend: PixelDensityLegendDefinition }) {
  return (
    <div className="density-legend" aria-label="Camera pixel-density colour legend">
      {legend.thresholds.map((threshold) => (
        <div className="density-legend-row" key={threshold.token}>
          <span className="density-swatch" style={{ backgroundColor: threshold.colour }} />
          <span>{threshold.minimum}–{threshold.maximum ?? "∞"} px/face</span>
        </div>
      ))}
    </div>
  );
}
