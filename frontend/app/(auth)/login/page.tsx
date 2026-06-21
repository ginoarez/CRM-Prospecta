"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api-client";
import { useAuth } from "@/lib/auth-store";
import DotField from "@/components/ui/DotField";

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
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#0b0a0f]">
      <div className="absolute inset-0">
        <DotField dotRadius={1.5} dotSpacing={14} bulgeStrength={67} glowRadius={160}
                  sparkle={false} waveAmplitude={0} />
      </div>
      <form onSubmit={submit} className="relative z-10 w-80 space-y-3 rounded-lg bg-white p-6 shadow-2xl">
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
