import { ReactNode } from "react";

import { cn } from "@/lib/utils";

type Tone = "neutral" | "bull" | "bear" | "warm";

const toneClass: Record<Tone, string> = {
  neutral: "text-foreground",
  bull: "text-bull",
  bear: "text-bear",
  warm: "text-accentWarm"
};

const deltaToneClass: Record<Tone, string> = {
  neutral: "text-muted-foreground",
  bull: "text-bull",
  bear: "text-bear",
  warm: "text-accentWarm"
};

export function Stat({
  label,
  value,
  delta,
  tone = "neutral",
  size = "md",
  align = "left",
  hint
}: {
  label: ReactNode;
  value: ReactNode;
  delta?: ReactNode;
  tone?: Tone;
  size?: "sm" | "md" | "lg" | "xl";
  align?: "left" | "right";
  hint?: ReactNode;
}) {
  const valueSize =
    size === "xl"
      ? "text-4xl"
      : size === "lg"
      ? "text-3xl"
      : size === "sm"
      ? "text-lg"
      : "text-2xl";
  const alignClass = align === "right" ? "text-right items-end" : "text-left items-start";
  return (
    <div className={cn("flex flex-col gap-1", alignClass)}>
      <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-muted-foreground">
        {label}
      </span>
      <span
        className={cn(
          "font-mono tabular-nums leading-none tracking-tight",
          valueSize,
          toneClass[tone]
        )}
      >
        {value}
      </span>
      {(delta || hint) && (
        <span
          className={cn(
            "font-mono text-[11px] tabular-nums",
            delta ? deltaToneClass[tone] : "text-muted-foreground"
          )}
        >
          {delta ?? hint}
        </span>
      )}
    </div>
  );
}
