export function formatLux(value: unknown): string;

export type LightingLabelPoint = {
  id: string;
  coordinate: [number, number];
  lux: number;
  label: string;
};

export function lightingLabelPoints(
  results: Record<string, {
    calculation_area_id?: string;
    points?: Array<{
      id: string;
      wgs84_coordinate: [number, number];
      maintained_horizontal_illuminance_lux: number;
    }>;
  }> | null | undefined,
): LightingLabelPoint[];
