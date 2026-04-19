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
import { ScoreHistoryPoint } from "@/types/generated-api";

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

export function PriceVsScoreChart({ points }: { points: ScoreHistoryPoint[] }) {
  if (points.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center border border-rule/60 bg-surface/80 text-xs text-muted-foreground">
        No price/score points available for this range.
      </div>
    );
  }

  return (
    <div className="h-[300px] border border-rule/60 bg-surface/80 p-3">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
          <CartesianGrid stroke="hsl(var(--rule) / 0.6)" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={axisTick}
            axisLine={false}
            tickLine={false}
            minTickGap={24}
          />
          <YAxis
            yAxisId="left"
            tick={axisTick}
            axisLine={false}
            tickLine={false}
            domain={[0, 100]}
            width={36}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={axisTick}
            axisLine={false}
            tickLine={false}
            width={48}
          />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend wrapperStyle={legendStyle} iconType="plainline" />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="overall_score"
            name="Score"
            stroke="hsl(var(--accent-warm))"
            strokeWidth={1.75}
            dot={false}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="price_close"
            name="Price"
            stroke="hsl(var(--accent))"
            strokeWidth={1.5}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
