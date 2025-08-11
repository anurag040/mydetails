export interface ProjectBlueprintSelection {
  baseStack: string | null | undefined;
  databases: string[] | null | undefined;
  auth: string[] | null | undefined;
  tooling: string[] | null | undefined;
  prdFileName: string | null;
}

export interface StackOption { id: string; label: string; description?: string; }

export interface ProjectBlueprintPayload {
  baseStack: string | null | undefined;
  databases: string[] | null | undefined;
  auth: string[] | null | undefined;
  tooling: string[] | null | undefined;
  prdFileName: string | null;
}
