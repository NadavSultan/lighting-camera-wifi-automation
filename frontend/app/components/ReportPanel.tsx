"use client";

import { useEffect, useState } from "react";
import { downloadReportPackage, previewReport } from "../lib/api";
import {
  REPORT_DISCLAIMER,
  applyLastReportMetadata,
  defaultReportFormats,
  defaultReportSections,
  mergeReportPreferences,
  reportCanGenerate,
  reportStatusLabel,
} from "../lib/phase7-report-workflows.mjs";
import type { LastReportMetadata, Project, ReportFormatSelection, ReportPackageRequest, ReportSectionSelection } from "../lib/types";

type Preview = {
  status: string;
  checklist: Array<{ section: string; title: string; enabled: boolean; disposition: string }>;
  formats: Array<{ format: string; enabled: boolean }>;
  blockers: string[];
  warnings: string[];
  validation_findings: string[];
  can_generate: boolean;
  disclaimer: string;
  report_input_sha256: string | null;
};

const FORMAT_LABELS: Record<keyof ReportFormatSelection, string> = {
  project_json: "Project JSON archive",
  engineering_kmz: "Derived engineering KMZ",
  csv_schedules: "CSV schedules",
  xlsx_workbook: "XLSX workbook",
  pdf_summary: "PDF summary",
  presentation_model: "Presentation-model JSON",
};

const SECTION_LABELS: Record<keyof ReportSectionSelection, string> = {
  project_inventory: "Project inventory",
  poles_fixtures: "Poles / fixtures",
  cameras: "Cameras",
  lighting: "Lighting",
  wifi: "Wi-Fi",
  cap: "CAP",
  warnings_assumptions: "Warnings / assumptions",
  validation_findings: "Validation findings",
  provenance: "Provenance",
};

type Props = {
  project: Project;
  busy: boolean;
  onBusy: (value: boolean) => void;
  onStatus: (value: string) => void;
  onError: (value: string | null) => void;
  onReportMetadataApplied: (project: Project) => void;
};

