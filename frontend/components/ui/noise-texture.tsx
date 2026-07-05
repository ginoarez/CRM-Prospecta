"use client";
import { useId } from "react";
import type { ComponentProps } from "react";

export interface NoiseTextureProps extends ComponentProps<"svg"> {
  /** baseFrequency for feTurbulence; higher = finer grain. */
  frequency?: number;
  /** numOctaves for feTurbulence; more = more detail. */
  octaves?: number;
  /** linear slope per channel after desaturation; adjusts contrast. */
  slope?: number;
  /** opacity of the noise rect. */
  noiseOpacity?: number;
}

/**
 * Monochrome SVG fractal-noise overlay (Magic UI). Desaturated (saturate 0) so
 * it never introduces color. Render inside a `relative overflow-hidden` parent;
 * it positions itself absolutely behind sibling content.
 */
export function NoiseTexture({
  className = "",
  frequency = 0.6,
  octaves = 4,
  slope = 0.12,
  noiseOpacity = 0.5,
  ...props
}: NoiseTextureProps) {
  const filterId = `noise-${useId().replace(/:/g, "")}`;

  return (
    <svg
      aria-hidden="true"
      className={`pointer-events-none absolute inset-0 size-full select-none ${className}`}
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <filter id={filterId}>
        <feTurbulence
          type="fractalNoise"
          baseFrequency={frequency}
          numOctaves={octaves}
          stitchTiles="stitch"
        />
        <feColorMatrix type="saturate" values="0" />
        <feComponentTransfer>
          <feFuncR type="linear" slope={slope} />
          <feFuncG type="linear" slope={slope} />
          <feFuncB type="linear" slope={slope} />
        </feComponentTransfer>
      </filter>
      <rect width="100%" height="100%" filter={`url(#${filterId})`} opacity={noiseOpacity} />
    </svg>
  );
}
