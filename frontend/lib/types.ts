export type LeadStatus =
  | "nuevo" | "calificado" | "contactado" | "en_conversacion"
  | "propuesta_enviada" | "negociacion" | "ganado" | "perdido" | "descartado";

export const LEAD_STATUSES: LeadStatus[] = [
  "nuevo", "calificado", "contactado", "en_conversacion",
  "propuesta_enviada", "negociacion", "ganado", "perdido", "descartado",
];

export interface Lead {
  id: string;
  business_name: string;
  industry: string | null;
  city: string | null;
  country: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  status: LeadStatus;
  score: number | null;
  source: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface LeadList { items: Lead[]; total: number; page: number; page_size: number; }
export interface Interaction {
  id: string; lead_id: string; kind: string; content: string | null; created_at: string;
}
export interface DashboardMetrics { total_leads: number; by_status: Record<string, number>; }

export interface GeoCategory { key: string; label: string; }

export interface GeoResult {
  osm_id: string;
  name: string;
  lat: number;
  lng: number;
  website: string | null;
  phone: string | null;
  address: string | null;
  already_imported: boolean;
}

export interface GeoSearchResponse {
  location: string;
  category: string;
  bbox: number[];
  count: number;
  results: GeoResult[];
}

export interface GeoImportResult { created: number; skipped_existing: number; }

export interface Analysis {
  id: string;
  lead_id: string;
  score: number | null;
  needs: string[];
  urgency: string | null;
  buy_probability: number | null;
  detected_problems: string[];
  opportunities: string[];
  summary: string | null;
  raw_signals: Record<string, unknown>;
  model: string | null;
  created_at: string;
}

export interface AnalyzeResponse { task_id: string; status: string; }
export interface TaskStatus { task_id: string; status: string; error: string | null; }
