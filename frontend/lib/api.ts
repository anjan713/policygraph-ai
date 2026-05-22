export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/* ---- Shared API types ---- */

export type DocumentItem = {
  id: string;
  file_name: string;
  status: string;
  storage_uri: string;
  job_id?: string | null;
  error_message?: string | null;
  created_at: string;
  processed_at?: string | null;
};

export type Citation = {
  document_id: string;
  chunk_id: string;
  page_number: number;
  excerpt: string;
  score?: number | null;
};

export type QueryResult = {
  query_id: string;
  answer: string;
  confidence: number;
  citations: Citation[];
  graph_context: Record<string, unknown>[];
  answer_mode: string; // vertex_gemini | rule_based | no_evidence
  model: string | null;
};

export type MatchedRule = {
  rule_id: string;
  procedure: string | null;
  decision: string;
  requirement_text: string | null;
  condition_text: string | null;
  confidence: number;
  page_number?: number | null;
  excerpt?: string | null;
};

export type ValidationResult = {
  decision: string;
  reasoning: string;
  missing_fields: string[];
  matched_rules: MatchedRule[];
};

export type GraphNode = {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
};

export type GraphEdge = {
  id: string;
  source_id: string;
  target_id: string;
  relationship: string;
  properties: Record<string, unknown>;
};

export type GraphData = { nodes: GraphNode[]; edges: GraphEdge[] };

/* ---- Display helpers ---- */

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    uploaded: "neutral",
    queued: "info",
    processing: "info",
    processed: "success",
    failed: "error",
  };
  return map[status] || "neutral";
}

export function decisionColor(decision: string): string {
  const d = decision.toLowerCase();
  if (d.includes("not_covered") || d.includes("excluded")) return "error";
  if (d.includes("covered") || d.includes("eligible")) return "success";
  if (d.includes("authorization")) return "purple";
  return "neutral";
}

export function prettyLabel(value: string): string {
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
