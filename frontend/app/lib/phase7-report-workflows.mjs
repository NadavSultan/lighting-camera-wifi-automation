export const REPORT_DISCLAIMER =
  "Report package for engineering review only. Conceptual Phase 4-6 outputs are not professionally validated photometry, verified RF coverage, compliance determinations, optimal layouts, or installation-ready deliverables.";

export function defaultReportFormats() {
  return {
    project_json: true,
    engineering_kmz: true,
    csv_schedules: true,
    xlsx_workbook: true,
    pdf_summary: true,
    presentation_model: true,
  };
}

export function defaultReportSections() {
  return {
    project_inventory: true,
    poles_fixtures: true,
    cameras: true,
    lighting: true,
    wifi: true,
    cap: true,
    warnings_assumptions: true,
    validation_findings: true,
    provenance: true,
  };
}

export function reportCanGenerate(preview) {
  return Boolean(preview?.can_generate) && !(preview?.blockers?.length);
}

export function reportStatusLabel(status) {
  if (status === "complete") return "Complete";
  if (status === "complete_with_warnings") return "Complete with warnings";
  if (status === "incomplete") return "Incomplete";
  return "Unknown";
}

/** Presentation-only preference edits must not be treated as engineering undo steps by callers. */
export function mergeReportPreferences(project, formats, sections, kmzLayers) {
  if (!project) return project;
  return {
    ...project,
    report_preferences: {
      model_version: "report-package-1.0.0",
      formats: { ...defaultReportFormats(), ...project.report_preferences?.formats, ...formats },
      sections: { ...defaultReportSections(), ...project.report_preferences?.sections, ...sections },
      kmz_layers: {
        camera_geometry: true,
        lighting: true,
        wifi: true,
        cap: true,
        priority_areas: true,
        calculation_areas: true,
        wifi_analysis_areas: true,
        ...project.report_preferences?.kmz_layers,
        ...kmzLayers,
      },
    },
  };
}

/** Apply last_report metadata without touching engineering collections (undo-safe when applied outside history). */
export function applyLastReportMetadata(project, lastReport) {
  if (!project) return project;
  return { ...project, last_report: lastReport ?? null };
}
