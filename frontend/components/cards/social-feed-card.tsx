import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/formatters";
import { ContentItem } from "@/types/generated-api";

export function SocialFeedCard({ items }: { items: ContentItem[] }) {
  const sentimentCounts = items.reduce(
    (acc, item) => {
      acc[item.sentiment.label] += 1;
      return acc;
    },
    { bullish: 0, neutral: 0, bearish: 0 }
  );

  return (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            Social Pulse
          </p>
          <h3 className="mt-2 text-xl font-semibold text-white">X + Reddit sentiment</h3>
          <p className="mt-2 text-xs text-muted-foreground">
            {sentimentCounts.bullish} bullish, {sentimentCounts.neutral} neutral,{" "}
            {sentimentCounts.bearish} bearish
          </p>
        </div>
      </div>
      <div className="mt-5 space-y-3">
        {items.length === 0 ? (
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm text-muted-foreground">
            No recent social posts available for this ticker.
          </div>
        ) : null}
        {items.map((item) => (
          <a
            key={item.url}
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className="block rounded-2xl border border-white/8 bg-white/[0.03] p-4 transition hover:border-cyan-300/20"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Badge tone={item.sentiment.label}>{item.source}</Badge>
                <span className="text-xs text-muted-foreground">@{item.author}</span>
              </div>
              <span className="text-xs text-muted-foreground">{formatDate(item.created_at)}</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-100">{item.text}</p>
            <p className="mt-3 font-mono text-xs text-muted-foreground">
              engagement {item.engagement.score}
            </p>
          </a>
        ))}
      </div>
    </Card>
  );
}
