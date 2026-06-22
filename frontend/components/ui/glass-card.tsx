import type { HTMLAttributes } from "react";

export function GlassCard({ className = "", children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-xl border backdrop-blur-md bg-black/[0.03] border-black/10 dark:bg-white/[0.06] dark:border-white/10 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
