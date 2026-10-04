import type { CameraEquipmentCatalog, CameraMountingSlot, PoleCameraOverride, CameraModel, LensConfiguration } from "./types";
export function resolveCameraSlotSpecifications(catalog: CameraEquipmentCatalog | null, slot: CameraMountingSlot, override?: PoleCameraOverride): { camera: CameraModel | null; lens: LensConfiguration | null; warnings: string[] };
