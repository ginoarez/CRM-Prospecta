"use client";
import { memo } from "react";
import dynamic from "next/dynamic";
import { useTheme } from "next-themes";

const Threads = dynamic(() => import("@/components/ui/Threads"), { ssr: false });

// Referencias estables a nivel de módulo (evitan recrear el contexto WebGL).
const COLOR_DARK: [number, number, number] = [1, 1, 1];
const COLOR_LIGHT: [number, number, number] = [0.1, 0.1, 0.1];

/**
 * Fondo del interior del CRM: hilos WebGL (React Bits) monocromos detrás de
 * todo el shell. Memoizado y sin props del padre, así NO se re-renderiza al
 * navegar entre páginas — el contexto WebGL persiste (un solo canvas). El color
 * sigue al tema (líneas claras en oscuro, oscuras en claro). `fixed` + sin
 * pointer-events; las tarjetas glass lo difuminan por detrás.
 */
function InteriorBackground() {
  const { resolvedTheme } = useTheme();
  const color = resolvedTheme === "light" ? COLOR_LIGHT : COLOR_DARK;

  return (
    <div className="pointer-events-none fixed inset-0 opacity-50 dark:opacity-60">
      {/* dpr/fps bajos: shader caro a pantalla completa en GPU integrada (ver login). */}
      <Threads color={color} amplitude={0.9} distance={0.4} enableMouseInteraction={false} dpr={0.6} fps={30} />
    </div>
  );
}

export default memo(InteriorBackground);
