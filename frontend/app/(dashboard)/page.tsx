"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { DashboardMetrics, LEAD_STATUSES } from "@/lib/types";

export default function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["metrics"],
    queryFn: () => api<DashboardMetrics>("/dashboard/metrics"),
  });

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">Dashboard</h1>
      <div className="mb-6 grid grid-cols-3 gap-4">
        <div className="rounded bg-white p-4 shadow">
          <div className="text-sm text-gray-500">Total leads</div>
          <div className="text-3xl font-bold">{data?.total_leads ?? 0}</div>
        </div>
        <div className="rounded bg-white p-4 text-gray-400 shadow">Ingresos · próximamente</div>
        <div className="rounded bg-white p-4 text-gray-400 shadow">Tasa de respuesta · próximamente</div>
      </div>
      <h2 className="mb-2 font-semibold">Embudo por etapa</h2>
      <div className="space-y-1">
        {LEAD_STATUSES.map((s) => (
          <div key={s} className="flex items-center gap-2">
            <span className="w-40 text-sm">{s}</span>
            <div className="h-5 rounded bg-blue-500"
              style={{ width: `${(data?.by_status?.[s] ?? 0) * 24 + 4}px` }} />
            <span className="text-sm">{data?.by_status?.[s] ?? 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
