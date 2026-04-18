import { notFound } from "next/navigation";
import Link from "next/link";

import { FilingCard } from "@/components/cards/filing-card";
import { HeadlinesCard } from "@/components/cards/headlines-card";
import { SocialFeedCard } from "@/components/cards/social-feed-card";
import { SourceBreakdownCard } from "@/components/cards/source-breakdown-card";
import { ThesisCard } from "@/components/cards/thesis-card";
import { PriceVsScoreChart } from "@/components/charts/price-vs-score-chart";
import { ScoreHistoryChart } from "@/components/charts/score-history-chart";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatCurrency, formatPercent, scoreTone } from "@/lib/formatters";
import { ApiError } from "@/lib/api-client";
import { api } from "@/services/api";

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

    return (
      <AppShell>
        <section className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
          <div className="rounded-[32px] border border-white/10 bg-white/[0.03] p-6 shadow-panel">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.32em] text-cyan-200">
                  {stock.quote.ticker}
                </p>
                <h1 className="mt-3 text-5xl font-semibold text-white">
                  {stock.quote.company_name}
                </h1>
                <div className="mt-4 flex flex-wrap items-center gap-4">
                  <span className="text-3xl font-semibold text-white">
                    {formatCurrency(stock.quote.price)}
                  </span>
                  <span
                    className={`text-sm font-medium ${
                      stock.quote.daily_change_percent >= 0
                        ? "text-emerald-300"
                        : "text-rose-300"
                    }`}
                  >
                    {formatPercent(stock.quote.daily_change_percent)}
                  </span>
                  {stock.quote.is_stale ? <Badge tone="neutral">cached</Badge> : null}
                </div>
              </div>
              <div className="rounded-[28px] border border-cyan-500/20 bg-cyan-500/8 px-6 py-5 text-center">
                <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-cyan-100/80">
                  Overall Score
                </p>
                <p className={`mt-3 text-6xl font-semibold ${scoreTone(stock.score)}`}>
                  {stock.score.toFixed(0)}
                </p>
                <p className="mt-2 text-sm text-muted-foreground">Explainable score out of 100</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Weighted blend of News, X, Reddit, Filings, and Macro. 50 is neutral.
                </p>
              </div>
            </div>
            <div className="mt-6">
              <ThesisCard thesis={stock.thesis} />
            </div>
            <div className="mt-6">
              <Link
                href={`/backtest?ticker=${stock.quote.ticker}&strategy=threshold_cross`}
                className="inline-flex h-10 items-center justify-center rounded-full border border-cyan-500/30 bg-cyan-500/10 px-5 text-sm font-medium text-cyan-100 transition hover:border-cyan-400/40 hover:bg-cyan-500/20"
              >
                Backtest this ticker
              </Link>
            </div>
          </div>
          <div className="space-y-6">
            <SourceBreakdownCard components={stock.components} />
            <Card>
              <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
                Macro Context
              </p>
              <h3 className="mt-3 text-3xl font-semibold text-white">
                {stock.macro.score.toFixed(0)}
                <span className="ml-2 text-base text-muted-foreground">
                  {stock.macro.regime}
                </span>
              </h3>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">
                {stock.macro.summary}
              </p>
            </Card>
          </div>
        </section>

        <section className="mt-6 grid gap-6 xl:grid-cols-2">
          <ScoreHistoryChart points={history.points} />
          <PriceVsScoreChart points={history.points} />
        </section>

        <section className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
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
