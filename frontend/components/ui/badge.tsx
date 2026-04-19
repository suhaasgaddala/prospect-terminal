import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type Tone = "bullish" | "neutral" | "bearish";
type Shape = "pill" | "square";

export function Badge({
  className,
  tone = "neutral",
  shape = "square",
  ...props
}: HTMLAttributes<HTMLDivElement> & { tone?: Tone; shape?: Shape }) {
  return (
    <div
      className={cn(
        "inline-flex items-center border px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.22em]",
        shape === "pill" ? "rounded-full px-2.5 py-1" : "rounded-sm",
        tone === "bullish" && "border-bull/40 bg-bull/10 text-bull",
        tone === "bearish" && "border-bear/40 bg-bear/10 text-bear",
        tone === "neutral" && "border-rule/70 bg-surface2/60 text-muted-foreground",
        className
      )}
      {...props}
    />
  );
}
