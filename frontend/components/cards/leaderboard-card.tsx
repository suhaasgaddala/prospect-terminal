import Link from "next/link";

import { Panel } from "@/components/ui/panel";
import { Badge } from "@/components/ui/badge";
import { formatCurrency, formatPercent, scoreTone } from "@/lib/formatters";
import { LeaderboardEntry } from "@/types/generated-api";

export function LeaderboardCard({
  title,
  subtitle,
  items,
  tone
}: {
  title: string;
  subtitle: string;
  items: LeaderboardEntry[];
  tone: "bullish" | "bearish";
}) {
  const eyebrow = tone === "bullish" ? "Top Conviction" : "Weakest Setup";
  return (
    <Panel
      eyebrow={eyebrow}
      title={title}
      actions={<Badge tone={tone}>{tone === "bullish" ? "Bull" : "Bear"}</Badge>}
      density="compact"
      className="h-full"
    >
      <p className="mb-3 text-xs text-muted-foreground">{subtitle}</p>
      {items.length === 0 ? (
        <div className="rounded-2xl border border-rule/70 bg-surface2/30 px-4 py-5">
          <p className="text-sm font-medium text-foreground">
            {tone === "bearish"
              ? "No qualified bearish setups in the tracked universe today."
              : "No qualified bullish setups in the tracked universe today."}
          </p>
          <p className="mt-2 text-xs leading-6 text-muted-foreground">
            {tone === "bearish"
              ? "Market breadth is strong right now, so bearish names only appear when both score and price action weaken."
              : "Bullish names appear only when score and price action align in the tracked universe."}
          </p>
        </div>
      ) : null}
      <ul className="divide-y divide-rule/60">
        {items.map((item, index) => {
          const change = item.daily_change_percent;
          const changeTone =
            change > 0 ? "text-bull" : change < 0 ? "text-bear" : "text-muted-foreground";
          return (
            <li key={item.ticker}>
              <Link
                href={`/stocks/${item.ticker}`}
                className="grid grid-cols-[28px_minmax(0,1fr)_auto_auto] items-center gap-4 px-1 py-3 transition-colors hover:bg-surface2/40"
              >
                <span className="font-mono text-[11px] tabular-nums text-muted-foreground">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <div className="min-w-0">
                  <div className="flex items-baseline gap-2">
                    <span className="font-mono text-base font-semibold tracking-wide text-white">
                      {item.ticker}
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      {item.company_name}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-xs tabular-nums text-foreground">
                    {formatCurrency(item.price)}
                  </div>
                  <div className={`font-mono text-[11px] tabular-nums ${changeTone}`}>
                    {formatPercent(change)}
                  </div>
                </div>
                <div className={`font-mono text-xl tabular-nums ${scoreTone(item.overall_score)}`}>
                  {item.overall_score.toFixed(0)}
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
    </Panel>
  );
}
