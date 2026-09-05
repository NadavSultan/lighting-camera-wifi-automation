import type { LastReportMetadata, Project, ReportFormatSelection, ReportKmzLayerSelection, ReportSectionSelection } from "./types";

export declare const REPORT_DISCLAIMER: string;
export declare function defaultReportFormats(): ReportFormatSelection;
export declare function defaultReportSections(): ReportSectionSelection;
export declare function reportCanGenerate(preview: { can_generate?: boolean; blockers?: string[] } | null | undefined): boolean;
export declare function reportStatusLabel(status: string | null | undefined): string;
export declare function mergeReportPreferences(
  project: Project | null,
  formats?: Partial<ReportFormatSelection>,
  sections?: Partial<ReportSectionSelection>,
  kmzLayers?: Partial<ReportKmzLayerSelection>,
): Project | null;
export declare function applyLastReportMetadata(
  project: Project | null,
  lastReport: LastReportMetadata | null,
  projectUpdatedAt?: string | null,
): Project | null;
