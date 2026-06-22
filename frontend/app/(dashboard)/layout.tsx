"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-store";
import { GlassCard } from "@/components/ui/glass-card";
import { ThemeToggle } from "@/components/ui/theme-toggle";

const NAV = [
  { href: "/", label: "Dashboard" },
  { href: "/leads", label: "Leads" },
  { href: "/leads/import", label: "Importar CSV" },
  { href: "/buscar", label: "Buscar (OSM)" },
  { href: "/plantillas", label: "Plantillas" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { accessToken, clear } = useAuth();

  useEffect(() => {
    if (!accessToken) router.replace("/login");
  }, [accessToken, router]);

  if (!accessToken) return null;

  return (
    <div className="flex min-h-screen gap-4 p-4">
      <GlassCard className="flex w-56 flex-none flex-col p-4">
        <h2 className="mb-6 px-2 text-lg font-bold tracking-tight">Prospecta</h2>
        <nav className="flex flex-col gap-1">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-lg px-3 py-2 text-sm transition-colors ${
                  active
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-black/[0.04] dark:hover:bg-white/[0.06]"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
        <button
          className="mt-auto rounded-lg px-3 py-2 text-left text-sm text-muted-foreground hover:bg-black/[0.04] dark:hover:bg-white/[0.06]"
          onClick={() => { clear(); router.replace("/login"); }}
        >
          Salir
        </button>
      </GlassCard>

      <div className="flex min-w-0 flex-1 flex-col gap-4">
        <GlassCard className="flex items-center justify-between px-5 py-3">
          <span className="text-sm font-medium text-muted-foreground">CRM</span>
          <ThemeToggle />
        </GlassCard>
        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
