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

export function EquityCurveChart({ points }: { points: EquityPoint[] }) {
  return (
    <div className="h-[360px] rounded-[28px] border border-white/8 bg-black/20 p-4">
      <div className="mb-4">
        <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
          Equity Curve
        </p>
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points}>
          <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
          <XAxis dataKey="date" tickFormatter={formatDate} tick={{ fill: "#88a2ad", fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#88a2ad", fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{
              background: "#040809",
              border: "1px solid rgba(78,192,214,0.2)",
              borderRadius: "18px"
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="strategy_equity" name="Score strategy" stroke="#61d3e9" strokeWidth={3} dot={false} />
          <Line type="monotone" dataKey="benchmark_equity" name="Buy & hold" stroke="#f0be4a" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
