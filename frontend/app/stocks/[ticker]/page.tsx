import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { FilingCard } from "@/components/cards/filing-card";
import { HeadlinesCard } from "@/components/cards/headlines-card";
import { SocialFeedCard } from "@/components/cards/social-feed-card";
import { SourceBreakdownCard } from "@/components/cards/source-breakdown-card";
import { ThesisCard } from "@/components/cards/thesis-card";
import { PriceVsScoreChart } from "@/components/charts/price-vs-score-chart";
import { ScoreHistoryChart } from "@/components/charts/score-history-chart";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import { Stat } from "@/components/ui/stat";
import { formatCurrency, formatPercent, scoreTone } from "@/lib/formatters";
import { ApiError } from "@/lib/api-client";
import { api } from "@/services/api";

export const dynamic = "force-dynamic";

export default async function StockPage({
  params
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = await params;

  try {
    const [stock, history] = await Promise.all([
      api.getStock(ticker.toUpperCase()),
      api.getScoreHistory(ticker.toUpperCase(), "3M")
    ]);

    const change = stock.quote.daily_change_percent;
    const changeTone = change > 0 ? "bull" : change < 0 ? "bear" : "neutral";
    const scoreTonality: "bull" | "bear" | "warm" =
      stock.score >= 65 ? "bull" : stock.score <= 40 ? "bear" : "warm";
    const rating = stock.thesis.rating;
    const ratingTone: "bull" | "bear" | "neutral" =
      rating === "bullish" ? "bull" : rating === "bearish" ? "bear" : "neutral";
    const ratingLabel = rating.toUpperCase();
    const ratingColorClass =
      ratingTone === "bull"
        ? "text-bull border-bull/40 bg-bull/10"
        : ratingTone === "bear"
        ? "text-bear border-bear/40 bg-bear/10"
        : "text-muted-foreground border-rule/70 bg-surface2/60";
    const ratingBarClass =
      ratingTone === "bull" ? "bg-bull" : ratingTone === "bear" ? "bg-bear" : "bg-muted-foreground/40";
    const scoreColorClass =
      scoreTonality === "bull" ? "text-bull" : scoreTonality === "bear" ? "text-bear" : "text-accentWarm";

    return (
      <AppShell>
        {/* Dossier header */}
        <section className="border-b border-rule/60 pb-6">
          <div className="flex flex-wrap items-end justify-between gap-6">
            <div className="min-w-0">
              <p className="font-mono text-[11px] uppercase tracking-[0.32em] text-accentWarm">
                Dossier · {stock.quote.ticker}
              </p>
              <h1 className="mt-2 truncate text-3xl font-semibold tracking-tight text-white md:text-4xl">
                {stock.quote.company_name}
              </h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {stock.quote.is_stale ? <Badge tone="neutral">Cached quote</Badge> : null}
              <Link
                href={`/backtest?ticker=${stock.quote.ticker}&strategy=threshold_cross`}
                className="inline-flex h-9 items-center gap-2 rounded-sm border border-accentWarm/50 bg-accentWarm/10 px-4 font-mono text-[11px] uppercase tracking-[0.22em] text-accentWarm hover:bg-accentWarm/20"
              >
                Backtest this ticker <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>

          {/* Quote strip */}
          <div className="mt-6 grid gap-px overflow-hidden border border-rule/70 bg-rule/60 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-surface/90 p-5">
              <Stat
                label="Last"
                value={formatCurrency(stock.quote.price)}
                size="xl"
                tone="neutral"
              />
            </div>
            <div className="bg-surface/90 p-5">
              <Stat
                label="Change"
                value={formatPercent(change)}
                size="xl"
                tone={changeTone}
              />
            </div>
            <div className="relative bg-surface/90 p-5">
              <span className={`absolute inset-y-0 left-0 w-[3px] ${ratingBarClass}`} aria-hidden />
              <div className="flex items-center justify-between gap-3">
                <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-muted-foreground">
                  Prospect Score
                </span>
                <span
                  className={`inline-flex items-center gap-1.5 border px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.26em] ${ratingColorClass}`}
                >
                  <span className={`h-1 w-1 rounded-full ${ratingBarClass}`} aria-hidden />
                  {ratingLabel}
                </span>
              </div>
              <div className="mt-2 flex items-baseline gap-2">
                <span className={`font-mono text-4xl tabular-nums leading-none tracking-tight ${scoreColorClass}`}>
                  {stock.score.toFixed(0)}
                </span>
                <span className="font-mono text-[11px] tabular-nums text-muted-foreground">
                  / 100
                </span>
              </div>
            </div>
            <div className="bg-surface/90 p-5">
              <Stat
                label="Macro"
                value={stock.macro.score.toFixed(0)}
                size="xl"
                tone="neutral"
                hint={stock.macro.regime}
              />
            </div>
          </div>
          <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
            Score = weighted blend of News · Filings · Macro. Social pulse is preview-only.
          </p>
        </section>

        {/* Thesis + score breakdown + macro */}
        <section className="mt-8 grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
          <ThesisCard thesis={stock.thesis} />
          <div className="space-y-6">
            <SourceBreakdownCard components={stock.components} />
            <Panel eyebrow="Macro Context" title={stock.macro.regime} density="compact">
              <div className="flex items-baseline gap-4">
                <span className={`font-mono text-4xl tabular-nums ${scoreTone(stock.macro.score)}`}>
                  {stock.macro.score.toFixed(0)}
                </span>
                <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
                  Composite / 100
                </span>
              </div>
              <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
                {stock.macro.summary}
              </p>
            </Panel>
          </div>
        </section>

        {/* Charts */}
        <section className="mt-8 grid gap-6 xl:grid-cols-2">
          <Panel eyebrow="Score · 3M" title="Score history" density="compact">
            <ScoreHistoryChart points={history.points} />
          </Panel>
          <Panel eyebrow="Price vs Score" title="Conviction overlay" density="compact">
            <PriceVsScoreChart points={history.points} />
          </Panel>
        </section>

        {/* Headlines + Social + Filing */}
        <section className="mt-8 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <HeadlinesCard items={stock.headlines} />
            <SocialFeedCard items={stock.social_items} />
          </div>
          <FilingCard filing={stock.filing} />
        </section>
      </AppShell>
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
}
