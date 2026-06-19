"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-store";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { accessToken, clear } = useAuth();

  useEffect(() => {
    if (!accessToken) router.replace("/login");
  }, [accessToken, router]);

  if (!accessToken) return null;

  return (
    <div className="flex min-h-screen">
      <aside className="w-56 space-y-2 bg-white p-4 shadow">
        <h2 className="mb-4 font-bold">Prospecta</h2>
        <Link className="block" href="/">Dashboard</Link>
        <Link className="block" href="/leads">Leads</Link>
        <Link className="block" href="/leads/import">Importar CSV</Link>
        <Link className="block" href="/buscar">Buscar (OSM)</Link>
        <Link className="block" href="/plantillas">Plantillas</Link>
        <button className="mt-6 text-sm text-red-600" onClick={() => { clear(); router.replace("/login"); }}>
          Salir
        </button>
      </aside>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
