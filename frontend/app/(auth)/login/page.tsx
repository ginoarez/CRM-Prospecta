"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { api } from "@/lib/api-client";
import { useAuth } from "@/lib/auth-store";

const FaultyTerminal = dynamic(() => import("@/components/ui/FaultyTerminal"), { ssr: false });

export default function LoginPage() {
  const router = useRouter();
  const setTokens = useAuth((s) => s.setTokens);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      if (mode === "register") {
        await api("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) });
      }
      const t = await api<{ access_token: string; refresh_token: string }>(
        "/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }
      );
      setTokens(t.access_token, t.refresh_token);
      router.push("/");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-black">
      <div className="absolute inset-0">
        <FaultyTerminal scale={2.5} gridMul={[2, 1]} digitSize={0.9} timeScale={1.5}
          pause={false} scanlineIntensity={0.6} glitchAmount={1} flickerAmount={1}
          noiseAmp={1} chromaticAberration={0} dither={0} curvature={0} tint="#ffffff"
          mouseReact={true} mouseStrength={0.4} pageLoadAnimation={false} brightness={0.5} />
      </div>
      <form onSubmit={submit} className="relative z-10 w-80 space-y-3 rounded-lg bg-white/95 p-6 shadow-2xl backdrop-blur">
        <h1 className="text-xl font-semibold">Prospecta · {mode === "login" ? "Entrar" : "Registro"}</h1>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <input className="w-full rounded border p-2" placeholder="Email" type="email"
          value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="w-full rounded border p-2" placeholder="Contraseña" type="password"
          value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button className="w-full rounded bg-blue-600 p-2 text-white" type="submit">
          {mode === "login" ? "Entrar" : "Crear cuenta"}
        </button>
        <button type="button" className="w-full text-sm text-blue-600"
          onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Crear una cuenta" : "Ya tengo cuenta"}
        </button>
      </form>
    </div>
  );
}
