import { ArrowRight, BrainCircuit, CandlestickChart, Globe, Radar } from "lucide-react";
import Link from "next/link";

import { LeaderboardCard } from "@/components/cards/leaderboard-card";
import { MacroCard } from "@/components/cards/macro-card";
import { MetricCard } from "@/components/cards/metric-card";
import { AppShell } from "@/components/layout/app-shell";
import { TickerSearch } from "@/components/layout/ticker-search";
import { api } from "@/services/api";
import { formatPercent } from "@/lib/formatters";

/** Always SSR with live API data — avoids flaky static/dynamic toggling in dev. */
export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [leaderboard, macro] = await Promise.all([api.getLeaderboard(), api.getMacro()]);
  const topBull = leaderboard.bullish[0];
  const topBear = leaderboard.bearish[0];

  return (
    <AppShell currentPath="/">
      <section className="grid gap-6 lg:grid-cols-[1.35fr_0.95fr]">
        <div className="rounded-[36px] border border-white/10 bg-[linear-gradient(135deg,rgba(6,10,12,0.94),rgba(8,14,16,0.78))] p-8 shadow-panel">
          <p className="font-mono text-xs uppercase tracking-[0.32em] text-cyan-200">
            PROSPECT TERMINAL
          </p>
          <h1 className="mt-5 max-w-3xl text-5xl font-semibold leading-[1.02] text-white md:text-6xl">
            Spot conviction.
            <br />
            Test the edge.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-muted-foreground">
            An explainable stock terminal built on live prices, filings, news, macro, and backtests.
          </p>
          <div className="mt-8 max-w-xl">
            <TickerSearch />
          </div>
          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <MetricCard
              label="Top Bull"
              value={topBull?.ticker ?? "--"}
              detail={topBull ? `${topBull.overall_score.toFixed(0)} score` : "No signal"}
              icon={<Radar className="h-5 w-5" />}
            />
            <MetricCard
              label="Top Bear"
              value={topBear?.ticker ?? "--"}
              detail={topBear ? `${topBear.overall_score.toFixed(0)} score` : "No signal"}
              icon={<BrainCircuit className="h-5 w-5" />}
            />
            <MetricCard
              label="Macro Regime"
              value={macro.snapshot.regime}
              detail={`${macro.snapshot.score.toFixed(0)}/100 context score`}
              icon={<Globe className="h-5 w-5" />}
            />
          </div>
        </div>
        <MacroCard snapshot={macro.snapshot} />
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-2">
        <LeaderboardCard
          title="Top Bullish Stocks"
          subtitle="Highest explainable scores across the tracked demo universe."
          items={leaderboard.bullish}
          tone="bullish"
        />
        <LeaderboardCard
          title="Top Bearish Stocks"
          subtitle="Lowest scores where social, filing, or macro pressure is dominating."
          items={leaderboard.bearish}
          tone="bearish"
        />
      </section>

      <section className="mt-6 rounded-[32px] border border-white/10 bg-white/[0.03] p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
              Quick routes
            </p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Jump from signal discovery to thesis and backtest
            </h2>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href={`/stocks/${topBull?.ticker ?? "NVDA"}`}
              className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-500/10 px-4 py-2 text-sm text-cyan-100 transition hover:text-white"
            >
              Open signal page <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href={`/backtest?ticker=${topBull?.ticker ?? "NVDA"}`}
              className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-500/10 px-4 py-2 text-sm text-amber-100 transition hover:text-white"
            >
              Run backtest <CandlestickChart className="h-4 w-4" />
            </Link>
          </div>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {macro.snapshot.factors.slice(0, 3).map((factor) => (
            <div key={factor.name} className="rounded-[24px] border border-white/8 bg-black/20 p-4">
              <p className="font-mono text-xs uppercase tracking-[0.24em] text-muted-foreground">
                {factor.name}
              </p>
              <p className="mt-3 text-3xl font-semibold text-white">{factor.value.toFixed(2)}</p>
              <p className="mt-2 text-sm text-muted-foreground">
                {factor.summary} {formatPercent(factor.delta)}
              </p>
            </div>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
