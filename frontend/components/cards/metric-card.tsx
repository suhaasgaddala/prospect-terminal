import { ReactNode } from "react";

import { Card } from "@/components/ui/card";

export function MetricCard({
  label,
  value,
  detail,
  icon
}: {
  label: string;
  value: string;
  detail: string;
  icon?: ReactNode;
}) {
  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/40 to-transparent" />
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            {label}
          </p>
          <p className="mt-4 text-3xl font-semibold text-white">{value}</p>
          <p className="mt-2 text-sm text-muted-foreground">{detail}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-cyan-200">
          {icon}
        </div>
      </div>
    </Card>
  );
}