export function ReportPanel({ project, busy, onBusy, onStatus, onError, onReportMetadataApplied }: Props) {
  const [formats, setFormats] = useState<ReportFormatSelection>({
    ...defaultReportFormats(),
    ...project.report_preferences?.formats,
  });
  const [sections, setSections] = useState<ReportSectionSelection>({
    ...defaultReportSections(),
    ...project.report_preferences?.sections,
  });
  const [preview, setPreview] = useState<Preview | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const next = await previewReport(project.id, { formats, sections });
        if (!cancelled) setPreview(next as Preview);
      } catch (error) {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : String(error);
          setPreview({
            status: "incomplete",
            checklist: [],
            formats: [],
            blockers: [message],
            warnings: [],
            validation_findings: [],
            can_generate: false,
            disclaimer: REPORT_DISCLAIMER,
            report_input_sha256: null,
          });
          onError(message);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
    // Automatic preview follows saved project identity; selection-aware refresh uses the button.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional: avoid preview storms on every checkbox toggle
  }, [project.id, project.updated_at]);

  async function refreshPreview() {
    onBusy(true);
    onError(null);
    try {
      const next = await previewReport(project.id, { formats, sections });
      setPreview(next as Preview);
      onStatus(`Report preview · ${reportStatusLabel((next as Preview).status)}`);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setPreview({
        status: "incomplete",
        checklist: [],
        formats: [],
        blockers: [message],
        warnings: [],
        validation_findings: [],
        can_generate: false,
        disclaimer: REPORT_DISCLAIMER,
        report_input_sha256: null,
      });
      onError(message);
    } finally {
      onBusy(false);
    }
  }

  async function generate() {
    onBusy(true);
    onError(null);
    try {
      const request: ReportPackageRequest = {
        formats,
        sections,
        persist_last_report_metadata: true,
        expected_project_updated_at: project.updated_at,
      };
      const result = await downloadReportPackage(project, request);
      // Persist selection into client prefs before remount (updated_at key) rehydrates checkboxes.
      const withPrefs = mergeReportPreferences(project, formats, sections) ?? project;
      const merged = applyLastReportMetadata(
        withPrefs,
        result.last_report as LastReportMetadata | null,
        result.project_updated_at,
      );
      if (merged) onReportMetadataApplied(merged);
      onStatus(`Report package downloaded · ${reportStatusLabel(result.status || result.last_report?.status)}`);
      const next = await previewReport(project.id, { formats, sections });
      setPreview(next as Preview);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setPreview({
        status: "incomplete",
        checklist: [],
        formats: [],
        blockers: [message],
        warnings: [],
        validation_findings: [],
        can_generate: false,
        disclaimer: REPORT_DISCLAIMER,
        report_input_sha256: null,
      });
      onError(message);
    } finally {
      onBusy(false);
    }
  }

  const canGenerate = reportCanGenerate(preview) && Object.values(formats).some(Boolean);

  return (
    <section className="section">
      <div className="section-heading">
        <h3>Phase 7 — Report package</h3>
        <span className="helper">Export only</span>
      </div>
      <p className="lighting-disclaimer">{REPORT_DISCLAIMER}</p>
      <p className="helper">Reports reflect the saved project. Generation does not recalculate engineering results or edit source poles.</p>
      <div className="form-grid">
        {(Object.keys(FORMAT_LABELS) as Array<keyof ReportFormatSelection>).map((key) => (
          <label className="layer-row" key={key}>
            <input
              type="checkbox"
              checked={formats[key]}
              disabled={busy}
              onChange={(event) => setFormats((current) => ({ ...current, [key]: event.target.checked }))}
            />
            <span>{FORMAT_LABELS[key]}</span>
          </label>
        ))}
      </div>
      <div className="form-grid">
        {(Object.keys(SECTION_LABELS) as Array<keyof ReportSectionSelection>).map((key) => (
          <label className="layer-row" key={key}>
            <input
              type="checkbox"
              checked={sections[key]}
              disabled={busy}
              onChange={(event) => setSections((current) => ({ ...current, [key]: event.target.checked }))}
            />
            <span>{SECTION_LABELS[key]}</span>
          </label>
        ))}
      </div>
      <div className="button-row">
        <button type="button" className="quiet-button" onClick={() => void refreshPreview()} disabled={busy}>
          Refresh report checklist
        </button>
        <button type="button" className="tool-button primary" onClick={() => void generate()} disabled={busy || !canGenerate}>
          Generate / Download report package
        </button>
      </div>
      {preview && (
        <div className="warning-card info">
          <strong>Status: {reportStatusLabel(preview.status)}</strong>
          {preview.report_input_sha256 && <p>Input fingerprint {preview.report_input_sha256}</p>}
          {preview.blockers.length > 0 && (
            <p>
              <strong>Blockers:</strong> {preview.blockers.join("; ")}
            </p>
          )}
          {preview.validation_findings.length > 0 && (
            <details>
              <summary>Validation findings ({preview.validation_findings.length})</summary>
              {preview.validation_findings.map((finding) => (
                <p key={finding}>{finding}</p>
              ))}
            </details>
          )}
          {preview.warnings.length > 0 && (
            <details>
              <summary>Warnings ({preview.warnings.length})</summary>
              {preview.warnings.map((warning) => (
                <p key={warning}>{warning}</p>
              ))}
            </details>
          )}
          <details>
            <summary>Section dispositions</summary>
            {preview.checklist.map((item) => (
              <p key={item.section}>
                {item.title}: {item.disposition}
                {item.enabled ? "" : " (disabled)"}
              </p>
            ))}
          </details>
        </div>
      )}
      {project.last_report && (
        <p className="helper">
          Last report {reportStatusLabel(project.last_report.status)} at {project.last_report.generated_at} · package{" "}
          {project.last_report.package_sha256.slice(0, 12)}…
        </p>
      )}
    </section>
  );
}
