import { Panel } from "@/components/ui/panel";
import { Badge } from "@/components/ui/badge";
import { Stat } from "@/components/ui/stat";
import { MacroSnapshot } from "@/types/generated-api";

export function MacroCard({ snapshot }: { snapshot: MacroSnapshot }) {
  const tone =
    snapshot.score >= 60 ? "bullish" : snapshot.score <= 45 ? "bearish" : "neutral";

  return (
    <Panel
      eyebrow="Macro Regime"
      title={snapshot.regime}
      actions={<Badge tone={tone}>{tone}</Badge>}
      density="compact"
      className="h-full"
    >
      <div className="flex flex-wrap items-end justify-between gap-6 border-b border-rule/60 pb-4">
        <Stat
          label="Composite"
          value={snapshot.score.toFixed(0)}
          hint="0–100 macro signal"
          size="xl"
          tone={tone === "bullish" ? "bull" : tone === "bearish" ? "bear" : "neutral"}
        />
        <p className="max-w-md text-xs leading-relaxed text-muted-foreground">{snapshot.summary}</p>
      </div>
      <div className="mt-4 grid gap-px overflow-hidden rounded-sm border border-rule/60 bg-rule/60 md:grid-cols-2">
        {snapshot.factors.map((factor) => {
          const deltaTone =
            factor.delta > 0 ? "text-bull" : factor.delta < 0 ? "text-bear" : "text-muted-foreground";
          return (
            <div key={factor.name} className="bg-surface/90 p-4">
              <div className="flex items-baseline justify-between gap-3">
                <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
                  {factor.name}
                </p>
                <span className={`font-mono text-[11px] tabular-nums ${deltaTone}`}>
                  {factor.delta > 0 ? "+" : ""}
                  {factor.delta.toFixed(2)}
                </span>
              </div>
              <p className="mt-2 font-mono text-2xl tabular-nums text-white">
                {factor.value.toFixed(2)}
              </p>
              <p className="mt-1 text-xs leading-snug text-muted-foreground">{factor.summary}</p>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}
