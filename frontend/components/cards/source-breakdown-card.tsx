import { Panel } from "@/components/ui/panel";
import { ScoreComponents } from "@/types/generated-api";

const labels: Array<keyof ScoreComponents> = ["news", "filings", "macro"];

function barTone(value: number) {
  if (value >= 65) return "bg-bull";
  if (value <= 40) return "bg-bear";
  return "bg-accentWarm";
}

export function SourceBreakdownCard({ components }: { components: ScoreComponents }) {
  return (
    <Panel eyebrow="Score Inputs" title="Source breakdown" density="compact">
      <p className="mb-4 text-xs leading-snug text-muted-foreground">
        Each input runs 0–100 and rolls into the Prospect Score. Social Pulse is preview-only context.
      </p>
      <div className="space-y-4">
        {labels.map((label) => {
          const value = components[label];
          const safeValue = Math.max(0, Math.min(100, value));
          return (
            <div key={label}>
              <div className="mb-1.5 flex items-center justify-between gap-3">
                <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-muted-foreground">
                  {label}
                </span>
                <span className="font-mono text-sm tabular-nums text-foreground">
                  {value.toFixed(0)}
                </span>
              </div>
              <div className="h-1.5 w-full bg-surface2/80">
                <div
                  className={`h-1.5 ${barTone(value)}`}
                  style={{ width: `${safeValue}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </Panel>
  );
}
