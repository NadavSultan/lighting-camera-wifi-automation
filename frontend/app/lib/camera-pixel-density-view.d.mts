import type { Project } from "./types";

export type CameraPixelDensityView = {
  status: "not-calculated" | "current" | "stale";
  canCalculate: boolean;
  layerAvailable: boolean;
  message: string;
};

export function cameraPixelDensityView(project: Project | null): CameraPixelDensityView;
export function invalidateCameraPixelDensityIfSignificant(previous: Project, next: Project): Project;
