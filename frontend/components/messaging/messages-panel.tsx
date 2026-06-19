"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Message, Template, WaLink } from "@/lib/types";

export default function MessagesPanel({ leadId }: { leadId: string }) {
  const qc = useQueryClient();
  const [templateId, setTemplateId] = useState("");
  const [body, setBody] = useState("");
  const [phone, setPhone] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

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

  const waUrl = phone ? `https://wa.me/${phone}?text=${encodeURIComponent(body)}` : null;

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
            <button className="rounded bg-gray-800 px-3 py-2 text-white"
                    onClick={() => markSent.mutate()}>Marcar como enviado</button>
          </div>
        </div>
      )}

      <ul className="space-y-2">
        {(messages ?? []).map((m) => (
          <li key={m.id} className="rounded bg-white p-2 text-sm shadow">
            <span className="font-medium">{m.channel}</span> · {m.status}
            <div>{m.body}</div>
            <div className="text-xs text-gray-500">{new Date(m.created_at).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
