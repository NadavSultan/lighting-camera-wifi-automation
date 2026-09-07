"use client";

import { useEffect, useRef } from "react";
import type { Map as MapLibreMap } from "maplibre-gl";

export type LightingLabelPoint = {
  id: string;
  longitude: number;
  latitude: number;
  label: string;
};

type Props = {
  map: MapLibreMap | null;
  points: LightingLabelPoint[];
  visible: boolean;
};

export default function LightingPointLabels({ map, points, visible }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !map) return;

    const draw = () => {
      frameRef.current = null;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      const width = map.getCanvas().clientWidth;
      const height = map.getCanvas().clientHeight;
      const dpr = window.devicePixelRatio || 1;
      if (canvas.width !== Math.floor(width * dpr) || canvas.height !== Math.floor(height * dpr)) {
        canvas.width = Math.floor(width * dpr);
        canvas.height = Math.floor(height * dpr);
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      if (!visible) return;
      ctx.font = "11px ui-sans-serif, system-ui, sans-serif";
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      for (const point of points) {
        const screen = map.project([point.longitude, point.latitude]);
        if (screen.x < -40 || screen.y < -20 || screen.x > width + 40 || screen.y > height + 20) continue;
        const x = screen.x + 6;
        const y = screen.y - 6;
        ctx.lineWidth = 3;
        ctx.strokeStyle = "rgba(7, 16, 24, 0.92)";
        ctx.fillStyle = "#f8fafc";
        ctx.strokeText(point.label, x, y);
        ctx.fillText(point.label, x, y);
      }
    };

    const schedule = () => {
      if (frameRef.current != null) return;
      frameRef.current = window.requestAnimationFrame(draw);
    };

    schedule();
    map.on("move", schedule);
    map.on("resize", schedule);
    map.on("zoom", schedule);
    map.on("rotate", schedule);
    map.on("pitch", schedule);
    window.addEventListener("resize", schedule);
    return () => {
      if (frameRef.current != null) window.cancelAnimationFrame(frameRef.current);
      map.off("move", schedule);
      map.off("resize", schedule);
      map.off("zoom", schedule);
      map.off("rotate", schedule);
      map.off("pitch", schedule);
      window.removeEventListener("resize", schedule);
    };
  }, [map, points, visible]);

  return (
    <>
      <canvas ref={canvasRef} className="lighting-point-labels" aria-hidden="true" />
      {visible && points.length > 0 && (
        <div className="map-overlay lighting-lux-legend">
          <strong>Point values: maintained illuminance (lx)</strong>
          <span>Zoom in to separate point values</span>
        </div>
      )}
    </>
  );
}
