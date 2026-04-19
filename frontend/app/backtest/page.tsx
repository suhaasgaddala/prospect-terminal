import { endOfMonth, formatISO, startOfMonth, subMonths } from "date-fns";

import { EquityCurveChart } from "@/components/charts/equity-curve-chart";
import { AppShell } from "@/components/layout/app-shell";
import { TradeTable } from "@/components/tables/trade-table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Panel } from "@/components/ui/panel";
import { SectionHeader } from "@/components/ui/section-header";
import { Stat } from "@/components/ui/stat";
import { strategies } from "@/lib/constants";
import { formatPercent } from "@/lib/formatters";
import { api } from "@/services/api";

export const dynamic = "force-dynamic";

export default async function BacktestPage({
  searchParams
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = (await searchParams) ?? {};
  const ticker = typeof params.ticker === "string" ? params.ticker.toUpperCase() : "NVDA";
  const strategy = typeof params.strategy === "string" ? params.strategy : "threshold_cross";
  const threshold = typeof params.threshold === "string" ? Number(params.threshold) : 60;
  const exitThreshold =
    typeof params.exit_threshold === "string" ? Number(params.exit_threshold) : 45;
  const momentumWindow =
    typeof params.momentum_window === "string" ? Number(params.momentum_window) : 5;
  const momentumDelta =
    typeof params.momentum_delta === "string" ? Number(params.momentum_delta) : 8;
  const start =
    typeof params.start === "string"
      ? params.start
      : formatISO(startOfMonth(subMonths(new Date(), 6)), { representation: "date" });
  const end =
    typeof params.end === "string"
      ? params.end
      : formatISO(endOfMonth(new Date()), { representation: "date" });

  const data = await api.getBacktest({
    ticker,
    start,
    end,
    strategy,
    threshold,
    exit_threshold: exitThreshold,
    momentum_window: momentumWindow,
    momentum_delta: momentumDelta
  });

  const stratLabel = strategies.find((s) => s.key === strategy)?.label ?? strategy;
  const alpha = data.metrics.total_return - data.metrics.benchmark_return;
  const stratTone =
    data.metrics.total_return > 0
      ? "bull"
      : data.metrics.total_return < 0
      ? "bear"
      : "neutral";
  const alphaTone = alpha > 0 ? "bull" : alpha < 0 ? "bear" : "neutral";

  return (
    <AppShell currentPath="/backtest">
      <SectionHeader
        eyebrow="Strategy Lab"
        title="Score-driven backtest"
      />
      <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        Run simple Prospect Score signals against buy & hold using daily score persistence and explicit transaction costs.
      </p>

      {/* Controls */}
      <Panel
        eyebrow="Controls"
        title={`${ticker} · ${stratLabel}`}
        density="compact"
        className="mt-6"
      >
        <form className="grid gap-4 md:grid-cols-12">
          <Field label="Ticker" className="md:col-span-2">
            <Input name="ticker" defaultValue={ticker} className="uppercase tracking-[0.18em]" />
          </Field>
          <Field label="Strategy" className="md:col-span-3">
            <select
              name="strategy"
              defaultValue={strategy}
              className="h-9 w-full rounded-sm border border-rule/70 bg-surface2/60 px-3 font-mono text-sm text-foreground outline-none focus:border-accentWarm/60"
            >
              {strategies.map((item) => (
                <option key={item.key} value={item.key}>
                  {item.label}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Start" className="md:col-span-2">
            <Input name="start" type="date" defaultValue={start} />
          </Field>
          <Field label="End" className="md:col-span-2">
            <Input name="end" type="date" defaultValue={end} />
          </Field>
          <Field label="Buy ≥" className="md:col-span-1">
            <Input name="threshold" type="number" defaultValue={threshold} />
          </Field>
          <div className="flex items-end md:col-span-2">
            <Button type="submit" variant="primary" className="w-full">
              Run
            </Button>
          </div>
          <input type="hidden" name="exit_threshold" value={exitThreshold} />
          <input type="hidden" name="momentum_window" value={momentumWindow} />
          <input type="hidden" name="momentum_delta" value={momentumDelta} />
        </form>
      </Panel>

      {/* Metrics strip */}
      <section className="mt-6 grid gap-px overflow-hidden border border-rule/70 bg-rule/60 sm:grid-cols-2 lg:grid-cols-5">
        <div className="bg-surface/90 p-5">
          <Stat label="Strategy" value={formatPercent(data.metrics.total_return)} size="lg" tone={stratTone} />
        </div>
        <div className="bg-surface/90 p-5">
          <Stat label="Buy & Hold" value={formatPercent(data.metrics.benchmark_return)} size="lg" tone="neutral" />
        </div>
        <div className="bg-surface/90 p-5">
          <Stat label="Alpha" value={formatPercent(alpha)} size="lg" tone={alphaTone} hint="Strategy − benchmark" />
        </div>
        <div className="bg-surface/90 p-5">
          <Stat label="Win Rate" value={formatPercent(data.metrics.win_rate)} size="lg" tone="neutral" hint={`${data.metrics.trade_count} trades`} />
        </div>
        <div className="bg-surface/90 p-5">
          <Stat label="Max DD" value={formatPercent(-data.metrics.max_drawdown)} size="lg" tone="bear" />
        </div>
      </section>

      {/* Equity curve */}
      <section className="mt-8">
        <Panel eyebrow="Equity Curve" title="Strategy vs Buy & Hold" density="compact">
          <EquityCurveChart points={data.equity_curve} />
        </Panel>
      </section>

      {/* Trade log */}
      <section className="mt-8">
        <Panel
          eyebrow="Trade Log"
          title={`${data.trades.length} executed trade${data.trades.length === 1 ? "" : "s"}`}
          density="compact"
        >
          <TradeTable trades={data.trades} />
        </Panel>
      </section>
    </AppShell>
  );
}

function Field({
  label,
  className,
  children
}: {
  label: string;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={className}>
      <label className="mb-1.5 block font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
        {label}
      </label>
      {children}
    </div>
  );
}
