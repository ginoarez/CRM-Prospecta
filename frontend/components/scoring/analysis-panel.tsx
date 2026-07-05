"use client";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Analysis, AnalyzeResponse, TaskStatus } from "@/lib/types";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/controls";

export default function AnalysisPanel({ leadId }: { leadId: string }) {
  const qc = useQueryClient();
  const [taskId, setTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: analysis, isLoading } = useQuery({
    queryKey: ["analysis", leadId],
    queryFn: () => api<Analysis | null>(`/leads/${leadId}/analysis`),
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
      qc.invalidateQueries({ queryKey: ["analysis", leadId] });
      setTaskId(null);
    } else if (task?.status === "failure") {
      setError(task.error ?? "El análisis falló");
      setTaskId(null);
    }
  }, [task, leadId, qc]);

  const start = useMutation({
    mutationFn: () => api<AnalyzeResponse>(`/leads/${leadId}/analyze`, { method: "POST" }),
    onSuccess: (r) => { setError(null); setTaskId(r.task_id); },
    onError: (e) => setError((e as Error).message),
  });

  const running = !!taskId;

  return (
    <div className="space-y-3">
      <Button onClick={() => start.mutate()} disabled={running}>
        {running ? "Analizando…" : "Analizar con IA"}
      </Button>
      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

      {analysis && (
        <GlassCard className="max-w-2xl space-y-2 p-5 text-sm">
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold">{analysis.score ?? "—"}</span>
            <span className="text-muted-foreground">/100</span>
            {analysis.urgency && (
              <span className="rounded-md border border-black/10 px-2 py-0.5 text-xs text-muted-foreground dark:border-white/10">
                urgencia: {analysis.urgency}
              </span>
            )}
            {analysis.buy_probability != null && <span className="text-muted-foreground">prob. compra: {analysis.buy_probability}%</span>}
          </div>
          {analysis.summary && <p>{analysis.summary}</p>}
          {analysis.needs.length > 0 && <p><b>Necesidades:</b> {analysis.needs.join(", ")}</p>}
          {analysis.detected_problems.length > 0 && (
            <div><b>Problemas:</b><ul className="list-disc pl-5">{analysis.detected_problems.map((p, i) => <li key={i}>{p}</li>)}</ul></div>
          )}
          {analysis.opportunities.length > 0 && (
            <div><b>Oportunidades:</b><ul className="list-disc pl-5">{analysis.opportunities.map((o, i) => <li key={i}>{o}</li>)}</ul></div>
          )}
          <p className="text-xs text-muted-foreground">{analysis.model ? `${analysis.model} · ` : ""}{new Date(analysis.created_at).toLocaleString()}</p>
        </GlassCard>
      )}
      {!analysis && !running && !isLoading && <p className="text-sm text-muted-foreground">Este lead aún no tiene análisis.</p>}
    </div>
  );
}
