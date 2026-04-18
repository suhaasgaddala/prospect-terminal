"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { formatDate } from "@/lib/formatters";
import { ScoreHistoryPoint } from "@/types/generated-api";

export function ScoreHistoryChart({ points }: { points: ScoreHistoryPoint[] }) {
  if (points.length === 0) {
    return (
      <div className="flex h-[320px] items-center justify-center rounded-[28px] border border-white/8 bg-black/20 px-6 text-sm text-muted-foreground">
        No score history available for this range.
      </div>
    );
  }

  return (
    <div className="h-[320px] rounded-[28px] border border-white/8 bg-black/20 p-4">
      <div className="mb-4">
        <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
          Score History
        </p>
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points}>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fill: "#88a2ad", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis tick={{ fill: "#88a2ad", fontSize: 12 }} axisLine={false} tickLine={false} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              background: "#040809",
              border: "1px solid rgba(78,192,214,0.2)",
              borderRadius: "18px"
            }}
          />
          <Line type="monotone" dataKey="overall_score" stroke="#61d3e9" strokeWidth={3} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
