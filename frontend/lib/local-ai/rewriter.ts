type Msg = { role: "system" | "user" | "assistant"; content: string };
type Pending = { resolve: (s: string) => void; reject: (e: Error) => void };

let worker: Worker | null = null;
let progressCb: ((p: number) => void) | null = null;
const pending = new Map<string, Pending>();

function getWorker(): Worker {
  if (!worker) {
    worker = new Worker(new URL("./rewriter.worker.ts", import.meta.url), { type: "module" });
    worker.onmessage = (e: MessageEvent) => {
      const { id, type, text, error, progress } = e.data;
      if (type === "progress") {
        const pct = typeof progress?.progress === "number" ? progress.progress / 100 : 0;
        progressCb?.(pct);
        return;
      }
      const p = pending.get(id);
      if (!p) return;
      pending.delete(id);
      if (type === "error") p.reject(new Error(error));
      else p.resolve(text);
    };
  }
  return worker;
}

function run(messages: Msg[], onProgress?: (p: number) => void): Promise<string> {
  progressCb = onProgress ?? null;
  const id = crypto.randomUUID();
  return new Promise<string>((resolve, reject) => {
    pending.set(id, { resolve, reject });
    getWorker().postMessage({ id, messages });
  });
}

const SYSTEM =
  "Eres un asistente de redacción en español para mensajes de ventas por WhatsApp y email. " +
  "Respondes SOLO con el mensaje final, sin explicaciones ni comillas.";

export function improve(text: string, onProgress?: (p: number) => void): Promise<string> {
  return run(
    [
      { role: "system", content: SYSTEM },
      {
        role: "user",
        content:
          "Reescribe este mensaje en español manteniendo el mismo significado e idioma, " +
          "con tono profesional, claro y cordial. No inventes datos.\n\n" + text,
      },
    ],
    onProgress,
  );
}

export function draft(instruction: string, context?: string, onProgress?: (p: number) => void): Promise<string> {
  const ctx = context ? `\n\nContexto: ${context}` : "";
  return run(
    [
      { role: "system", content: SYSTEM },
      { role: "user", content: `Redacta un mensaje breve en español para: ${instruction}${ctx}` },
    ],
    onProgress,
  );
}
