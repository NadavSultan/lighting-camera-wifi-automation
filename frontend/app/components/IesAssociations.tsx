"use client";

import { useMemo, useState } from "react";
import { associateIes, removeIesAssociation, setDefaultIes } from "../lib/api";
import { associationRows, groupAssociationRowsByFamily } from "../lib/ies-association-view.mjs";
import type { FixtureModel, IesFileRecord, IesLibrary } from "../lib/types";

interface Props {
  file: IesFileRecord;
  fixtureModels: FixtureModel[];
  ies: IesLibrary;
  onRefresh: () => Promise<void>;
  onError: (message: string | null) => void;
}

export function IesAssociations({ file, fixtureModels, ies, onRefresh, onError }: Props) {
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [defaultPending, setDefaultPending] = useState(false);
  const rows = useMemo(
    () => associationRows(file.id, fixtureModels, ies.fixture_associations),
    [file.id, fixtureModels, ies.fixture_associations],
  );
  const groups = useMemo(() => groupAssociationRowsByFamily(rows), [rows]);
  const canEdit = file.active && file.validation_status === "valid";

  async function toggle(modelId: string, currentlyAssociated: boolean) {
    if (!canEdit || pendingId) return;
    setPendingId(modelId);
    try {
      if (currentlyAssociated) await removeIesAssociation(file.id, modelId);
      else await associateIes(file.id, modelId);
      await onRefresh();
    } catch (caught) {
      onError(caught instanceof Error ? caught.message : "IES association update failed");
      await onRefresh();
    } finally {
      setPendingId(null);
    }
  }

  async function makeDefault(modelId: string) {
    if (!canEdit || defaultPending) return;
    setDefaultPending(true);
    try {
      await setDefaultIes(modelId, file.id);
      await onRefresh();
    } catch (caught) {
      onError(caught instanceof Error ? caught.message : "Set default IES failed");
      await onRefresh();
    } finally {
      setDefaultPending(false);
    }
  }

  return (
    <div className="ies-associations">
      <strong className="ies-associations-title">Assigned models</strong>
      {!canEdit && <p className="helper">Invalid or inactive IES files cannot gain active associations.</p>}
      {groups.map((group) => (
        <div className="ies-association-family" key={group.family}>
          <span className="ies-association-family-name">{group.family}</span>
          {group.items.map((row) => {
            const model = fixtureModels.find((item) => item.id === row.id);
            const isDefault = model?.default_ies_file_id === file.id;
            return (
              <label className="ies-association-row" key={row.id}>
                <input
                  type="checkbox"
                  checked={row.associated}
                  disabled={!canEdit || pendingId === row.id}
                  onChange={() => void toggle(row.id, row.associated)}
                />
                <span>{row.display_name} · {row.capability_variant}</span>
                <button
                  type="button"
                  className="quiet-button"
                  disabled={!canEdit || !row.associated || defaultPending || isDefault}
                  onClick={() => void makeDefault(row.id)}
                >
                  {isDefault ? "Default" : "Set default"}
                </button>
              </label>
            );
          })}
        </div>
      ))}
    </div>
  );
}
