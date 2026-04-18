import Link from "next/link";

import { Card } from "@/components/ui/card";
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
  return (
    <Card className="h-full">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-semibold text-white">{title}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
        </div>
        <Badge tone={tone}>{tone}</Badge>
      </div>
      <div className="space-y-3">
        {items.map((item, index) => (
          <Link
            key={item.ticker}
            href={`/stocks/${item.ticker}`}
            className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/[0.03] px-4 py-3 transition hover:border-cyan-300/20 hover:bg-white/[0.05]"
          >
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.24em] text-muted-foreground">
                #{index + 1}
              </p>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-lg font-semibold text-white">{item.ticker}</span>
                <span className="text-sm text-muted-foreground">{item.company_name}</span>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-xl font-semibold ${scoreTone(item.overall_score)}`}>
                {item.overall_score.toFixed(0)}
              </div>
              <p className="text-sm text-muted-foreground">
                {formatCurrency(item.price)} · {formatPercent(item.daily_change_percent)}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </Card>
  );
}
