"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, downloadFile } from "@/lib/api-client";
import type { Meeting } from "@/lib/types";
import { GlassCard } from "@/components/ui/glass-card";
import { Button, Input, Textarea } from "@/components/ui/controls";

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
    <div className="max-w-2xl space-y-4">
      <GlassCard className="space-y-2 p-4">
        <Input className="w-full" placeholder="Título de la cita"
               value={title} onChange={(e) => setTitle(e.target.value)} />
        <div className="flex gap-2">
          <Input type="datetime-local" value={when}
                 onChange={(e) => setWhen(e.target.value)} />
          <Input type="number" className="w-24" value={duration}
                 onChange={(e) => setDuration(Number(e.target.value))} placeholder="min" />
        </div>
        <Input className="w-full" placeholder="Lugar o enlace de video"
               value={location} onChange={(e) => setLocation(e.target.value)} />
        <Textarea className="w-full" placeholder="Notas"
                  value={notes} onChange={(e) => setNotes(e.target.value)} />
        <Button onClick={() => create.mutate()} disabled={!title || !when}>
          Programar cita
        </Button>
        {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
      </GlassCard>

      <ul className="space-y-2">
        {(meetings ?? []).map((m) => (
          <GlassCard key={m.id} className="p-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="font-medium">{m.title}</span>
              <span className="rounded-md border border-black/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground dark:border-white/10">
                {m.status}
              </span>
              <span className="text-muted-foreground">{new Date(m.scheduled_at).toLocaleString()} · {m.duration_minutes} min</span>
            </div>
            {m.location && <div className="mt-0.5 text-muted-foreground">{m.location}</div>}
            <div className="mt-2 flex flex-wrap gap-3">
              <a className="underline underline-offset-2 hover:text-muted-foreground" href={m.google_calendar_url} target="_blank" rel="noreferrer">Añadir a Google Calendar</a>
              <button className="underline underline-offset-2 hover:text-muted-foreground"
                      onClick={() => downloadFile(`/meetings/${m.id}/ics`, `cita-${m.id}.ics`)}>Descargar .ics</button>
              {m.status === "programada" && (
                <>
                  <button className="underline underline-offset-2 hover:text-muted-foreground" onClick={() => setStatus.mutate({ id: m.id, status: "realizada" })}>Marcar realizada</button>
                  <button className="text-red-600 underline underline-offset-2 dark:text-red-400" onClick={() => setStatus.mutate({ id: m.id, status: "cancelada" })}>Cancelar</button>
                </>
              )}
            </div>
          </GlassCard>
        ))}
      </ul>
    </div>
  );
}
