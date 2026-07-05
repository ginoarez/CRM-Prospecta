"use client";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, downloadFile } from "@/lib/api-client";
import type { Proposal, ProposalResponse, TaskStatus } from "@/lib/types";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/controls";

export default function ProposalsPanel({ leadId }: { leadId: string }) {
  const qc = useQueryClient();
  const [taskId, setTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: proposal, isLoading } = useQuery({
    queryKey: ["proposal", leadId],
    queryFn: () => api<Proposal | null>(`/leads/${leadId}/proposals`),
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
      qc.invalidateQueries({ queryKey: ["proposal", leadId] });
      setTaskId(null);
    } else if (task?.status === "failure") {
      setError(task.error ?? "La generación falló");
      setTaskId(null);
    }
  }, [task, leadId, qc]);

  const start = useMutation({
    mutationFn: () => api<ProposalResponse>(`/leads/${leadId}/proposals`, { method: "POST" }),
    onSuccess: (r) => { setError(null); setTaskId(r.task_id); },
    onError: (e) => setError((e as Error).message),
  });

  const running = !!taskId;
  const c = proposal?.content;

  return (
    <div className="space-y-3">
      <Button onClick={() => start.mutate()} disabled={running}>
        {running ? "Generando…" : proposal ? "Regenerar propuesta" : "Generar propuesta"}
      </Button>
      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

      {proposal && c && (
        <GlassCard className="max-w-2xl space-y-2 p-5 text-sm">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold">
              {proposal.price != null ? `$${proposal.price.toLocaleString()}` : "A convenir"}
            </span>
            {c.tiempo_estimado && <span className="text-muted-foreground">· {c.tiempo_estimado}</span>}
            {proposal.pdf_available && (
              <Button variant="ghost" className="ml-auto px-3 py-1"
                      onClick={() => downloadFile(`/proposals/${proposal.id}/pdf`, `propuesta-${proposal.id}.pdf`)}>
                Descargar PDF
              </Button>
            )}
          </div>
          {c.diagnostico && <p>{c.diagnostico}</p>}
          {c.soluciones && c.soluciones.length > 0 && (
            <div><b>Soluciones:</b><ul className="list-disc pl-5">{c.soluciones.map((s, i) => <li key={i}>{s}</li>)}</ul></div>
          )}
          {c.roi_estimado && <p><b>ROI estimado:</b> {c.roi_estimado}</p>}
          <p className="text-xs text-muted-foreground">{new Date(proposal.created_at).toLocaleString()}</p>
        </GlassCard>
      )}
      {!proposal && !running && !isLoading && <p className="text-sm text-muted-foreground">Este lead aún no tiene propuesta.</p>}
    </div>
  );
}
