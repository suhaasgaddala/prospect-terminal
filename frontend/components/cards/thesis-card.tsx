import { AlertTriangle, ArrowUpRight, Sparkles } from "lucide-react";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Thesis } from "@/types/generated-api";

export function ThesisCard({ thesis }: { thesis: Thesis }) {
  return (
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            AI Thesis
          </p>
          <h2 className="mt-3 text-2xl font-semibold text-white">{thesis.summary}</h2>
        </div>
        <Badge tone={thesis.rating}>{thesis.rating}</Badge>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-[24px] border border-emerald-500/10 bg-emerald-500/5 p-5">
          <div className="mb-4 flex items-center gap-2 text-sm font-medium text-emerald-200">
            <Sparkles className="h-4 w-4" />
            Catalysts
          </div>
          <div className="space-y-3">
            {thesis.catalysts.map((item) => (
              <div key={item} className="flex gap-3 text-sm text-emerald-50/90">
                <ArrowUpRight className="mt-0.5 h-4 w-4 text-emerald-300" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-[24px] border border-rose-500/10 bg-rose-500/5 p-5">
          <div className="mb-4 flex items-center gap-2 text-sm font-medium text-rose-200">
            <AlertTriangle className="h-4 w-4" />
            Risks
          </div>
          <div className="space-y-3">
            {thesis.risks.map((item) => (
              <div key={item} className="flex gap-3 text-sm text-rose-50/90">
                <AlertTriangle className="mt-0.5 h-4 w-4 text-rose-300" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
