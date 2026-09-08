"use client";

import { useEffect, useRef, useState } from "react";
import type { Map as MapLibreMap } from "maplibre-gl";
import type { LightingCalculationResult } from "../lib/types";
import { clampCard, cardOffsetFromProjected } from "../lib/lighting-card-position.mjs";
import { formatLuxWithUnit } from "../lib/lighting-labels.mjs";

type LightingResultCardProps = {
  map: MapLibreMap | null;
  areaName: string;
  result: LightingCalculationResult | null;
  unavailableReason?: string | null;
  anchorLngLat: [number, number] | null;
  draggedPosition: { x: number; y: number } | null;
  onDraggedPosition: (position: { x: number; y: number } | null) => void;
  onClose: () => void;
};

function formatRatio(value: number | null | undefined, digits = 3) {
  if (value == null || !Number.isFinite(value)) return "—";
  return value.toFixed(digits);
}

export default function LightingResultCard({
  map,
  areaName,
  result,
  unavailableReason,
  anchorLngLat,
  draggedPosition,
  onDraggedPosition,
  onClose,
}: LightingResultCardProps) {
  const cardRef = useRef<HTMLElement | null>(null);
  const [position, setPosition] = useState({ x: 24, y: 72 });
  const dragOffsetRef = useRef<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const updateFromAnchor = () => {
      if (!map || !cardRef.current || draggedPosition) return;
      if (!anchorLngLat) return;
      const projected = map.project(anchorLngLat);
      const rect = cardRef.current.getBoundingClientRect();
      const container = map.getContainer().getBoundingClientRect();
      const offset = cardOffsetFromProjected(projected, 12);
      const next = clampCard(
        { x: offset.x, y: offset.y, width: rect.width || 280, height: rect.height || 180 },
        { width: container.width, height: container.height },
      );
      setPosition(next);
    };
    updateFromAnchor();
    if (!map) return;
    map.on("move", updateFromAnchor);
    map.on("resize", updateFromAnchor);
    return () => {
      map.off("move", updateFromAnchor);
      map.off("resize", updateFromAnchor);
    };
  }, [map, anchorLngLat, draggedPosition]);

  useEffect(() => {
    if (!draggedPosition || !cardRef.current || !map) return;
    const rect = cardRef.current.getBoundingClientRect();
    const container = map.getContainer().getBoundingClientRect();
    setPosition(clampCard(
      { ...draggedPosition, width: rect.width || 280, height: rect.height || 180 },
      { width: container.width, height: container.height },
    ));
  }, [draggedPosition, map]);

  function stageBounds() {
    const stage = cardRef.current?.closest(".map-stage");
    if (stage) return stage.getBoundingClientRect();
    if (map) return map.getContainer().getBoundingClientRect();
    return null;
  }

  function onPointerDown(event: React.PointerEvent<HTMLElement>) {
    if (!cardRef.current) return;
    if ((event.target as HTMLElement).closest("button")) return;
    event.preventDefault();
    event.stopPropagation();
    const rect = cardRef.current.getBoundingClientRect();
    dragOffsetRef.current = { x: event.clientX - rect.left, y: event.clientY - rect.top };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function onPointerMove(event: React.PointerEvent<HTMLElement>) {
    if (!dragOffsetRef.current || !cardRef.current) return;
    const container = stageBounds();
    if (!container) return;
    event.stopPropagation();
    const rect = cardRef.current.getBoundingClientRect();
    const next = clampCard(
      {
        x: event.clientX - container.left - dragOffsetRef.current.x,
        y: event.clientY - container.top - dragOffsetRef.current.y,
        width: rect.width || 280,
        height: rect.height || 180,
      },
      { width: container.width, height: container.height },
    );
    setPosition(next);
    onDraggedPosition(next);
  }

  function onPointerUp(event: React.PointerEvent<HTMLElement>) {
    if (!dragOffsetRef.current) return;
    event.stopPropagation();
    dragOffsetRef.current = null;
    try { event.currentTarget.releasePointerCapture(event.pointerId); } catch { /* already released */ }
  }

  const stats = result?.statistics;
  const current = result != null && !unavailableReason;

  return (
    <aside
      ref={cardRef}
      className="map-overlay lighting-result-card"
      style={{ left: position.x, top: position.y }}
      aria-label={`Lighting results for ${areaName}`}
      onPointerDown={(event) => event.stopPropagation()}
    >
      <header
        className="lighting-result-card-header"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
      >
        <strong>{areaName}</strong>
        <div className="lighting-result-card-actions">
          <button type="button" className="quiet-button" onClick={() => onDraggedPosition(null)}>Reset position</button>
          <button type="button" className="quiet-button" onClick={onClose} aria-label="Close lighting results">Close</button>
        </div>
      </header>
      {unavailableReason ? (
        <div className="lighting-result-card-body">
          <p className="helper">{unavailableReason}</p>
        </div>
      ) : !result ? (
        <div className="lighting-result-card-body">
          <p className="helper">No lighting result for this area.</p>
        </div>
      ) : (
        <div className="lighting-result-card-body">
          <p className="helper">{current ? "Current calculated result" : "Result state unknown"}</p>
          <dl className="lighting-result-stats">
            <div><dt>Eavg</dt><dd title={stats?.average_illuminance_lux != null ? String(stats.average_illuminance_lux) : undefined}>{formatLuxWithUnit(stats?.average_illuminance_lux)}</dd></div>
            <div><dt>Emin</dt><dd title={stats?.minimum_illuminance_lux != null ? String(stats.minimum_illuminance_lux) : undefined}>{formatLuxWithUnit(stats?.minimum_illuminance_lux)}</dd></div>
            <div><dt>Emax</dt><dd title={stats?.maximum_illuminance_lux != null ? String(stats.maximum_illuminance_lux) : undefined}>{formatLuxWithUnit(stats?.maximum_illuminance_lux)}</dd></div>
            <div><dt>Emin/Eavg</dt><dd>{formatRatio(stats?.emin_over_eavg)}</dd></div>
            <div><dt>Emin/Emax</dt><dd>{formatRatio(stats?.emin_over_emax)}</dd></div>
            <div><dt>Points</dt><dd>{stats?.point_count ?? "—"}</dd></div>
          </dl>
          <details className="lighting-result-assumptions">
            <summary>Assumptions and limitations</summary>
            <p className="helper">{result.disclaimer}</p>
            <p className="helper">Approved simplified direct-light model; not a standards-compliance determination.</p>
          </details>
        </div>
      )}
    </aside>
  );
}
