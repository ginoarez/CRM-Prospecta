"use client";
import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { GeoCategory, GeoResult, GeoSearchResponse, GeoImportResult } from "@/lib/types";
import type { MapFocus } from "@/components/geo/map-view";
import { GlassCard } from "@/components/ui/glass-card";
import { Button, Input, Select } from "@/components/ui/controls";

const MapView = dynamic(() => import("@/components/geo/map-view"), { ssr: false });

export default function BuscarPage() {
  const qc = useQueryClient();
  const [categories, setCategories] = useState<GeoCategory[]>([]);
  const [location, setLocation] = useState("");
  const [category, setCategory] = useState("");
  const [results, setResults] = useState<GeoResult[]>([]);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importMsg, setImportMsg] = useState<string | null>(null);
  const [focus, setFocus] = useState<MapFocus | null>(null);
  const [importedIds, setImportedIds] = useState<Set<string>>(new Set());
  const [importingId, setImportingId] = useState<string | null>(null);
  const [importErr, setImportErr] = useState<string | null>(null);

  useEffect(() => {
    api<GeoCategory[]>("/geo/categories")
      .then((cs) => { setCategories(cs); if (cs[0]) setCategory(cs[0].key); })
      .catch((e) => setError((e as Error).message));
  }, []);

  async function runSearch(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setImportMsg(null);
    setLoading(true);
    try {
      const res = await api<GeoSearchResponse>("/geo/search", {
        method: "POST",
        body: JSON.stringify({ location, category }),
      });
      setResults(res.results);
      const sel: Record<string, boolean> = {};
      res.results.forEach((r) => { sel[r.osm_id] = !r.already_imported; });
      setSelected(sel);
    } catch (err) {
      setError((err as Error).message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  const chosen = useMemo(
    () => results.filter((r) => selected[r.osm_id]),
    [results, selected],
  );

  async function importOne(r: GeoResult) {
    setImportingId(r.osm_id); setImportErr(null);
    try {
      await api<GeoImportResult>("/geo/import", {
        method: "POST",
        body: JSON.stringify({ items: [{ osm_id: r.osm_id, name: r.name, lat: r.lat, lng: r.lng,
          website: r.website, phone: r.phone, address: r.address, category }] }),
      });
      setImportedIds((s) => new Set(s).add(r.osm_id));
      qc.invalidateQueries({ queryKey: ["leads"] });
    } catch (err) {
      setImportErr((err as Error).message);
    } finally {
      setImportingId(null);
    }
  }

  async function sendToCrm() {
    setImportMsg(null);
    const items = chosen.map((r) => ({
      osm_id: r.osm_id, name: r.name, lat: r.lat, lng: r.lng,
      website: r.website, phone: r.phone, address: r.address, category,
    }));
    try {
      const res = await api<GeoImportResult>("/geo/import", {
        method: "POST",
        body: JSON.stringify({ items }),
      });
      setImportMsg(`Creados: ${res.created} · Ya existían: ${res.skipped_existing}`);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Buscar negocios</h1>
        <p className="text-sm text-muted-foreground">Prospección sobre OpenStreetMap por lugar y categoría</p>
      </div>

      <GlassCard className="p-5">
        <form onSubmit={runSearch} className="flex flex-wrap items-end gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Lugar</label>
            <Input className="w-64" value={location} required
                   onChange={(e) => setLocation(e.target.value)} placeholder="Palermo, Buenos Aires" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Categoría</label>
            <Select value={category} onChange={(e) => setCategory(e.target.value)}>
              {categories.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
            </Select>
          </div>
          <Button disabled={loading}>{loading ? "Buscando…" : "Buscar"}</Button>
        </form>
        {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
      </GlassCard>

      {results.length > 0 && (
        <>
          <GlassCard className="overflow-hidden p-1.5">
            <MapView results={results} focus={focus} onImport={importOne} importedIds={importedIds}
                      importingId={importingId} importError={importErr} />
          </GlassCard>
          <div className="flex items-center gap-3">
            <Button type="button" onClick={sendToCrm} disabled={chosen.length === 0}>
              Enviar al CRM ({chosen.length})
            </Button>
            {importMsg && <span className="text-sm text-muted-foreground">{importMsg}</span>}
          </div>
          <GlassCard className="overflow-x-auto p-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                  <th className="pb-2"></th><th className="pb-2">Nombre</th><th className="pb-2">Teléfono</th>
                  <th className="pb-2">Web</th><th className="pb-2">Dirección</th><th className="pb-2"></th>
                </tr>
              </thead>
              <tbody>
                {results.map((r) => (
                  <tr key={r.osm_id} className="border-t border-black/10 dark:border-white/10">
                    <td className="py-2 pr-2">
                      <input type="checkbox" className="accent-current" checked={!!selected[r.osm_id]}
                             onChange={(e) => setSelected((s) => ({ ...s, [r.osm_id]: e.target.checked }))} />
                    </td>
                    <td className="py-2 pr-3 font-medium">
                      <button className="text-left font-medium underline-offset-2 hover:underline"
                              onClick={() => setFocus({ osmId: r.osm_id, ts: Date.now() })}>{r.name}</button>
                    </td>
                    <td className="py-2 pr-3">{r.phone ?? "—"}</td>
                    <td className="py-2 pr-3">
                      {r.website
                        ? <a className="underline underline-offset-2 hover:text-muted-foreground" href={r.website} target="_blank" rel="noreferrer">link</a>
                        : "—"}
                    </td>
                    <td className="py-2 pr-3 text-muted-foreground">{r.address ?? "—"}</td>
                    <td className="py-2">{(r.already_imported || importedIds.has(r.osm_id)) && <span className="text-xs text-muted-foreground">ya importado</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </GlassCard>
        </>
      )}
    </div>
  );
}
