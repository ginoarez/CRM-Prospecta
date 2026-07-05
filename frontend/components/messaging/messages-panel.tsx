"use client";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Lead, Message, Template, TaskStatus, WaLink, WaSendResponse } from "@/lib/types";
import WritingToolbar from "@/components/assistant/writing-toolbar";
import { GlassCard } from "@/components/ui/glass-card";
import { Button, Input, Select, Textarea } from "@/components/ui/controls";

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

  // --- Asistente de objeciones (Fase 8a) ---
  const [objection, setObjection] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const suggest = useMutation({
    mutationFn: () => api<{ suggestions: string[] }>(`/leads/${leadId}/suggest-reply`, {
      method: "POST", body: JSON.stringify({ objection: objection || null }),
    }),
    onSuccess: (r) => setSuggestions(r.suggestions),
    onError: (e) => setWaErr((e as Error).message),
  });

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <Select value={templateId} onChange={(e) => setTemplateId(e.target.value)}>
          <option value="">— plantilla —</option>
          {(templates ?? []).map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </Select>
        <Button disabled={!templateId || generate.isPending} onClick={() => generate.mutate()}>
          Generar wa.me
        </Button>
      </div>
      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

      {phone && waUrl && (
        <GlassCard className="max-w-2xl space-y-2 p-4">
          <Textarea className="w-full" rows={4}
                    value={body} onChange={(e) => setBody(e.target.value)} />
          <div className="flex gap-2">
            <a className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-85"
               href={waUrl} target="_blank" rel="noreferrer">Abrir WhatsApp</a>
            <Button variant="ghost" disabled={markSent.isPending} onClick={() => markSent.mutate()}>
              Marcar como enviado
            </Button>
          </div>
        </GlassCard>
      )}

      <GlassCard className="max-w-2xl space-y-2 p-4">
        <div className="flex items-center gap-2">
          <span className="font-medium">WhatsApp Cloud</span>
          {lead?.whatsapp_opt_out && (
            <span className="rounded-md border border-red-500/40 px-2 py-0.5 text-xs text-red-600 dark:text-red-400">opt-out</span>
          )}
          <span className="text-xs text-muted-foreground">
            {windowOpen ? "ventana 24 h abierta" : "ventana 24 h cerrada — requiere plantilla aprobada"}
          </span>
        </div>
        <div className="space-y-2 border-t border-black/10 pt-2 dark:border-white/10">
          <div className="flex gap-2">
            <Input className="flex-1" placeholder="Objeción del prospecto (opcional)"
                   value={objection} onChange={(e) => setObjection(e.target.value)} />
            <Button variant="ghost" onClick={() => suggest.mutate()} disabled={suggest.isPending}>
              {suggest.isPending ? "Pensando…" : "Sugerir respuesta"}
            </Button>
          </div>
          {suggestions.length > 0 && (
            <ul className="space-y-1">
              {suggestions.map((s, i) => (
                <li key={i}>
                  <button className="w-full rounded-lg border border-black/10 bg-black/[0.03] p-2 text-left text-sm transition-colors hover:bg-black/[0.06] dark:border-white/10 dark:bg-white/[0.04] dark:hover:bg-white/[0.08]"
                          onClick={() => { setWaText(s); setSuggestions([]); }}>
                    {s}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <WritingToolbar value={waText} onChange={setWaText}
          context={lead ? `${lead.business_name}${lead.city ? ", " + lead.city : ""}` : undefined} />
        <Textarea className="w-full" rows={3}
                  placeholder="Mensaje (solo dentro de la ventana de 24 h)"
                  value={waText} onChange={(e) => setWaText(e.target.value)} />
        <Button onClick={() => waSend.mutate()}
                disabled={!!waTask || !waText || !windowOpen || !!lead?.whatsapp_opt_out}>
          {waTask ? "Enviando…" : "Enviar por WhatsApp Cloud"}
        </Button>
        {waErr && <p className="text-sm text-red-600 dark:text-red-400">{waErr}</p>}
      </GlassCard>

      <ul className="max-w-2xl space-y-2">
        {(messages ?? []).map((m) => (
          <GlassCard key={m.id} className="p-3 text-sm">
            <span className="font-medium">{m.channel}</span>
            <span className="text-muted-foreground"> · {m.direction} · {m.status}</span>
            <div className="mt-1">{m.body}</div>
            <div className="mt-0.5 text-xs text-muted-foreground">{new Date(m.created_at).toLocaleString()}</div>
          </GlassCard>
        ))}
      </ul>
    </div>
  );
}
