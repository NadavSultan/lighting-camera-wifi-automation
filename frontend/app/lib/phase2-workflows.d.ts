import type { EffectivePole, PoleCameraOverride } from "./types";

export function selectBulkPoleIds(poles: EffectivePole[], mode: "all" | "folder" | "manual", folder: string, manualIds: string[]): string[];
export function withoutCameraOverride(overrides: Record<string, PoleCameraOverride>, slotId: string): Record<string, PoleCameraOverride>;
export function formatApiErrorDetail(detail: unknown): string;
export function uploadIesAndRefresh<T>(upload: () => Promise<T>, refresh: () => Promise<void>): Promise<{ value: T; error: null } | { value: null; error: unknown }>;
