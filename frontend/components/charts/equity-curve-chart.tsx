"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { formatDate } from "@/lib/formatters";
import { EquityPoint } from "@/types/generated-api";

const tooltipStyle = {
  background: "#06090b",
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: 2,
  fontSize: 12,
  fontFamily: "var(--font-mono)"
} as const;

const axisTick = {
  fill: "hsl(var(--muted-foreground))",
  fontSize: 11,
  fontFamily: "var(--font-mono)"
};

const legendStyle = {
  fontSize: 11,
  fontFamily: "var(--font-mono)",
  textTransform: "uppercase" as const,
  letterSpacing: "0.18em",
  color: "hsl(var(--muted-foreground))"
};

export function EquityCurveChart({ points }: { points: EquityPoint[] }) {
  if (points.length === 0) {
    return (
      <div className="flex h-[360px] items-center justify-center border border-rule/60 bg-surface/80 text-xs text-muted-foreground">
        No equity curve data is available for this backtest window.
      </div>
    );
  }

  return (
    <div className="h-[360px] border border-rule/60 bg-surface/80 p-3">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 8, right: 12, bottom: 0, left: -12 }}>
          <CartesianGrid stroke="hsl(var(--rule) / 0.6)" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={axisTick}
            axisLine={false}
            tickLine={false}
            minTickGap={24}
          />
          <YAxis tick={axisTick} axisLine={false} tickLine={false} width={56} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={legendStyle} iconType="plainline" />
          <Line
            type="monotone"
            dataKey="strategy_equity"
            name="Strategy"
            stroke="hsl(var(--accent-warm))"
            strokeWidth={1.75}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="benchmark_equity"
            name="Buy & Hold"
            stroke="hsl(var(--muted))"
            strokeWidth={1.25}
            strokeDasharray="4 4"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
