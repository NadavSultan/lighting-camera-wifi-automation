export function screenArrow(
  origin: { x: number; y: number },
  endpoint: { x: number; y: number },
  length?: number,
): { dx: number; dy: number } | null;

export function directionSignificantKey(
  project: {
    id?: string;
    projected_crs?: string | null;
    source?: { poles?: Array<{ id: string; longitude: number; latitude: number }> };
    pole_edits?: Record<
      string,
      {
        active?: boolean | null;
        fixture_configuration?: {
          fixture_model_id?: string;
          fixture_model_revision?: number;
          fixture_azimuth_deg?: number;
        } | null;
      }
    >;
  } | null | undefined,
): string;
