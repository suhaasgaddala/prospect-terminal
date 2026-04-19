import { ArrowRight, CandlestickChart } from "lucide-react";
import Link from "next/link";

import { LeaderboardCard } from "@/components/cards/leaderboard-card";
import { MacroCard } from "@/components/cards/macro-card";
import { AppShell } from "@/components/layout/app-shell";
import { TickerSearch } from "@/components/layout/ticker-search";
import { Stat } from "@/components/ui/stat";
import { SectionHeader } from "@/components/ui/section-header";
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
      {/* Hero */}
      <section className="border-b border-rule/60 pb-10">
        <div className="grid gap-10 lg:grid-cols-[1.4fr_0.9fr]">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.32em] text-accentWarm">
              Signal Terminal · Live
            </p>
            <h1 className="mt-4 max-w-3xl text-4xl font-semibold leading-[1.05] tracking-tight text-white md:text-6xl">
              Find the conviction.
              <br />
              <span className="text-foreground/70">Pressure-test the edge.</span>
            </h1>
            <p className="mt-5 max-w-xl text-sm leading-relaxed text-muted-foreground">
              A live signal terminal across price action, SEC filings, news, and macro context — paired with a backtest engine for every score.
            </p>
            <div className="mt-7 max-w-xl">
              <TickerSearch />
            </div>
          </div>

          <div className="grid gap-px self-end overflow-hidden border border-rule/70 bg-rule/60">
            <div className="bg-surface/90 p-5">
              <Stat
                label="Top Conviction"
                value={topBull?.ticker ?? "—"}
                tone="bull"
                size="lg"
                hint={topBull ? `Score ${topBull.overall_score.toFixed(0)} · ${formatPercent(topBull.daily_change_percent)}` : "No signal"}
              />
            </div>
            <div className="bg-surface/90 p-5">
              <Stat
                label="Weakest Setup"
                value={topBear?.ticker ?? "—"}
                tone="bear"
                size="lg"
                hint={
                  topBear
                    ? `Score ${topBear.overall_score.toFixed(0)} · ${formatPercent(topBear.daily_change_percent)}`
                    : "No qualified bearish setups today"
                }
              />
            </div>
            <div className="bg-surface/90 p-5">
              <Stat
                label="Macro Regime"
                value={macro.snapshot.regime}
                tone="warm"
                size="lg"
                hint={`Composite ${macro.snapshot.score.toFixed(0)} / 100`}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Leaderboards */}
      <section className="mt-10">
        <SectionHeader
          eyebrow="Universe Pulse"
          title="Conviction leaderboard"
          actions={
            <Link
              href="/leaderboard"
              className="inline-flex items-center gap-1 font-mono text-[11px] uppercase tracking-[0.22em] text-accentWarm hover:text-accentWarm/80"
            >
              Full board <ArrowRight className="h-3 w-3" />
            </Link>
          }
        />
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <LeaderboardCard
            title="Top bullish"
            subtitle="Highest explainable scores in the tracked universe."
            items={leaderboard.bullish}
            tone="bullish"
          />
          <LeaderboardCard
            title="Top bearish"
            subtitle="Where filings, news, or macro are dragging conviction down."
            items={leaderboard.bearish}
            tone="bearish"
          />
        </div>
      </section>

      {/* Macro and quick routes */}
      <section className="mt-10 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <MacroCard snapshot={macro.snapshot} />
        <div className="border border-rule/70 bg-surface/90">
          <div className="border-b border-rule/60 px-5 py-3">
            <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-muted-foreground">
              Quick routes
            </p>
            <h3 className="mt-0.5 text-sm font-semibold tracking-tight text-white">
              From signal to strategy
            </h3>
          </div>
          <div className="grid gap-px bg-rule/60 sm:grid-cols-2">
            <Link
              href={`/stocks/${topBull?.ticker ?? "NVDA"}`}
              className="group bg-surface/90 p-5 transition-colors hover:bg-surface2/40"
            >
              <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-muted-foreground">
                Open dossier
              </p>
              <p className="mt-3 font-mono text-2xl tabular-nums text-white">
                {topBull?.ticker ?? "NVDA"}
              </p>
              <p className="mt-2 inline-flex items-center gap-1 font-mono text-[11px] uppercase tracking-[0.22em] text-accentWarm">
                Inspect signal
                <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
              </p>
            </Link>
            <Link
              href={`/backtest?ticker=${topBull?.ticker ?? "NVDA"}`}
              className="group bg-surface/90 p-5 transition-colors hover:bg-surface2/40"
            >
              <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-muted-foreground">
                Strategy lab
              </p>
              <p className="mt-3 font-mono text-2xl tabular-nums text-white">
                Backtest
              </p>
              <p className="mt-2 inline-flex items-center gap-1 font-mono text-[11px] uppercase tracking-[0.22em] text-accentWarm">
                Run on {topBull?.ticker ?? "NVDA"}
                <CandlestickChart className="h-3.5 w-3.5" />
              </p>
            </Link>
          </div>
        </div>
      </section>
    </AppShell>
  );
}
