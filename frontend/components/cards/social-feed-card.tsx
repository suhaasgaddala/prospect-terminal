import { Panel } from "@/components/ui/panel";
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

  const summary = (
    <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.2em]">
      <span className="text-bull">{sentimentCounts.bullish} bull</span>
      <span className="text-muted-foreground">{sentimentCounts.neutral} neut</span>
      <span className="text-bear">{sentimentCounts.bearish} bear</span>
    </div>
  );

  return (
    <Panel
      eyebrow="Social Pulse · Preview"
      title="X + Reddit chatter"
      actions={summary}
      density="compact"
    >
      <p className="mb-4 text-xs leading-snug text-muted-foreground">
        Context only. Not included in Prospect Score or backtests.
      </p>
      {items.length === 0 ? (
        <div className="border border-dashed border-rule/60 px-4 py-6 text-center text-xs text-muted-foreground">
          No recent social posts for this ticker.
        </div>
      ) : (
        <ul className="divide-y divide-rule/60">
          {items.map((item) => {
            const isPreviewOnlyLink = item.url.includes("example.com");
            const content = (
              <>
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Badge tone={item.sentiment.label}>{item.source}</Badge>
                    <span className="font-mono text-[11px] text-muted-foreground">
                      @{item.author}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {isPreviewOnlyLink ? <Badge tone="neutral">preview</Badge> : null}
                    <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                      {formatDate(item.created_at)}
                    </span>
                  </div>
                </div>
                <p className="mt-2 text-sm leading-snug text-foreground/90">{item.text}</p>
                <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                  Engagement {item.engagement.score}
                </p>
              </>
            );

            if (isPreviewOnlyLink) {
              return (
                <li key={item.url} className="px-1 py-3">
                  {content}
                </li>
              );
            }

            return (
              <li key={item.url}>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="block px-1 py-3 transition-colors hover:bg-surface2/40"
                >
                  {content}
                </a>
              </li>
            );
          })}
        </ul>
      )}
    </Panel>
  );
}
