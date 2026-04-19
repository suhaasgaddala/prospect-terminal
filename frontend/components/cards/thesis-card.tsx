import { ArrowUpRight, ArrowDownRight } from "lucide-react";

import { Panel } from "@/components/ui/panel";
import { Badge } from "@/components/ui/badge";
import { Thesis } from "@/types/generated-api";

export function ThesisCard({ thesis }: { thesis: Thesis }) {
  return (
    <Panel
      eyebrow="Thesis"
      title="Conviction stack"
      actions={<Badge tone={thesis.rating}>{thesis.rating}</Badge>}
    >
      <p className="text-sm leading-relaxed text-foreground/90">{thesis.summary}</p>
      <div className="mt-5 grid gap-px overflow-hidden rounded-sm border border-rule/60 bg-rule/60 lg:grid-cols-2">
        <div className="bg-surface/90 p-5">
          <div className="mb-3 flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-bull">
              Catalysts
            </span>
            <span className="font-mono text-[10px] tabular-nums text-muted-foreground">
              {String(thesis.catalysts.length).padStart(2, "0")}
            </span>
          </div>
          <ul className="space-y-2.5">
            {thesis.catalysts.map((item) => (
              <li key={item} className="flex gap-2.5 text-sm leading-snug text-foreground/85">
                <ArrowUpRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-bull" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-surface/90 p-5">
          <div className="mb-3 flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-bear">
              Risks
            </span>
            <span className="font-mono text-[10px] tabular-nums text-muted-foreground">
              {String(thesis.risks.length).padStart(2, "0")}
            </span>
          </div>
          <ul className="space-y-2.5">
            {thesis.risks.map((item) => (
              <li key={item} className="flex gap-2.5 text-sm leading-snug text-foreground/85">
                <ArrowDownRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-bear" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Panel>
  );
}
