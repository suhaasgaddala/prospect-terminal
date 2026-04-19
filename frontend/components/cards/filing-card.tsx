import { ArrowUpRight } from "lucide-react";

import { Panel } from "@/components/ui/panel";
import { Badge } from "@/components/ui/badge";
import { FilingSummary } from "@/types/generated-api";

export function FilingCard({ filing }: { filing: FilingSummary }) {
  const tone =
    filing.signal_score >= 60 ? "bullish" : filing.signal_score <= 45 ? "bearish" : "neutral";

  return (
    <Panel
      eyebrow="SEC Filing"
      title={filing.form_type}
      actions={
        <div className="flex items-center gap-2">
          <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-muted-foreground">
            Signal
          </span>
          <Badge tone={tone}>{filing.signal_score.toFixed(0)}</Badge>
        </div>
      }
      density="compact"
    >
      <p className="text-sm leading-relaxed text-foreground/90">{filing.summary}</p>
      <div className="mt-5 grid gap-px overflow-hidden border border-rule/60 bg-rule/60 md:grid-cols-2">
        <div className="bg-surface/90 p-4">
          <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.22em] text-bull">
            Highlights
          </p>
          <ul className="space-y-1.5 text-sm leading-snug text-foreground/85">
            {filing.highlights.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="bg-surface/90 p-4">
          <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.22em] text-bear">
            Risks
          </p>
          <ul className="space-y-1.5 text-sm leading-snug text-foreground/85">
            {filing.risks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
      <a
        href={filing.filing_url}
        target="_blank"
        rel="noreferrer"
        className="mt-4 inline-flex items-center gap-1 font-mono text-[11px] uppercase tracking-[0.22em] text-accentWarm hover:text-accentWarm/80"
      >
        Open filing
        <ArrowUpRight className="h-3 w-3" />
      </a>
    </Panel>
  );
}
