"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import type { Template } from "@/lib/types";
import { GlassCard } from "@/components/ui/glass-card";
import { Button, Input, Textarea } from "@/components/ui/controls";

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
    <div className="flex max-w-2xl flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Plantillas</h1>
        <p className="text-sm text-muted-foreground">
          Variables: {"{business_name}"}, {"{city}"}, {"{country}"}, {"{industry}"}.
          Las desconocidas se dejan tal cual para completarlas a mano.
        </p>
      </div>

      <GlassCard className="space-y-2 p-5">
        <Input className="w-full" placeholder="Nombre"
               value={name} onChange={(e) => setName(e.target.value)} />
        <Textarea className="w-full" rows={3} placeholder="Cuerpo del mensaje"
                  value={body} onChange={(e) => setBody(e.target.value)} />
        <Button disabled={!name || !body || create.isPending} onClick={() => create.mutate()}>
          Crear plantilla
        </Button>
      </GlassCard>

      <ul className="space-y-3">
        {(templates ?? []).map((t) => (
          <GlassCard key={t.id} className="p-4">
            <div className="flex items-center justify-between">
              <span className="font-medium">
                {t.name}{" "}
                <span className="rounded-md border border-black/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground dark:border-white/10">
                  {t.channel}
                </span>
              </span>
              <button className="text-sm text-red-600 hover:underline dark:text-red-400" onClick={() => remove.mutate(t.id)}>
                Borrar
              </button>
            </div>
            <p className="mt-1.5 text-sm text-muted-foreground">{t.body}</p>
          </GlassCard>
        ))}
      </ul>
    </div>
  );
}
