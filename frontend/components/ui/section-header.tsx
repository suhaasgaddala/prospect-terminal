import { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function SectionHeader({
  eyebrow,
  title,
  actions,
  className
}: {
  eyebrow?: ReactNode;
  title: ReactNode;
  actions?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex flex-wrap items-end justify-between gap-4 border-b border-rule/60 pb-4",
        className
      )}
    >
      <div>
        {eyebrow && (
          <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-muted-foreground">
            {eyebrow}
          </p>
        )}
        <h2 className="mt-1 text-2xl font-semibold tracking-tight text-white md:text-3xl">
          {title}
        </h2>
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}
