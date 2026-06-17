"use client";
import { useState } from "react";
import { api } from "@/lib/api-client";

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
    <div className="max-w-lg space-y-4">
      <h1 className="text-2xl font-bold">Importar leads (CSV)</h1>
      <p className="text-sm text-gray-600">
        Columnas reconocidas: business_name, industry, city, country, phone, email, website,
        company_size, employees, notes.
      </p>
      <input type="file" accept=".csv" onChange={upload} />
      {error && <p className="text-red-600">{error}</p>}
      {result && (
        <div className="rounded bg-white p-3 shadow">
          <p className="font-medium text-green-700">Creados: {result.created}</p>
          {result.errors.length > 0 && (
            <ul className="mt-2 text-sm text-red-600">
              {result.errors.map((e) => <li key={e.row}>Fila {e.row}: {e.error}</li>)}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
