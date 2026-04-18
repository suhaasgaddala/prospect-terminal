import { Card } from "@/components/ui/card";
import { ScoreComponents } from "@/types/generated-api";

const labels: Array<keyof ScoreComponents> = ["news", "x", "reddit", "filings", "macro"];

export function SourceBreakdownCard({ components }: { components: ScoreComponents }) {
  return (
    <Card>
      <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
        Source Breakdown
      </p>
      <div className="mt-5 space-y-4">
        {labels.map((label) => {
          const value = components[label];
          return (
            <div key={label}>
              <div className="mb-2 flex items-center justify-between gap-3">
                <span className="text-sm capitalize text-white">{label}</span>
                <span className="font-mono text-sm text-cyan-100">{value.toFixed(0)}</span>
              </div>
              <div className="h-2 rounded-full bg-white/5">
                <div
                  className="h-2 rounded-full bg-[linear-gradient(90deg,rgba(78,192,214,0.8),rgba(240,190,74,0.7))]"
                  style={{ width: `${value}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
