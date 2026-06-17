"use client";
import { useState } from "react";

export function NewLeadDialog({ onCreate }: { onCreate: (data: Record<string, string>) => void }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ business_name: "", city: "", country: "", phone: "" });

  if (!open) return <button className="rounded bg-blue-600 px-3 py-1 text-white" onClick={() => setOpen(true)}>+ Nuevo lead</button>;

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/30">
      <div className="w-96 space-y-2 rounded bg-white p-4">
        <h3 className="font-semibold">Nuevo lead</h3>
        {(["business_name", "city", "country", "phone"] as const).map((f) => (
          <input key={f} className="w-full rounded border p-2" placeholder={f}
            value={form[f]} onChange={(e) => setForm({ ...form, [f]: e.target.value })} />
        ))}
        <div className="flex justify-end gap-2">
          <button onClick={() => setOpen(false)}>Cancelar</button>
          <button className="rounded bg-blue-600 px-3 py-1 text-white"
            onClick={() => { onCreate(form); setOpen(false); setForm({ business_name: "", city: "", country: "", phone: "" }); }}>
            Crear
          </button>
        </div>
      </div>
    </div>
  );
}
