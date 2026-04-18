import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Badge({
  className,
  tone = "neutral",
  ...props
}: HTMLAttributes<HTMLDivElement> & { tone?: "bullish" | "neutral" | "bearish" }) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.24em]",
        tone === "bullish" &&
          "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
        tone === "bearish" && "border-rose-500/30 bg-rose-500/10 text-rose-300",
        tone === "neutral" &&
          "border-cyan-500/20 bg-cyan-500/10 text-cyan-200",
        className
      )}
      {...props}
    />
  );
}
