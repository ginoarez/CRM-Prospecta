// Web Worker: generación de texto con Transformers.js (Qwen2.5-0.5B-Instruct).
// Transformers.js se carga desde el CDN en runtime (webpackIgnore) para no empaquetar
// onnxruntime/wasm en el build de Next.
const CDN = "https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.2.0";
const MODEL = "onnx-community/Qwen2.5-0.5B-Instruct";

let tf: any = null;
let generator: any = null;

async function getGenerator(progress: (p: any) => void) {
  if (!tf) {
    tf = await import(/* webpackIgnore: true */ CDN);
    tf.env.allowLocalModels = false; // usar el CDN de Hugging Face
  }
  if (!generator) {
    try {
      generator = await tf.pipeline("text-generation", MODEL, {
        dtype: "q4",
        device: "webgpu",
        progress_callback: progress,
      });
    } catch {
      generator = await tf.pipeline("text-generation", MODEL, {
        dtype: "q4",
        device: "wasm",
        progress_callback: progress,
      });
    }
  }
  return generator;
}

function extractReply(out: any): string {
  const g = out?.[0]?.generated_text;
  if (Array.isArray(g)) return (g[g.length - 1]?.content ?? "").trim();
  return String(g ?? "").trim();
}

self.onmessage = async (e: MessageEvent) => {
  const { id, messages } = e.data;
  try {
    const gen = await getGenerator((p) =>
      self.postMessage({ type: "progress", progress: p }),
    );
    const out = await gen(messages, {
      max_new_tokens: 220,
      do_sample: false,
      return_full_text: false,
    });
    self.postMessage({ id, type: "result", text: extractReply(out) });
  } catch (err) {
    self.postMessage({ id, type: "error", error: String(err) });
  }
};
