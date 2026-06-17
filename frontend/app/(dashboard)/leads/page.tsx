"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Lead, LeadList, LEAD_STATUSES, LeadStatus } from "@/lib/types";
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
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Leads ({data?.total ?? 0})</h1>
        <NewLeadDialog onCreate={(d) => create.mutate(d)} />
      </div>
      <div className="flex gap-3 overflow-x-auto">
        {LEAD_STATUSES.map((status) => (
          <div key={status} className="w-56 flex-shrink-0 rounded bg-gray-100 p-2">
            <h3 className="mb-2 text-sm font-semibold">{status}</h3>
            {leads.filter((l) => l.status === status).map((l) => (
              <LeadCard key={l.id} lead={l} onMove={(s) => move.mutate({ id: l.id, status: s })} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
