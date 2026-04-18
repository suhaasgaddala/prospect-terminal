import { formatCurrency, formatPercent } from "@/lib/formatters";
import { BacktestTrade } from "@/types/generated-api";

export function TradeTable({ trades }: { trades: BacktestTrade[] }) {
  return (
    <div className="overflow-hidden rounded-[28px] border border-white/8 bg-black/20">
      <table className="w-full border-collapse text-left">
        <thead className="bg-white/[0.03]">
          <tr className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
            <th className="px-4 py-4 font-mono">Entry</th>
            <th className="px-4 py-4 font-mono">Exit</th>
            <th className="px-4 py-4 font-mono">Entry Px</th>
            <th className="px-4 py-4 font-mono">Exit Px</th>
            <th className="px-4 py-4 font-mono">Return</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={`${trade.entry_date}-${trade.exit_date}`} className="border-t border-white/5 text-sm text-slate-100">
              <td className="px-4 py-4">{trade.entry_date}</td>
              <td className="px-4 py-4">{trade.exit_date || "-"}</td>
              <td className="px-4 py-4">{formatCurrency(trade.entry_price)}</td>
              <td className="px-4 py-4">{trade.exit_price ? formatCurrency(trade.exit_price) : "-"}</td>
              <td className="px-4 py-4">{trade.return_pct !== null && trade.return_pct !== undefined ? formatPercent(trade.return_pct) : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
