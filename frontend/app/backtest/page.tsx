import { endOfMonth, formatISO, startOfMonth, subMonths } from "date-fns";

import { EquityCurveChart } from "@/components/charts/equity-curve-chart";
import { AppShell } from "@/components/layout/app-shell";
import { TradeTable } from "@/components/tables/trade-table";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { strategies } from "@/lib/constants";
import { formatPercent } from "@/lib/formatters";
import { api } from "@/services/api";

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

  return (
    <AppShell currentPath="/backtest">
      <section className="mb-6">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-cyan-200">
          Backtest
        </p>
        <h1 className="mt-4 text-5xl font-semibold text-white">
          Score-based daily strategy testing
        </h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-muted-foreground">
          Compare simple score signals against buy-and-hold using daily historical score persistence and explicit transaction costs.
        </p>
      </section>

      <Card className="mb-6">
        <form className="grid gap-4 md:grid-cols-6">
          <div className="md:col-span-1">
            <label className="mb-2 block font-mono text-xs uppercase tracking-[0.24em] text-muted-foreground">
              Ticker
            </label>
            <Input name="ticker" defaultValue={ticker} />
          </div>
          <div className="md:col-span-1">
            <label className="mb-2 block font-mono text-xs uppercase tracking-[0.24em] text-muted-foreground">
              Strategy
            </label>
            <select
              name="strategy"
              defaultValue={strategy}
              className="h-11 w-full rounded-full border border-[hsl(var(--border))] bg-black/30 px-4 text-sm text-white"
            >
              {strategies.map((item) => (
                <option key={item.key} value={item.key}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-2 block font-mono text-xs uppercase tracking-[0.24em] text-muted-foreground">
              Start
            </label>
            <Input name="start" type="date" defaultValue={start} />
          </div>
          <div>
            <label className="mb-2 block font-mono text-xs uppercase tracking-[0.24em] text-muted-foreground">
              End
            </label>
            <Input name="end" type="date" defaultValue={end} />
          </div>
          <div>
            <label className="mb-2 block font-mono text-xs uppercase tracking-[0.24em] text-muted-foreground">
              Buy threshold
            </label>
            <Input name="threshold" type="number" defaultValue={threshold} />
          </div>
          <div className="flex items-end">
            <Button type="submit" className="w-full">
              Run Backtest
            </Button>
          </div>
          <input type="hidden" name="exit_threshold" value={exitThreshold} />
          <input type="hidden" name="momentum_window" value={momentumWindow} />
          <input type="hidden" name="momentum_delta" value={momentumDelta} />
        </form>
      </Card>

      <section className="grid gap-4 md:grid-cols-5">
        <Card>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            Strategy Return
          </p>
          <p className="mt-4 text-4xl font-semibold text-white">
            {formatPercent(data.metrics.total_return)}
          </p>
        </Card>
        <Card>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            Benchmark
          </p>
          <p className="mt-4 text-4xl font-semibold text-white">
            {formatPercent(data.metrics.benchmark_return)}
          </p>
        </Card>
        <Card>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            Trades
          </p>
          <p className="mt-4 text-4xl font-semibold text-white">{data.metrics.trade_count}</p>
        </Card>
        <Card>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            Win Rate
          </p>
          <p className="mt-4 text-4xl font-semibold text-white">
            {formatPercent(data.metrics.win_rate)}
          </p>
        </Card>
        <Card>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            Max Drawdown
          </p>
          <p className="mt-4 text-4xl font-semibold text-white">
            {formatPercent(-data.metrics.max_drawdown)}
          </p>
        </Card>
      </section>

      <section className="mt-6">
        <EquityCurveChart points={data.equity_curve} />
      </section>

      <section className="mt-6">
        <div className="mb-4">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
            Trade Log
          </p>
        </div>
        <TradeTable trades={data.trades} />
      </section>
    </AppShell>
  );
}
