import { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

type PanelProps = HTMLAttributes<HTMLDivElement> & {
  title?: ReactNode;
  eyebrow?: ReactNode;
  actions?: ReactNode;
  density?: "default" | "compact";
};

export function Panel({
  className,
  title,
  eyebrow,
  actions,
  density = "default",
  children,
  ...props
}: PanelProps) {
  const padding = density === "compact" ? "p-4" : "p-5";
  return (
    <div
      className={cn(
        "rounded-md border border-rule/70 bg-surface/90 text-foreground",
        className
      )}
      {...props}
    >
      {(title || eyebrow || actions) && (
        <div className="flex items-center justify-between gap-3 border-b border-rule/60 px-5 py-3">
          <div className="min-w-0">
            {eyebrow && (
              <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-muted-foreground">
                {eyebrow}
              </p>
            )}
            {title && (
              <h3 className="mt-0.5 truncate text-sm font-semibold tracking-tight text-white">
                {title}
              </h3>
            )}
          </div>
          {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className={padding}>{children}</div>
    </div>
  );
}
