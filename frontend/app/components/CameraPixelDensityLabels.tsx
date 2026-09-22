"use client";
import { useEffect, useRef } from "react";
import type { Map as MapLibreMap } from "maplibre-gl";
import type { DensityOverlapLabelPoint } from "../lib/camera-pixel-density-map.mjs";
import { cancelMapFrame, createMapFrameScheduler } from "../lib/map-frame-scheduler.mjs";

export default function CameraPixelDensityLabels({ map, points, visible }: { map: MapLibreMap | null; points: DensityOverlapLabelPoint[]; visible: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef<number | null>(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !map) return;
    const draw = () => {
      const ctx = canvas.getContext("2d"); if (!ctx) return;
      const width = map.getCanvas().clientWidth, height = map.getCanvas().clientHeight, dpr = window.devicePixelRatio || 1;
      if (canvas.width !== Math.floor(width * dpr) || canvas.height !== Math.floor(height * dpr)) { canvas.width = Math.floor(width * dpr); canvas.height = Math.floor(height * dpr); canvas.style.width = `${width}px`; canvas.style.height = `${height}px`; }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, width, height); if (!visible) return;
      ctx.font = "bold 12px ui-sans-serif, system-ui, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      for (const point of points) { const screen = map.project(point.coordinate); if (screen.x < 0 || screen.y < 0 || screen.x > width || screen.y > height) continue; ctx.lineWidth = 4; ctx.strokeStyle = "rgba(7,16,24,.95)"; ctx.fillStyle = "#fff"; ctx.strokeText(point.label, screen.x, screen.y); ctx.fillText(point.label, screen.x, screen.y); }
    };
    const schedule = createMapFrameScheduler(frameRef, draw); schedule();
    for (const event of ["move", "resize", "zoom", "rotate", "pitch", "idle"] as const) map.on(event, schedule);
    window.addEventListener("resize", schedule);
    return () => { cancelMapFrame(frameRef); for (const event of ["move", "resize", "zoom", "rotate", "pitch", "idle"] as const) map.off(event, schedule); window.removeEventListener("resize", schedule); };
  }, [map, points, visible]);
  return <canvas ref={canvasRef} className="camera-density-labels" aria-hidden="true" />;
}
