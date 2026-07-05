"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Interaction, Lead, STATUS_LABELS } from "@/lib/types";
import { GlassCard } from "@/components/ui/glass-card";
import { Button, Input } from "@/components/ui/controls";
import AnalysisPanel from "@/components/scoring/analysis-panel";
import MessagesPanel from "@/components/messaging/messages-panel";
import ProposalsPanel from "@/components/proposals/proposals-panel";
import EmailPanel from "@/components/email/email-panel";
import AgendaPanel from "@/components/agenda/agenda-panel";

export default function LeadDetailPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();
  const [tab, setTab] = useState<"info" | "analysis" | "messages" | "email" | "proposals" | "agenda" | "interactions">("info");
  const [note, setNote] = useState("");

  const { data: lead } = useQuery({ queryKey: ["lead", id], queryFn: () => api<Lead>(`/leads/${id}`) });
  const { data: interactions } = useQuery({
    queryKey: ["interactions", id],
    queryFn: () => api<Interaction[]>(`/leads/${id}/interactions`),
  });

  const addNote = useMutation({
    mutationFn: () => api(`/leads/${id}/interactions`, {
      method: "POST", body: JSON.stringify({ kind: "nota", content: note }),
    }),
    onSuccess: () => { setNote(""); qc.invalidateQueries({ queryKey: ["interactions", id] }); },
  });

  if (!lead) return <p className="text-sm text-muted-foreground">Cargando…</p>;

  const tabClass = (t: string) =>
    tab === t
      ? "border-b-2 border-foreground pb-2 text-sm font-medium"
      : "border-b-2 border-transparent pb-2 text-sm text-muted-foreground transition-colors hover:text-foreground";

  const TABS = [
    ["info", "Info"], ["analysis", "Análisis IA"], ["messages", "Mensajes"], ["email", "Email"],
    ["proposals", "Propuestas"], ["agenda", "Agenda"], ["interactions", "Interacciones"],
  ] as const;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold tracking-tight">{lead.business_name}</h1>
        <span className="rounded-md border border-black/10 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground dark:border-white/10">
          {STATUS_LABELS[lead.status]}
        </span>
        {lead.score != null && (
          <span className="rounded-md border border-black/10 px-2 py-0.5 text-[11px] font-semibold tabular-nums text-muted-foreground dark:border-white/10">
            Score {lead.score}
          </span>
        )}
      </div>
      <div className="flex gap-5 overflow-x-auto border-b border-black/10 dark:border-white/10">
        {TABS.map(([key, label]) => (
          <button key={key} className={tabClass(key)} onClick={() => setTab(key)}>{label}</button>
        ))}
      </div>

      {tab === "info" && (
        <GlassCard className="max-w-xl p-5">
          <dl className="grid grid-cols-2 gap-x-4 gap-y-2.5 text-sm">
            <dt className="text-muted-foreground">Estado</dt><dd>{STATUS_LABELS[lead.status]}</dd>
            <dt className="text-muted-foreground">Score</dt><dd>{lead.score ?? "—"}</dd>
            <dt className="text-muted-foreground">Ciudad</dt><dd>{lead.city ?? "—"}</dd>
            <dt className="text-muted-foreground">País</dt><dd>{lead.country ?? "—"}</dd>
            <dt className="text-muted-foreground">Teléfono</dt><dd>{lead.phone ?? "—"}</dd>
            <dt className="text-muted-foreground">Email</dt><dd>{lead.email ?? "—"}</dd>
            <dt className="text-muted-foreground">Web</dt><dd className="truncate">{lead.website ?? "—"}</dd>
            <dt className="text-muted-foreground">Origen</dt><dd>{lead.source}</dd>
          </dl>
        </GlassCard>
      )}

      {tab === "analysis" && <AnalysisPanel leadId={id} />}

      {tab === "messages" && <MessagesPanel leadId={id} />}

      {tab === "email" && <EmailPanel leadId={id} />}

      {tab === "proposals" && <ProposalsPanel leadId={id} />}

      {tab === "agenda" && <AgendaPanel leadId={id} />}

      {tab === "interactions" && (
        <div className="max-w-2xl space-y-3">
          <div className="flex gap-2">
            <Input className="flex-1" placeholder="Añadir nota…"
              value={note} onChange={(e) => setNote(e.target.value)} />
            <Button disabled={!note} onClick={() => addNote.mutate()}>Añadir</Button>
          </div>
          <ul className="space-y-2">
            {(interactions ?? []).map((i) => (
              <GlassCard key={i.id} className="p-3 text-sm">
                <span className="font-medium">{i.kind}</span> · {i.content}
                <div className="mt-0.5 text-xs text-muted-foreground">{new Date(i.created_at).toLocaleString()}</div>
              </GlassCard>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
