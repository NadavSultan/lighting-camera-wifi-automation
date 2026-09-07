export type WifiMapPresentationState = "not-calculated" | "empty" | "hidden" | "visible";

export type WifiMapStateResult = {
  global_statistics?: {
    circle_count?: number;
  };
} | null | undefined;

export function wifiMapState(
  result: WifiMapStateResult,
  visible: boolean,
): WifiMapPresentationState;
