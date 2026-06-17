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
