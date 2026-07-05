import type {
  ButtonHTMLAttributes,
  InputHTMLAttributes,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from "react";

// Primitivas de formulario del tema grafito: mismas superficies translúcidas que GlassCard,
// foco monocromo (ring del foreground), sin color.

const FIELD =
  "rounded-lg border bg-black/[0.03] border-black/10 px-3 py-2 text-sm outline-none transition-colors " +
  "placeholder:text-muted-foreground focus:border-foreground/40 " +
  "dark:bg-white/[0.06] dark:border-white/10 dark:focus:border-white/40";

export function Input({ className = "", ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`${FIELD} ${className}`} {...props} />;
}

export function Select({ className = "", ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={`${FIELD} bg-background dark:bg-background ${className}`} {...props} />;
}

export function Textarea({ className = "", ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={`${FIELD} ${className}`} {...props} />;
}

const BUTTON: Record<"primary" | "ghost" | "danger", string> = {
  primary:
    "rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground transition-opacity hover:opacity-85 disabled:opacity-40",
  ghost:
    "rounded-lg border border-black/10 px-4 py-2 text-sm font-medium transition-colors hover:bg-black/[0.04] disabled:opacity-40 dark:border-white/10 dark:hover:bg-white/[0.06]",
  danger:
    "rounded-lg border border-black/10 px-4 py-2 text-sm font-medium text-red-600 transition-colors hover:bg-red-500/10 disabled:opacity-40 dark:border-white/10 dark:text-red-400",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: keyof typeof BUTTON }) {
  return <button className={`${BUTTON[variant]} ${className}`} {...props} />;
}
