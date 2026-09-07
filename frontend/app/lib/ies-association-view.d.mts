export type AssociationRowModel = {
  id: string;
  fixture_family?: string;
  capability_variant?: string;
  display_name?: string;
};

export type AssociationPair = {
  ies_file_id: string;
  fixture_model_id: string;
  active?: boolean;
};

export type AssociationRow = {
  id: string;
  fixture_family: string;
  capability_variant: string;
  display_name: string;
  associated: boolean;
};

export function associationRows(
  fileId: string,
  fixtureModels: AssociationRowModel[],
  associations: AssociationPair[],
): AssociationRow[];

export function groupAssociationRowsByFamily(
  rows: AssociationRow[],
): Array<{ family: string; items: AssociationRow[] }>;
