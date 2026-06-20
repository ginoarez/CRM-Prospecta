"use client";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Lead, Message, Template, TaskStatus, WaLink, WaSendResponse } from "@/lib/types";

export default function MessagesPanel({ leadId }: { leadId: string }) {
  const qc = useQueryClient();
  const [templateId, setTemplateId] = useState("");
  const [body, setBody] = useState("");
  const [phone, setPhone] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: lead } = useQuery({ queryKey: ["lead", leadId], queryFn: () => api<Lead>(`/leads/${leadId}`) });
  const { data: templates } = useQuery({
    queryKey: ["templates", "wa"],
    queryFn: () => api<Template[]>("/templates?channel=wa"),
  });
  const { data: messages } = useQuery({
    queryKey: ["messages", leadId],
    queryFn: () => api<Message[]>(`/leads/${leadId}/messages`),
  });

  const generate = useMutation({
    mutationFn: () =>
      api<WaLink>(`/leads/${leadId}/wa-link`, {
        method: "POST",
        body: JSON.stringify({ template_id: templateId }),
      }),
    onSuccess: (r) => { setBody(r.body); setPhone(r.phone); setError(null); },
    onError: (e) => { setError((e as Error).message); setPhone(null); },
  });

  const markSent = useMutation({
    mutationFn: () =>
      api<Message>(`/leads/${leadId}/messages`, {
        method: "POST",
        body: JSON.stringify({ channel: "wa_link", body, template_id: templateId || null }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["messages", leadId] });
      qc.invalidateQueries({ queryKey: ["lead", leadId] });
      setPhone(null); setBody("");
    },
  });

  // El href se reconstruye en cliente desde el body editado; el url del servidor (wa-link) sería obsoleto tras editar.
  const waUrl = phone ? `https://wa.me/${phone}?text=${encodeURIComponent(body)}` : null;

  // --- WhatsApp Cloud (Fase 7) ---
  const [waText, setWaText] = useState("");
  const [waTask, setWaTask] = useState<string | null>(null);
  const [waErr, setWaErr] = useState<string | null>(null);
  const windowOpen = !!lead?.last_inbound_at &&
    Date.now() - new Date(lead.last_inbound_at).getTime() < 24 * 3600 * 1000;

  const { data: waTaskStatus } = useQuery({
    queryKey: ["task", waTask],
    queryFn: () => api<TaskStatus>(`/tasks/${waTask}`),
    enabled: !!waTask,
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "success" || s === "failure" ? false : 2000;
    },
  });
  useEffect(() => {
    if (waTaskStatus?.status === "success") {
      setWaTask(null); setWaText("");
      qc.invalidateQueries({ queryKey: ["messages", leadId] });
    } else if (waTaskStatus?.status === "failure") {
      setWaErr(waTaskStatus.error ?? "Falló el envío"); setWaTask(null);
    }
  }, [waTaskStatus, leadId, qc]);

  const waSend = useMutation({
    mutationFn: () => api<WaSendResponse>(`/leads/${leadId}/wa-send`, {
      method: "POST", body: JSON.stringify({ text: waText }),
    }),
    onSuccess: (r) => { setWaErr(null); setWaTask(r.task_id); },
    onError: (e) => setWaErr((e as Error).message),
  });

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <select className="rounded border p-2" value={templateId}
                onChange={(e) => setTemplateId(e.target.value)}>
          <option value="">— plantilla —</option>
          {(templates ?? []).map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
        <button className="rounded bg-blue-600 px-3 py-2 text-white disabled:opacity-50"
                disabled={!templateId || generate.isPending} onClick={() => generate.mutate()}>
          Generar wa.me
        </button>
      </div>
      {error && <p className="text-red-600">{error}</p>}

      {phone && waUrl && (
        <div className="space-y-2 rounded bg-white p-3 shadow">
          <textarea className="w-full rounded border p-2 text-sm" rows={4}
                    value={body} onChange={(e) => setBody(e.target.value)} />
          <div className="flex gap-2">
            <a className="rounded bg-green-600 px-3 py-2 text-white" href={waUrl}
               target="_blank" rel="noreferrer">Abrir WhatsApp</a>
            <button className="rounded bg-gray-800 px-3 py-2 text-white disabled:opacity-50"
                    disabled={markSent.isPending} onClick={() => markSent.mutate()}>Marcar como enviado</button>
          </div>
        </div>
      )}

      <div className="space-y-2 rounded bg-white p-3 shadow">
        <div className="flex items-center gap-2">
          <span className="font-medium">WhatsApp Cloud</span>
          {lead?.whatsapp_opt_out && <span className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700">opt-out</span>}
          <span className="text-xs text-gray-500">
            {windowOpen ? "ventana 24 h abierta" : "ventana 24 h cerrada — requiere plantilla aprobada"}
          </span>
        </div>
        <textarea className="w-full rounded border p-2 text-sm" rows={3}
                  placeholder="Mensaje (solo dentro de la ventana de 24 h)"
                  value={waText} onChange={(e) => setWaText(e.target.value)} />
        <button className="rounded bg-green-700 px-3 py-2 text-white disabled:opacity-50"
                onClick={() => waSend.mutate()}
                disabled={!!waTask || !waText || !windowOpen || !!lead?.whatsapp_opt_out}>
          {waTask ? "Enviando…" : "Enviar por WhatsApp Cloud"}
        </button>
        {waErr && <p className="text-red-600">{waErr}</p>}
      </div>

      <ul className="space-y-2">
        {(messages ?? []).map((m) => (
          <li key={m.id} className="rounded bg-white p-2 text-sm shadow">
            <span className="font-medium">{m.channel}</span> · {m.direction} · {m.status}
            <div>{m.body}</div>
            <div className="text-xs text-gray-500">{new Date(m.created_at).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
