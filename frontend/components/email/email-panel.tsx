"use client";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { EmailPreview, EmailSendResponse, Template, TaskStatus } from "@/lib/types";
import WritingToolbar from "@/components/assistant/writing-toolbar";
import { Button, Input, Select, Textarea } from "@/components/ui/controls";

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
    <div className="max-w-2xl space-y-3">
      <div className="flex gap-2">
        <Select value={templateId}
                onChange={(e) => { setTemplateId(e.target.value); if (e.target.value) preview.mutate(e.target.value); }}>
          <option value="">Elegir plantilla…</option>
          {emailTemplates.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </Select>
      </div>
      <Input className="w-full" placeholder="Asunto"
             value={subject} onChange={(e) => setSubject(e.target.value)} />
      <WritingToolbar value={body} onChange={setBody} />
      <Textarea className="h-40 w-full" placeholder="Cuerpo del correo"
                value={body} onChange={(e) => setBody(e.target.value)} />
      <Button onClick={() => send.mutate()} disabled={sending || !subject || !body}>
        {sending ? "Enviando…" : "Enviar email"}
      </Button>
      {msg && <p className="text-sm text-muted-foreground">{msg}</p>}
      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}
