import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/formatters";
import { ContentItem } from "@/types/generated-api";

export function HeadlinesCard({ items }: { items: ContentItem[] }) {
  return (
    <Card>
      <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
        Latest Headlines
      </p>
      <div className="mt-5 space-y-3">
        {items.map((item) => (
          <a
            key={item.url}
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className="block rounded-2xl border border-white/8 bg-white/[0.03] p-4 transition hover:border-cyan-300/20"
          >
            <div className="flex items-center justify-between gap-3">
              <Badge tone={item.sentiment.label}>{item.author}</Badge>
              <span className="text-xs text-muted-foreground">{formatDate(item.created_at)}</span>
            </div>
            <p className="mt-3 text-base font-medium text-white">
              {item.title || item.text}
            </p>
            <p className="mt-2 text-sm text-muted-foreground">{item.text}</p>
          </a>
        ))}
      </div>
    </Card>
  );
}
