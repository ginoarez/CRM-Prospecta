"use client";
import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { DashboardMetrics, LEAD_STATUSES, LeadStatus } from "@/lib/types";
import { GlassCard } from "@/components/ui/glass-card";
import { NumberTicker } from "@/components/ui/number-ticker";
import { Sparkline } from "@/components/ui/sparkline";

const STATUS_LABELS: Record<LeadStatus, string> = {
  nuevo: "Nuevos",
  calificado: "Calificados",
  contactado: "Contactados",
  en_conversacion: "En conversación",
  propuesta_enviada: "Propuesta enviada",
  negociacion: "Negociación",
  ganado: "Ganados",
  perdido: "Perdidos",
  descartado: "Descartados",
};

function Icon({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`h-5 w-5 ${className}`}
    >
      {children}
    </svg>
  );
}

const ICON_USERS = (<><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /></>);
const ICON_CHAT = <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />;
const ICON_TREND = (<><polyline points="23 6 13.5 15.5 8.5 10.5 1 18" /><polyline points="17 6 23 6 23 12" /></>);
const ICON_CHECK = (<><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></>);
const ICON_DOC = (<><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></>);

function StatCard({ label, value, suffix, icon }: { label: string; value: number; suffix?: string; icon: ReactNode }) {
  return (
    <GlassCard className="p-4">
      <div className="flex items-start justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">{label}</span>
        <span className="text-muted-foreground">{icon}</span>
      </div>
      <div className="mt-3 text-2xl font-bold">
        <NumberTicker value={value} suffix={suffix} />
      </div>
    </GlassCard>
  );
}

export default function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["metrics"],
    queryFn: () => api<DashboardMetrics>("/dashboard/metrics"),
  });

  const by = data?.by_status ?? {};
  const total = data?.total_leads ?? 0;
  const ganado = by["ganado"] ?? 0;
  const conversion = total > 0 ? Math.round((ganado / total) * 100) : 0;
  const weekly = data?.weekly?.map((p) => p.leads) ?? [];
  const newThisWeek = weekly.length ? weekly[weekly.length - 1] : 0;
  const maxByStatus = Math.max(1, ...LEAD_STATUSES.map((s) => by[s] ?? 0));

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Resumen de tu cartera de prospectos</p>
      </div>

      {/* Hero + side metrics */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <GlassCard className="p-6 lg:col-span-2">
          <div className="flex items-start justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Total leads</div>
              <div className="mt-2 text-5xl font-bold leading-none">
                <NumberTicker value={total} />
              </div>
              <div className="mt-2 text-sm text-muted-foreground">
                {newThisWeek} {newThisWeek === 1 ? "nuevo" : "nuevos"} esta semana
              </div>
            </div>
            <span className="text-muted-foreground">
              <Icon className="h-6 w-6">{ICON_USERS}</Icon>
            </span>
          </div>
          <Sparkline data={weekly} className="mt-5 h-16 w-full text-foreground/70" />
          <div className="mt-1 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
            Nuevos por semana · últimas 8
          </div>
        </GlassCard>

        <div className="flex flex-col gap-4">
          <GlassCard className="flex-1 p-5">
            <div className="flex items-start justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Conversión</span>
              <span className="text-muted-foreground">
                <Icon>{ICON_TREND}</Icon>
              </span>
            </div>
            <div className="mt-2 text-3xl font-bold">
              <NumberTicker value={conversion} suffix="%" />
            </div>
            <div className="mt-1 text-xs text-muted-foreground">{ganado} ganados sobre {total}</div>
          </GlassCard>
          <GlassCard className="flex-1 p-5">
            <div className="flex items-start justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">En conversación</span>
              <span className="text-muted-foreground">
                <Icon>{ICON_CHAT}</Icon>
              </span>
            </div>
            <div className="mt-2 text-3xl font-bold">
              <NumberTicker value={by["en_conversacion"] ?? 0} />
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Secondary stat row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Contactados" value={by["contactado"] ?? 0} icon={<Icon>{ICON_CHAT}</Icon>} />
        <StatCard label="Calificados" value={by["calificado"] ?? 0} icon={<Icon>{ICON_CHECK}</Icon>} />
        <StatCard label="Propuesta enviada" value={by["propuesta_enviada"] ?? 0} icon={<Icon>{ICON_DOC}</Icon>} />
        <StatCard label="Ganados" value={ganado} icon={<Icon>{ICON_CHECK}</Icon>} />
      </div>

      {/* Funnel */}
      <GlassCard className="p-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Embudo por etapa</h2>
        <div className="space-y-2.5">
          {LEAD_STATUSES.map((s) => {
            const n = by[s] ?? 0;
            const pct = total > 0 ? Math.round((n / total) * 100) : 0;
            const width = n > 0 ? Math.max((n / maxByStatus) * 100, 6) : 0;
            return (
              <div key={s} className="flex items-center gap-3">
                <span className="w-36 flex-none text-sm text-muted-foreground">{STATUS_LABELS[s]}</span>
                <div className="h-6 flex-1 overflow-hidden rounded-md bg-black/[0.04] dark:bg-white/[0.06]">
                  <div
                    className="h-full rounded-md bg-accent transition-[width] duration-700"
                    style={{ width: `${width}%` }}
                  />
                </div>
                <span className="w-20 flex-none text-right text-sm tabular-nums">
                  {n} <span className="text-muted-foreground">· {pct}%</span>
                </span>
              </div>
            );
          })}
        </div>
      </GlassCard>
    </div>
  );
}
