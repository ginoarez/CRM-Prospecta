// Corrector ortográfico español 100% local (nspell + dictionary-es).
// El diccionario se descarga del CDN una vez y queda en caché del navegador.
// @ts-expect-error - nspell no trae tipos
import nspell from "nspell";

let spellerPromise: Promise<any> | null = null;

const DICT_AFF = "https://cdn.jsdelivr.net/npm/dictionary-es/index.aff";
const DICT_DIC = "https://cdn.jsdelivr.net/npm/dictionary-es/index.dic";

export function loadSpeller(): Promise<any> {
  if (!spellerPromise) {
    spellerPromise = (async () => {
      const [aff, dic] = await Promise.all([
        fetch(DICT_AFF).then((r) => r.text()),
        fetch(DICT_DIC).then((r) => r.text()),
      ]);
      return nspell(aff, dic);
    })().catch((e) => {
      spellerPromise = null; // permitir reintento
      throw e;
    });
  }
  return spellerPromise;
}

// Pura y testeable: recorre palabras y aplica `suggest` (que devuelve corrección o null).
const WORD = /[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+/g;

export function applySpelling(text: string, suggest: (w: string) => string | null): string {
  return text.replace(WORD, (w) => {
    const s = suggest(w);
    if (!s || s === w) return w;
    // Conservar mayúscula inicial de la palabra original.
    return /^[A-ZÁÉÍÓÚÜÑ]/.test(w) ? s.charAt(0).toUpperCase() + s.slice(1) : s;
  });
}

export async function fixSpelling(text: string): Promise<string> {
  const sp = await loadSpeller();
  return applySpelling(text, (w) =>
    sp.correct(w) ? null : (sp.suggest(w)[0] ?? null),
  );
}
