"use client";
import type { GeoResult } from "@/lib/types";

function Chip({ children }: { children: React.ReactNode }) {
  return (
    <span className="mr-1 inline-block rounded-md border border-black/15 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground dark:border-white/15">
      {children}
    </span>
  );
}

function Row({ icon, children }: { icon: string; children: React.ReactNode }) {
  return <div className="flex gap-1.5 text-xs leading-relaxed"><span>{icon}</span><span className="min-w-0 break-words">{children}</span></div>;
}

export default function BusinessPopup({ r, imported, importing, error, onImport }: {
  r: GeoResult; imported: boolean; importing: boolean; error: string | null;
  onImport: (r: GeoResult) => void;
}) {
  const d = r.details;
  return (
    <div className="w-60">
      <div className="text-sm font-bold leading-tight">{r.name}</div>
      <div className="mt-1">
        {d.category && <Chip>{d.category.replace(/_/g, " ")}</Chip>}
        {d.brand && <Chip>{d.brand}</Chip>}
        {d.wheelchair === "yes" && <Chip>♿ accesible</Chip>}
        {d.delivery && <Chip>delivery</Chip>}
        {d.takeaway && <Chip>para llevar</Chip>}
      </div>
      <div className="mt-2 space-y-1">
        {r.address && <Row icon="📍">{r.address}</Row>}
        {d.opening_hours && <Row icon="🕐">{d.opening_hours}</Row>}
        {r.phone && <Row icon="📞"><a className="hover:underline" href={`tel:${r.phone}`}>{r.phone}</a></Row>}
        {r.website && <Row icon="🌐"><a className="underline underline-offset-2" href={r.website} target="_blank" rel="noreferrer">{r.website.replace(/^https?:\/\//, "")}</a></Row>}
        {d.email && <Row icon="✉️"><a className="hover:underline" href={`mailto:${d.email}`}>{d.email}</a></Row>}
        {d.instagram && <Row icon="📷">{d.instagram}</Row>}
        {d.facebook && <Row icon="📘">{d.facebook}</Row>}
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button
          className="rounded-lg bg-accent px-3 py-1.5 text-xs font-semibold text-accent-foreground transition-opacity hover:opacity-85 disabled:opacity-40"
          disabled={imported || importing} onClick={() => onImport(r)}>
          {imported ? "Ya en tu CRM ✓" : importing ? "Importando…" : "+ Enviar al CRM"}
        </button>
        <a className="rounded-lg border border-black/15 px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-black/[0.04] dark:border-white/15 dark:hover:bg-white/[0.06]"
           href={r.google_maps_url} target="_blank" rel="noreferrer">Google Maps ↗</a>
      </div>
      {error && <p className="mt-2 text-xs text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}
