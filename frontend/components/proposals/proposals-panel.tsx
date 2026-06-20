"use client";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, downloadFile } from "@/lib/api-client";
import type { Proposal, ProposalResponse, TaskStatus } from "@/lib/types";

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
      <button className="rounded bg-blue-600 px-3 py-2 text-white disabled:opacity-50"
              onClick={() => start.mutate()} disabled={running}>
        {running ? "Generando…" : proposal ? "Regenerar propuesta" : "Generar propuesta"}
      </button>
      {error && <p className="text-red-600">{error}</p>}

      {proposal && c && (
        <div className="space-y-2 rounded bg-white p-3 shadow text-sm">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold">
              {proposal.price != null ? `$${proposal.price.toLocaleString()}` : "A convenir"}
            </span>
            {c.tiempo_estimado && <span className="text-gray-500">· {c.tiempo_estimado}</span>}
            {proposal.pdf_available && (
              <button className="ml-auto rounded bg-green-600 px-3 py-1 text-white"
                      onClick={() => downloadFile(`/proposals/${proposal.id}/pdf`, `propuesta-${proposal.id}.pdf`)}>
                Descargar PDF
              </button>
            )}
          </div>
          {c.diagnostico && <p>{c.diagnostico}</p>}
          {c.soluciones && c.soluciones.length > 0 && (
            <div><b>Soluciones:</b><ul className="list-disc pl-5">{c.soluciones.map((s, i) => <li key={i}>{s}</li>)}</ul></div>
          )}
          {c.roi_estimado && <p><b>ROI estimado:</b> {c.roi_estimado}</p>}
          <p className="text-xs text-gray-400">{new Date(proposal.created_at).toLocaleString()}</p>
        </div>
      )}
      {!proposal && !running && !isLoading && <p className="text-sm text-gray-500">Este lead aún no tiene propuesta.</p>}
    </div>
  );
}
