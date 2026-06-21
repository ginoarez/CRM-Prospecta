"use client";
import { memo } from "react";
import dynamic from "next/dynamic";

const FaultyTerminal = dynamic(() => import("@/components/ui/FaultyTerminal"), { ssr: false });

// Referencias estables a nivel de módulo: evitan que el efecto del WebGL se reinicie en cada render.
const GRID_MUL: [number, number] = [2, 1];

// Fondo del login aislado y memoizado: no se re-renderiza cuando el formulario cambia de estado,
// así el contexto WebGL no se recrea al escribir. dpr bajo para rendir fluido en GPU integrada.
function LoginBackground() {
  return (
    <div className="absolute inset-0">
      <FaultyTerminal
        scale={2.5}
        gridMul={GRID_MUL}
        digitSize={0.9}
        timeScale={1.2}
        pause={false}
        scanlineIntensity={0.6}
        glitchAmount={1}
        flickerAmount={1}
        noiseAmp={1}
        chromaticAberration={0}
        dither={0}
        curvature={0}
        tint="#ffffff"
        mouseReact={true}
        mouseStrength={0.4}
        pageLoadAnimation={false}
        brightness={0.5}
        dpr={0.5}
      />
    </div>
  );
}

export default memo(LoginBackground);
