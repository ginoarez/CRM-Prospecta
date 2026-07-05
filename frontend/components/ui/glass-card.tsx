import type { HTMLAttributes } from "react";
import { NoiseTexture } from "@/components/ui/noise-texture";

export function GlassCard({ className = "", children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`relative overflow-hidden rounded-xl border backdrop-blur-md bg-black/[0.03] border-black/10 dark:bg-white/[0.06] dark:border-white/10 ${className}`}
      {...props}
    >
      {/* absolute → excluded from flex flow; paints behind sibling content */}
      <NoiseTexture className="opacity-[0.1] dark:opacity-20" />
      {children}
    </div>
  );
}
