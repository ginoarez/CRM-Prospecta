"use client";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { EmailPreview, EmailSendResponse, Template, TaskStatus } from "@/lib/types";

export default function EmailPanel({ leadId }: { leadId: string }) {
  const qc = useQueryClient();
  const [templateId, setTemplateId] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: templates } = useQuery({
    queryKey: ["templates", "email"],
    queryFn: () => api<Template[]>(`/templates`),
  });
  const emailTemplates = (templates ?? []).filter((t) => t.channel === "email");

  const preview = useMutation({
    mutationFn: (tid: string) =>
      api<EmailPreview>(`/leads/${leadId}/email-preview`, {
        method: "POST", body: JSON.stringify({ template_id: tid }),
      }),
    onSuccess: (r) => { setSubject(r.subject); setBody(r.body); setError(null); },
    onError: (e) => setError((e as Error).message),
  });

  const { data: task } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => api<TaskStatus>(`/tasks/${taskId}`),
    enabled: !!taskId,
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "success" || s === "failure" ? false : 2000;
    },
  });

  useEffect(() => {
    if (task?.status === "success") {
      setMsg("Correo enviado."); setTaskId(null);
      qc.invalidateQueries({ queryKey: ["messages", leadId] });
    } else if (task?.status === "failure") {
      setError(task.error ?? "El envío falló"); setTaskId(null);
    }
  }, [task, leadId, qc]);

  const send = useMutation({
    mutationFn: () => api<EmailSendResponse>(`/leads/${leadId}/email`, {
      method: "POST", body: JSON.stringify({ subject, body, template_id: templateId || null }),
    }),
    onSuccess: (r) => { setMsg(null); setError(null); setTaskId(r.task_id); },
    onError: (e) => setError((e as Error).message),
  });

  const sending = !!taskId;

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <select className="rounded border p-2" value={templateId}
                onChange={(e) => { setTemplateId(e.target.value); if (e.target.value) preview.mutate(e.target.value); }}>
          <option value="">Elegir plantilla…</option>
          {emailTemplates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
      </div>
      <input className="w-full rounded border p-2" placeholder="Asunto"
             value={subject} onChange={(e) => setSubject(e.target.value)} />
      <textarea className="h-40 w-full rounded border p-2" placeholder="Cuerpo del correo"
                value={body} onChange={(e) => setBody(e.target.value)} />
      <button className="rounded bg-blue-600 px-3 py-2 text-white disabled:opacity-50"
              onClick={() => send.mutate()} disabled={sending || !subject || !body}>
        {sending ? "Enviando…" : "Enviar email"}
      </button>
      {msg && <p className="text-green-600">{msg}</p>}
      {error && <p className="text-red-600">{error}</p>}
    </div>
  );
}
