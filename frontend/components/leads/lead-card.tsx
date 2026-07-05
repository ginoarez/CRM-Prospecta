"use client";
import Link from "next/link";
import { Lead, LEAD_STATUSES, LeadStatus, STATUS_LABELS } from "@/lib/types";

export function LeadCard({ lead, onMove }: { lead: Lead; onMove: (s: LeadStatus) => void }) {
  return (
    <div className="mb-2 rounded-lg border border-black/10 bg-background/70 p-2.5 text-sm backdrop-blur-sm transition-colors hover:border-black/25 dark:border-white/10 dark:hover:border-white/25">
      <div className="flex items-start justify-between gap-2">
        <Link href={`/leads/${lead.id}`} className="font-medium leading-snug hover:underline">
          {lead.business_name}
        </Link>
        {lead.score != null && (
          <span className="flex-none rounded-md border border-black/10 px-1.5 py-0.5 text-[10px] font-semibold tabular-nums text-muted-foreground dark:border-white/10">
            {lead.score}
          </span>
        )}
      </div>
      <div className="mt-0.5 text-xs text-muted-foreground">{lead.city ?? "—"}</div>
      <select
        className="mt-2 w-full rounded-md border border-black/10 bg-background px-1.5 py-1 text-xs outline-none focus:border-foreground/40 dark:border-white/10 dark:focus:border-white/40"
        value={lead.status}
        onChange={(e) => onMove(e.target.value as LeadStatus)}
      >
        {LEAD_STATUSES.map((s) => (
          <option key={s} value={s}>{STATUS_LABELS[s]}</option>
        ))}
      </select>
    </div>
  );
}
