import type { CameraPixelDensityProfile, PixelDensityLegendDefinition, Project } from "../lib/types";
import { cameraPixelDensityView } from "../lib/camera-pixel-density-view.mjs";
import { CameraPixelDensityLegend } from "./CameraPixelDensityLegend";

const DISCLAIMER = "Geometric horizontal pixel density for a front-facing 0.16 m reference face using an ideal pinhole model; not detection, recognition, identification, analytics, occlusion, visibility, or compliance evidence.";

type Props = {
  project: Project | null;
  legend: PixelDensityLegendDefinition | null;
  legendOpen: boolean;
  busy: boolean;
  onProfileChange: (profile: CameraPixelDensityProfile) => void;
  onCalculate: () => void;
  onToggleLegend: () => void;
};

export function CameraPixelDensityPanel({ project, legend, legendOpen, busy, onProfileChange, onCalculate, onToggleLegend }: Props) {
  const profile = project?.camera_pixel_density_profile;
  const view = cameraPixelDensityView(project);
  const update = (field: keyof CameraPixelDensityProfile, value: number) => {
    if (!profile || !Number.isFinite(value)) return;
    onProfileChange({ ...profile, [field]: value });
  };
  const midpoint = profile ? (profile.lower_projection_height_m + profile.upper_projection_height_m) / 2 : 1.25;
  return (
    <section className="section camera-density-panel">
      <div className="section-heading"><h3>Camera pixel density</h3><span className="helper">px/face</span></div>
      <div className="form-grid">
        <div className="field"><label htmlFor="density-lower-plane">Lower projection plane (m)</label><input id="density-lower-plane" type="number" value={profile?.lower_projection_height_m ?? 0.5} onChange={(event) => update("lower_projection_height_m", Number(event.target.value))} /></div>
        <div className="field"><label htmlFor="density-upper-plane">Upper projection plane (m)</label><input id="density-upper-plane" type="number" value={profile?.upper_projection_height_m ?? 2.0} onChange={(event) => update("upper_projection_height_m", Number(event.target.value))} /></div>
        <div className="field"><label htmlFor="density-auto-height">AUTO measurement height (m)</label><input id="density-auto-height" readOnly value={midpoint} /></div>
        <div className="field"><label htmlFor="density-max-distance">Maximum visible distance (m)</label><input id="density-max-distance" type="number" value={profile?.maximum_visible_distance_m ?? 50.0} onChange={(event) => update("maximum_visible_distance_m", Number(event.target.value))} /></div>
      </div>
      <p className={view.status === "stale" ? "warning-card" : "helper"}>{view.message}</p>
      <div className="button-row"><button className="primary" disabled={busy || !view.canCalculate} onClick={onCalculate}>Calculate camera density</button><button className="quiet-button" disabled={!legend} onClick={onToggleLegend}>Show colour legend</button></div>
      {legendOpen && legend ? <CameraPixelDensityLegend legend={legend} /> : null}
      {project?.camera_pixel_density.result?.warnings.map((warning) => <div className="warning-card" key={warning}>{warning}</div>)}
      <p className="lighting-disclaimer">{DISCLAIMER}</p>
    </section>
  );
}
