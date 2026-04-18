import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FilingSummary } from "@/types/generated-api";

export function FilingCard({ filing }: { filing: FilingSummary }) {
  const tone =
    filing.signal_score >= 60 ? "bullish" : filing.signal_score <= 45 ? "bearish" : "neutral";

  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            SEC Filing
          </p>
          <h3 className="mt-2 text-xl font-semibold text-white">{filing.form_type}</h3>
        </div>
        <Badge tone={tone}>{filing.signal_score.toFixed(0)}</Badge>
      </div>
      <p className="mt-4 text-sm leading-6 text-muted-foreground">{filing.summary}</p>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div>
          <p className="mb-2 text-sm font-medium text-white">Highlights</p>
          <div className="space-y-2">
            {filing.highlights.map((item) => (
              <p key={item} className="text-sm text-muted-foreground">
                {item}
              </p>
            ))}
          </div>
        </div>
        <div>
          <p className="mb-2 text-sm font-medium text-white">Risks</p>
          <div className="space-y-2">
            {filing.risks.map((item) => (
              <p key={item} className="text-sm text-muted-foreground">
                {item}
              </p>
            ))}
          </div>
        </div>
      </div>
      <a
        href={filing.filing_url}
        target="_blank"
        rel="noreferrer"
        className="mt-5 inline-flex text-sm text-cyan-200 hover:text-white"
      >
        Open filing
      </a>
    </Card>
  );
}
