"use client";

import { useState } from "react";
import type { WifiCoverageResult } from "../lib/types";
import { wifiBoundaryGapMessage } from "../lib/phase5-workflows.mjs";
import { wifiMapState } from "../lib/wifi-map-state.mjs";

type WifiMapSummaryProps = {
  result: WifiCoverageResult | null;
  layerVisible: boolean;
  onShowCoverage: () => void;
};

export default function WifiMapSummary({ result, layerVisible, onShowCoverage }: WifiMapSummaryProps) {
  const [statsOpen, setStatsOpen] = useState(false);
  const state = wifiMapState(result, layerVisible);
  const circleCount = result?.global_statistics.circle_count ?? 0;
  const boundaryMessage = wifiBoundaryGapMessage(result);

  if (state === "not-calculated") {
    return (
      <aside className="map-overlay wifi-map-summary" aria-label="Conceptual Wi-Fi coverage summary">
        <strong>Conceptual Wi-Fi</strong>
        <span>No coverage calculated yet.</span>
        {boundaryMessage && <span className="helper">{boundaryMessage}</span>}
      </aside>
    );
  }

  if (state === "empty") {
    return (
      <aside className="map-overlay wifi-map-summary" aria-label="Conceptual Wi-Fi coverage summary">
        <strong>Conceptual Wi-Fi</strong>
        <span>0 conceptual coverage circles — no eligible enabled WIFI/SMART fixtures produced circles.</span>
        {boundaryMessage && <span className="helper">{boundaryMessage}</span>}
        <details className="wifi-map-stats" open={statsOpen} onToggle={(event) => setStatsOpen((event.target as HTMLDetailsElement).open)}>
          <summary>Covered-area statistics</summary>
          <WifiStatsBody result={result!} />
        </details>
      </aside>
    );
  }

  const visibilityLabel = state === "visible"
    ? `${circleCount} conceptual coverage circle${circleCount === 1 ? "" : "s"} calculated — shown on map`
    : `${circleCount} conceptual coverage circle${circleCount === 1 ? "" : "s"} calculated — hidden on map`;

  return (
    <aside
      className="map-overlay wifi-map-summary"
      aria-label="Conceptual Wi-Fi coverage summary"
      onPointerDown={(event) => event.stopPropagation()}
    >
      <strong>Conceptual Wi-Fi</strong>
      <span>{visibilityLabel}</span>
      {state === "hidden" && (
        <button type="button" className="quiet-button wifi-show-coverage" onClick={onShowCoverage}>
          Show coverage on map
        </button>
      )}
      {boundaryMessage && <span className="helper">{boundaryMessage}</span>}
      <details className="wifi-map-stats" open={statsOpen} onToggle={(event) => setStatsOpen((event.target as HTMLDetailsElement).open)}>
        <summary>Covered-area statistics</summary>
        <WifiStatsBody result={result!} />
      </details>
    </aside>
  );
}

function WifiStatsBody({ result }: { result: WifiCoverageResult }) {
  const g = result.global_statistics;
  return (
    <>
      <p>
        {g.circle_count} circles · individual {g.individual_area_m2.toFixed(6)} m² · union {g.union_covered_area_m2.toFixed(6)} m² · overlap {g.overlap_area_m2.toFixed(6)} m²
      </p>
      <p>
        Aggregate pairwise overlap {g.pairwise_overlap_area_m2.toFixed(6)} m² · multiply-covered union {g.multiply_covered_union_area_m2.toFixed(6)} m² · {g.overlap_pair_count} overlap pairs
      </p>
      {result.analysis_area_statistics.map((stats) => (
        <p key={stats.analysis_area_id}>
          <strong>{stats.analysis_area_name}</strong>
          {" · "}
          {stats.covered_area_m2.toFixed(6)} m² covered ({stats.covered_percentage.toFixed(1)}%) · {stats.uncovered_area_m2.toFixed(6)} m² uncovered ({stats.uncovered_percentage.toFixed(1)}%) · boundary {stats.boundary_covered_length_m.toFixed(6)} m ({stats.boundary_covered_percentage.toFixed(1)}%)
        </p>
      ))}
      <p className="helper">{result.disclaimer}</p>
    </>
  );
}
