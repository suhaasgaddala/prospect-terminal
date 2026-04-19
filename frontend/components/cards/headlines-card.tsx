import { Panel } from "@/components/ui/panel";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/formatters";
import { ContentItem } from "@/types/generated-api";

export function HeadlinesCard({ items }: { items: ContentItem[] }) {
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
    <Panel eyebrow="Headlines" title="News flow" actions={summary} density="compact">
      {items.length === 0 ? (
        <div className="border border-dashed border-rule/60 px-4 py-6 text-center text-xs text-muted-foreground">
          No recent headlines for this ticker.
        </div>
      ) : (
        <ul className="divide-y divide-rule/60">
          {items.map((item) => (
            <li key={item.url}>
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="block px-1 py-3 transition-colors hover:bg-surface2/40"
              >
                <div className="flex items-center justify-between gap-3">
                  <Badge tone={item.sentiment.label}>{item.author}</Badge>
                  <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted-foreground">
                    {formatDate(item.created_at)}
                  </span>
                </div>
                <p className="mt-2 text-sm font-medium leading-snug text-white">
                  {item.title || item.text}
                </p>
                {item.title && item.text ? (
                  <p className="mt-1 line-clamp-2 text-xs leading-snug text-muted-foreground">
                    {item.text}
                  </p>
                ) : null}
              </a>
            </li>
          ))}
        </ul>
      )}
    </Panel>
  );
}
