"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { DashboardMetrics, LEAD_STATUSES } from "@/lib/types";
import { GlassCard } from "@/components/ui/glass-card";
import { NumberTicker } from "@/components/ui/number-ticker";
import { Sparkline } from "@/components/ui/sparkline";

export default function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["metrics"],
    queryFn: () => api<DashboardMetrics>("/dashboard/metrics"),
  });

  const total = data?.total_leads ?? 0;
  const contactados = data?.by_status?.["contactado"] ?? 0;
  const ganado = data?.by_status?.["ganado"] ?? 0;
  const conversion = total > 0 ? Math.round((ganado / total) * 100) : 0;
  const weekly = data?.weekly?.map((p) => p.leads) ?? [];
  const maxByStatus = Math.max(1, ...LEAD_STATUSES.map((s) => data?.by_status?.[s] ?? 0));

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <GlassCard className="p-5">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Total leads</div>
          <div className="mt-2 text-3xl font-bold"><NumberTicker value={total} /></div>
        </GlassCard>

        <GlassCard className="p-5">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Contactados</div>
          <div className="mt-2 text-3xl font-bold"><NumberTicker value={contactados} /></div>
        </GlassCard>

        <GlassCard className="p-5">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Conversión</div>
          <div className="mt-2 text-3xl font-bold"><NumberTicker value={conversion} suffix="%" /></div>
          <Sparkline data={weekly} className="mt-3 h-8 w-full text-foreground/70" />
        </GlassCard>
      </div>

      <GlassCard className="p-5">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Embudo por etapa</h2>
        <div className="space-y-2">
          {LEAD_STATUSES.map((s) => {
            const n = data?.by_status?.[s] ?? 0;
            return (
              <div key={s} className="flex items-center gap-3">
                <span className="w-36 flex-none text-sm text-muted-foreground">{s}</span>
                <div className="h-5 flex-1 overflow-hidden rounded bg-black/[0.04] dark:bg-white/[0.06]">
                  <div
                    className="h-full rounded bg-accent transition-[width] duration-500"
                    style={{ width: `${(n / maxByStatus) * 100}%` }}
                  />
                </div>
                <span className="w-8 flex-none text-right text-sm tabular-nums">{n}</span>
              </div>
            );
          })}
        </div>
      </GlassCard>
    </div>
  );
}
