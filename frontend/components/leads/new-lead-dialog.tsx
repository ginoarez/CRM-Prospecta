"use client";
import { useState } from "react";
import { GlassCard } from "@/components/ui/glass-card";
import { Button, Input } from "@/components/ui/controls";

const FIELD_LABELS = {
  business_name: "Nombre del negocio",
  city: "Ciudad",
  country: "País",
  phone: "Teléfono",
} as const;

export function NewLeadDialog({ onCreate }: { onCreate: (data: Record<string, string>) => void }) {
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ business_name: "", city: "", country: "", phone: "" });

  if (!open) return <Button onClick={() => setOpen(true)}>+ Nuevo lead</Button>;

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <GlassCard className="w-96 bg-background/80 p-5 dark:bg-background/80">
        <h3 className="mb-3 font-semibold">Nuevo lead</h3>
        <div className="space-y-2">
          {(Object.keys(FIELD_LABELS) as (keyof typeof FIELD_LABELS)[]).map((f) => (
            <Input key={f} className="w-full" placeholder={FIELD_LABELS[f]}
              value={form[f]} onChange={(e) => setForm({ ...form, [f]: e.target.value })} />
          ))}
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setOpen(false)}>Cancelar</Button>
          <Button
            disabled={!form.business_name}
            onClick={() => { onCreate(form); setOpen(false); setForm({ business_name: "", city: "", country: "", phone: "" }); }}>
            Crear
          </Button>
        </div>
      </GlassCard>
    </div>
  );
}
