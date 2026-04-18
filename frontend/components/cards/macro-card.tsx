import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MacroSnapshot } from "@/types/generated-api";

export function MacroCard({ snapshot }: { snapshot: MacroSnapshot }) {
  const tone =
    snapshot.score >= 60 ? "bullish" : snapshot.score <= 45 ? "bearish" : "neutral";

  return (
    <Card className="h-full">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            Macro Snapshot
          </p>
          <h3 className="mt-3 text-3xl font-semibold text-white">
            {snapshot.score.toFixed(0)}
            <span className="ml-2 text-base text-muted-foreground">/ 100</span>
          </h3>
          <p className="mt-2 max-w-xl text-sm text-muted-foreground">{snapshot.summary}</p>
        </div>
        <Badge tone={tone}>{snapshot.regime}</Badge>
      </div>
      <div className="mt-6 grid gap-3 md:grid-cols-2">
        {snapshot.factors.map((factor) => (
          <div key={factor.name} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="font-medium text-white">{factor.name}</p>
              <span className="font-mono text-sm text-cyan-100">{factor.delta.toFixed(2)}</span>
            </div>
            <p className="mt-3 text-2xl font-semibold text-white">{factor.value.toFixed(2)}</p>
            <p className="mt-2 text-sm text-muted-foreground">{factor.summary}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
