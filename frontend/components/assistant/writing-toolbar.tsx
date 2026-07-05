"use client";
import { useState } from "react";
import { fixSpelling } from "@/lib/local-ai/spell";
import { improve, draft } from "@/lib/local-ai/rewriter";

export default function WritingToolbar({
  value,
  onChange,
  context,
}: {
  value: string;
  onChange: (s: string) => void;
  context?: string;
}) {
  const [busy, setBusy] = useState<null | "spell" | "improve" | "draft">(null);
  const [progress, setProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runSpell() {
    setBusy("spell");
    setError(null);
    try {
      onChange(await fixSpelling(value));
    } catch {
      setError("No se pudo cargar el diccionario.");
    } finally {
      setBusy(null);
    }
  }

  async function runGen(kind: "improve" | "draft") {
    setBusy(kind);
    setError(null);
    setProgress(0);
    try {
      const onP = (p: number) => setProgress(p);
      const out =
        kind === "improve"
          ? await improve(value, onP)
          : await draft(value || "un primer contacto cordial", context, onP);
      if (out) onChange(out);
    } catch {
      setError("La IA local no está disponible en este navegador.");
    } finally {
      setBusy(null);
      setProgress(null);
    }
  }

  const label =
    busy === "spell"
      ? "Corrigiendo…"
      : busy && progress !== null && progress < 1
        ? `Descargando modelo… ${Math.round(progress * 100)}%`
        : busy
          ? "Pensando…"
          : null;

  return (
    <div className="space-y-1">
      <div className="flex flex-wrap gap-2">
        <button type="button" className="rounded-md border border-black/10 px-2 py-1 text-xs transition-colors hover:bg-black/[0.04] disabled:opacity-50 dark:border-white/10 dark:hover:bg-white/[0.06]"
                onClick={runSpell} disabled={!!busy || !value}>
          Corregir ortografía
        </button>
        <button type="button" className="rounded-md border border-black/10 px-2 py-1 text-xs transition-colors hover:bg-black/[0.04] disabled:opacity-50 dark:border-white/10 dark:hover:bg-white/[0.06]"
                onClick={() => runGen("improve")} disabled={!!busy || !value}>
          Reescribir
        </button>
        <button type="button" className="rounded-md border border-black/10 px-2 py-1 text-xs transition-colors hover:bg-black/[0.04] disabled:opacity-50 dark:border-white/10 dark:hover:bg-white/[0.06]"
                onClick={() => runGen("draft")} disabled={!!busy}>
          Redactar
        </button>
        {label && <span className="self-center text-xs text-muted-foreground">{label}</span>}
      </div>
      {error && <p className="text-xs text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}
