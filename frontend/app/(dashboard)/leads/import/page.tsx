"use client";
import { useState } from "react";
import { api } from "@/lib/api-client";
import { GlassCard } from "@/components/ui/glass-card";

interface ImportResult { created: number; errors: { row: number; error: string }[]; }

export default function ImportPage() {
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError(null);
    const fd = new FormData();
    fd.append("file", file);
    try {
      setResult(await api<ImportResult>("/leads/import-csv", { method: "POST", body: fd }));
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="flex max-w-lg flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Importar leads</h1>
        <p className="text-sm text-muted-foreground">
          CSV con columnas: business_name, industry, city, country, phone, email, website,
          company_size, employees, notes.
        </p>
      </div>
      <GlassCard className="p-5">
        <label className="flex cursor-pointer flex-col items-center gap-2 rounded-lg border border-dashed border-black/20 p-8 text-sm text-muted-foreground transition-colors hover:border-black/40 dark:border-white/20 dark:hover:border-white/40">
          <span className="font-medium text-foreground">Elegir archivo CSV</span>
          <span className="text-xs">se importa al seleccionarlo</span>
          <input type="file" accept=".csv" className="hidden" onChange={upload} />
        </label>
        {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {result && (
          <div className="mt-4">
            <p className="font-medium">Creados: {result.created}</p>
            {result.errors.length > 0 && (
              <ul className="mt-2 text-sm text-red-600 dark:text-red-400">
                {result.errors.map((e) => <li key={e.row}>Fila {e.row}: {e.error}</li>)}
              </ul>
            )}
          </div>
        )}
      </GlassCard>
    </div>
  );
}
