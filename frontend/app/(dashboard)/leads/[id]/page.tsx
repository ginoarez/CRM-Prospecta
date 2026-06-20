"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Interaction, Lead } from "@/lib/types";
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

  if (!lead) return <p>Cargando…</p>;

  const tabClass = (t: string) => (tab === t ? "border-b-2 border-blue-600 pb-1" : "pb-1");

  return (
    <div>
      <h1 className="text-2xl font-bold">{lead.business_name}</h1>
      <div className="my-3 flex gap-4 border-b">
        <button className={tabClass("info")} onClick={() => setTab("info")}>Info</button>
        <button className={tabClass("analysis")} onClick={() => setTab("analysis")}>Análisis IA</button>
        <button className={tabClass("messages")} onClick={() => setTab("messages")}>Mensajes</button>
        <button className={tabClass("email")} onClick={() => setTab("email")}>Email</button>
        <button className={tabClass("proposals")} onClick={() => setTab("proposals")}>Propuestas</button>
        <button className={tabClass("agenda")} onClick={() => setTab("agenda")}>Agenda</button>
        <button className={tabClass("interactions")} onClick={() => setTab("interactions")}>Interacciones</button>
      </div>

      {tab === "info" && (
        <dl className="grid grid-cols-2 gap-2 text-sm">
          <dt className="font-medium">Estado</dt><dd>{lead.status}</dd>
          <dt className="font-medium">Score</dt><dd>{lead.score ?? "—"}</dd>
          <dt className="font-medium">Ciudad</dt><dd>{lead.city ?? "—"}</dd>
          <dt className="font-medium">País</dt><dd>{lead.country ?? "—"}</dd>
          <dt className="font-medium">Teléfono</dt><dd>{lead.phone ?? "—"}</dd>
          <dt className="font-medium">Email</dt><dd>{lead.email ?? "—"}</dd>
          <dt className="font-medium">Web</dt><dd>{lead.website ?? "—"}</dd>
          <dt className="font-medium">Origen</dt><dd>{lead.source}</dd>
        </dl>
      )}

      {tab === "analysis" && <AnalysisPanel leadId={id} />}

      {tab === "messages" && <MessagesPanel leadId={id} />}

      {tab === "email" && <EmailPanel leadId={id} />}

      {tab === "proposals" && <ProposalsPanel leadId={id} />}

      {tab === "agenda" && <AgendaPanel leadId={id} />}

      {tab === "interactions" && (
        <div className="space-y-3">
          <div className="flex gap-2">
            <input className="flex-1 rounded border p-2" placeholder="Añadir nota…"
              value={note} onChange={(e) => setNote(e.target.value)} />
            <button className="rounded bg-blue-600 px-3 text-white"
              disabled={!note} onClick={() => addNote.mutate()}>Añadir</button>
          </div>
          <ul className="space-y-2">
            {(interactions ?? []).map((i) => (
              <li key={i.id} className="rounded bg-white p-2 text-sm shadow">
                <span className="font-medium">{i.kind}</span> · {i.content}
                <div className="text-xs text-gray-500">{new Date(i.created_at).toLocaleString()}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
