export function normalizeFixtureAzimuth(value: number): number;
export function roundNormalizedFixtureAzimuth(value: number, precision?: number): number;
export function fixtureAzimuthFromHandle(poleLongitude: number, poleLatitude: number, handleLongitude: number, handleLatitude: number): number;
export function closePriorityRing(points: Array<[number, number]>): Array<[number, number]>;
export function validateAndClosePriorityRing(points: Array<[number, number]>): Array<[number, number]>;
export function emptyPriorityRedrawDraft(): Array<[number, number]>;
export function renamePriorityArea<T extends { name: string; wgs84_coordinates: Array<[number, number]>; modified_at: string }>(area: T, name: string, modifiedAt: string): T;
export function formatEngineeringAzimuth(value: number): string;
