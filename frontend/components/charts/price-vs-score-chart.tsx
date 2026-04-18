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

export function PriceVsScoreChart({ points }: { points: ScoreHistoryPoint[] }) {
  if (points.length === 0) {
    return (
      <div className="flex h-[340px] items-center justify-center rounded-[28px] border border-white/8 bg-black/20 px-6 text-sm text-muted-foreground">
        No price/score points available for this range.
      </div>
    );
  }

  return (
    <div className="h-[340px] rounded-[28px] border border-white/8 bg-black/20 p-4">
      <div className="mb-4">
        <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
          Price vs Score
        </p>
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points}>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis dataKey="date" tickFormatter={formatDate} tick={{ fill: "#88a2ad", fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis yAxisId="left" tick={{ fill: "#88a2ad", fontSize: 12 }} axisLine={false} tickLine={false} domain={[0, 100]} />
          <YAxis yAxisId="right" orientation="right" tick={{ fill: "#88a2ad", fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{
              background: "#040809",
              border: "1px solid rgba(78,192,214,0.2)",
              borderRadius: "18px"
            }}
          />
          <Legend />
          <Line yAxisId="left" type="monotone" dataKey="overall_score" name="Score" stroke="#61d3e9" strokeWidth={3} dot={false} />
          <Line yAxisId="right" type="monotone" dataKey="price_close" name="Price" stroke="#f0be4a" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
