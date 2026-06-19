"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Template } from "@/lib/types";

export default function PlantillasPage() {
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [body, setBody] = useState("");

  const { data: templates } = useQuery({
    queryKey: ["templates"],
    queryFn: () => api<Template[]>("/templates"),
  });

  const create = useMutation({
    mutationFn: () =>
      api<Template>("/templates", {
        method: "POST",
        body: JSON.stringify({ name, channel: "wa", body }),
      }),
    onSuccess: () => { setName(""); setBody(""); qc.invalidateQueries({ queryKey: ["templates"] }); },
  });

  const remove = useMutation({
    mutationFn: (id: string) => api(`/templates/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["templates"] }),
  });

  return (
    <div className="max-w-2xl space-y-4">
      <h1 className="text-2xl font-bold">Plantillas</h1>
      <p className="text-sm text-gray-600">
        Variables disponibles: {"{business_name}"}, {"{city}"}, {"{country}"}, {"{industry}"}.
        Las desconocidas se dejan tal cual para completarlas a mano.
      </p>

      <div className="space-y-2 rounded bg-white p-3 shadow">
        <input className="w-full rounded border p-2" placeholder="Nombre"
               value={name} onChange={(e) => setName(e.target.value)} />
        <textarea className="w-full rounded border p-2 text-sm" rows={3} placeholder="Cuerpo del mensaje"
                  value={body} onChange={(e) => setBody(e.target.value)} />
        <button className="rounded bg-blue-600 px-3 py-2 text-white disabled:opacity-50"
                disabled={!name || !body || create.isPending} onClick={() => create.mutate()}>
          Crear plantilla
        </button>
      </div>

      <ul className="space-y-2">
        {(templates ?? []).map((t) => (
          <li key={t.id} className="rounded bg-white p-3 shadow">
            <div className="flex items-center justify-between">
              <span className="font-medium">{t.name} <span className="text-xs text-gray-400">({t.channel})</span></span>
              <button className="text-sm text-red-600" onClick={() => remove.mutate(t.id)}>Borrar</button>
            </div>
            <p className="mt-1 text-sm text-gray-700">{t.body}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
