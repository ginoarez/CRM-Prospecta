"use client";
import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api-client";
import type { GeoCategory, GeoResult, GeoSearchResponse, GeoImportResult } from "@/lib/types";

const MapView = dynamic(() => import("@/components/geo/map-view"), { ssr: false });

export default function BuscarPage() {
  const [categories, setCategories] = useState<GeoCategory[]>([]);
  const [location, setLocation] = useState("");
  const [category, setCategory] = useState("");
  const [results, setResults] = useState<GeoResult[]>([]);
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importMsg, setImportMsg] = useState<string | null>(null);

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
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Buscar negocios (OSM)</h1>
      <form onSubmit={runSearch} className="flex flex-wrap items-end gap-3">
        <div>
          <label className="block text-sm">Lugar</label>
          <input className="rounded border p-2" value={location} required
                 onChange={(e) => setLocation(e.target.value)} placeholder="Palermo, Buenos Aires" />
        </div>
        <div>
          <label className="block text-sm">Categoría</label>
          <select className="rounded border p-2" value={category}
                  onChange={(e) => setCategory(e.target.value)}>
            {categories.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
          </select>
        </div>
        <button className="rounded bg-blue-600 px-4 py-2 text-white" disabled={loading}>
          {loading ? "Buscando…" : "Buscar"}
        </button>
      </form>

      {error && <p className="text-red-600">{error}</p>}

      {results.length > 0 && (
        <>
          <MapView results={results} />
          <div className="flex items-center gap-3">
            <button type="button" className="rounded bg-green-600 px-4 py-2 text-white"
                    onClick={sendToCrm} disabled={chosen.length === 0}>
              Enviar al CRM ({chosen.length})
            </button>
            {importMsg && <span className="text-green-700">{importMsg}</span>}
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left">
                <th></th><th>Nombre</th><th>Teléfono</th><th>Web</th><th>Dirección</th><th></th>
              </tr>
            </thead>
            <tbody>
              {results.map((r) => (
                <tr key={r.osm_id} className="border-t">
                  <td>
                    <input type="checkbox" checked={!!selected[r.osm_id]}
                           onChange={(e) => setSelected((s) => ({ ...s, [r.osm_id]: e.target.checked }))} />
                  </td>
                  <td>{r.name}</td>
                  <td>{r.phone ?? "—"}</td>
                  <td>{r.website ? <a className="text-blue-600" href={r.website} target="_blank" rel="noreferrer">link</a> : "—"}</td>
                  <td>{r.address ?? "—"}</td>
                  <td>{r.already_imported && <span className="text-xs text-gray-500">ya importado</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
