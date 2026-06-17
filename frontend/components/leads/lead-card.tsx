"use client";
import Link from "next/link";
import { Lead, LEAD_STATUSES, LeadStatus } from "@/lib/types";

export function LeadCard({ lead, onMove }: { lead: Lead; onMove: (s: LeadStatus) => void }) {
  return (
    <div className="mb-2 rounded bg-white p-2 text-sm shadow">
      <Link href={`/leads/${lead.id}`} className="font-medium hover:underline">
        {lead.business_name}
      </Link>
      <div className="text-xs text-gray-500">{lead.city ?? "—"}</div>
      <select className="mt-1 w-full rounded border text-xs" value={lead.status}
        onChange={(e) => onMove(e.target.value as LeadStatus)}>
        {LEAD_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
      </select>
    </div>
  );
}
