"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Lead, LeadList, LEAD_STATUSES, LeadStatus, STATUS_LABELS } from "@/lib/types";
import { LeadCard } from "@/components/leads/lead-card";
import { NewLeadDialog } from "@/components/leads/new-lead-dialog";

export default function LeadsPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["leads"],
    queryFn: () => api<LeadList>("/leads?page_size=100"),
  });

  const create = useMutation({
    mutationFn: (body: Record<string, string>) =>
      api<Lead>("/leads", { method: "POST", body: JSON.stringify(body) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leads"] }),
  });

  const move = useMutation({
    mutationFn: ({ id, status }: { id: string; status: LeadStatus }) =>
      api<Lead>(`/leads/${id}/stage`, { method: "PATCH", body: JSON.stringify({ status }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leads"] }),
  });

  const leads = data?.items ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Leads</h1>
          <p className="text-sm text-muted-foreground">
            {data?.total ?? 0} en cartera · arrastra por etapa con el selector de cada tarjeta
          </p>
        </div>
        <NewLeadDialog onCreate={(d) => create.mutate(d)} />
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {LEAD_STATUSES.map((status) => {
          const column = leads.filter((l) => l.status === status);
          return (
            <div
              key={status}
              className="w-60 flex-shrink-0 rounded-xl border border-black/10 bg-black/[0.02] p-2.5 dark:border-white/10 dark:bg-white/[0.03]"
            >
              <div className="mb-2 flex items-center justify-between px-1">
                <h3 className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                  {STATUS_LABELS[status]}
                </h3>
                <span className="text-xs tabular-nums text-muted-foreground">{column.length}</span>
              </div>
              {column.map((l) => (
                <LeadCard key={l.id} lead={l} onMove={(s) => move.mutate({ id: l.id, status: s })} />
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
}
