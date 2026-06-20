"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, downloadFile } from "@/lib/api-client";
import type { Meeting } from "@/lib/types";

export default function AgendaPanel({ leadId }: { leadId: string }) {
  const qc = useQueryClient();
  const [title, setTitle] = useState("");
  const [when, setWhen] = useState("");
  const [duration, setDuration] = useState(30);
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: meetings } = useQuery({
    queryKey: ["meetings", leadId],
    queryFn: () => api<Meeting[]>(`/leads/${leadId}/meetings`),
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ["meetings", leadId] });

  const create = useMutation({
    mutationFn: () => api<Meeting>(`/leads/${leadId}/meetings`, {
      method: "POST",
      body: JSON.stringify({
        title, scheduled_at: new Date(when).toISOString(),
        duration_minutes: Number(duration) || 30,
        location: location || null, notes: notes || null,
      }),
    }),
    onSuccess: () => { setTitle(""); setWhen(""); setLocation(""); setNotes(""); setError(null); invalidate(); },
    onError: (e) => setError((e as Error).message),
  });

  const setStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api<Meeting>(`/meetings/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }),
    onSuccess: invalidate,
  });

  return (
    <div className="space-y-4">
      <div className="space-y-2 rounded bg-white p-3 shadow">
        <input className="w-full rounded border p-2" placeholder="Título de la cita"
               value={title} onChange={(e) => setTitle(e.target.value)} />
        <div className="flex gap-2">
          <input type="datetime-local" className="rounded border p-2" value={when}
                 onChange={(e) => setWhen(e.target.value)} />
          <input type="number" className="w-24 rounded border p-2" value={duration}
                 onChange={(e) => setDuration(Number(e.target.value))} placeholder="min" />
        </div>
        <input className="w-full rounded border p-2" placeholder="Lugar o enlace de video"
               value={location} onChange={(e) => setLocation(e.target.value)} />
        <textarea className="w-full rounded border p-2" placeholder="Notas"
                  value={notes} onChange={(e) => setNotes(e.target.value)} />
        <button className="rounded bg-blue-600 px-3 py-2 text-white disabled:opacity-50"
                onClick={() => create.mutate()} disabled={!title || !when}>
          Programar cita
        </button>
        {error && <p className="text-red-600">{error}</p>}
      </div>

      <ul className="space-y-2">
        {(meetings ?? []).map((m) => (
          <li key={m.id} className="rounded bg-white p-3 text-sm shadow">
            <div className="flex items-center gap-2">
              <span className="font-medium">{m.title}</span>
              <span className="rounded bg-gray-100 px-2 py-0.5 text-xs">{m.status}</span>
              <span className="text-gray-500">{new Date(m.scheduled_at).toLocaleString()} · {m.duration_minutes} min</span>
            </div>
            {m.location && <div className="text-gray-600">{m.location}</div>}
            <div className="mt-2 flex flex-wrap gap-3">
              <a className="text-blue-600 underline" href={m.google_calendar_url} target="_blank" rel="noreferrer">Añadir a Google Calendar</a>
              <button className="text-blue-600 underline"
                      onClick={() => downloadFile(`/meetings/${m.id}/ics`, `cita-${m.id}.ics`)}>Descargar .ics</button>
              {m.status === "programada" && (
                <>
                  <button className="text-green-600 underline" onClick={() => setStatus.mutate({ id: m.id, status: "realizada" })}>Marcar realizada</button>
                  <button className="text-red-600 underline" onClick={() => setStatus.mutate({ id: m.id, status: "cancelada" })}>Cancelar</button>
                </>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
