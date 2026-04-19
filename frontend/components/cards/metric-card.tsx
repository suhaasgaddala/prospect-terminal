import { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function MetricCard({
  label,
  value,
  detail,
  icon,
  tone = "neutral"
}: {
  label: string;
  value: string;
  detail: string;
  icon?: ReactNode;
  tone?: "neutral" | "bull" | "bear" | "warm";
}) {
  const toneClass =
    tone === "bull"
      ? "text-bull"
      : tone === "bear"
      ? "text-bear"
      : tone === "warm"
      ? "text-accentWarm"
      : "text-white";
  return (
    <div className="flex items-start justify-between gap-4 border border-rule/70 bg-surface/90 px-5 py-4">
      <div className="min-w-0">
        <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-muted-foreground">
          {label}
        </p>
        <p className={cn("mt-3 font-mono text-3xl tabular-nums leading-none", toneClass)}>{value}</p>
        <p className="mt-2 text-xs leading-snug text-muted-foreground">{detail}</p>
      </div>
      {icon && (
        <div className="rounded-sm border border-rule/70 bg-surface2/60 p-2 text-muted-foreground">
          {icon}
        </div>
      )}
    </div>
  );
}
