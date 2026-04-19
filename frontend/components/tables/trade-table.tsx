import { formatCurrency, formatPercent } from "@/lib/formatters";
import { BacktestTrade } from "@/types/generated-api";

export function TradeTable({ trades }: { trades: BacktestTrade[] }) {
  if (trades.length === 0) {
    return (
      <div className="border border-dashed border-rule/60 bg-surface/80 p-6 text-center text-xs text-muted-foreground">
        No trades triggered. Lower the buy threshold or widen the window.
      </div>
    );
  }

  return (
    <div className="overflow-hidden border border-rule/60 bg-surface/90">
      <table className="w-full border-collapse text-left">
        <thead className="bg-surface2/60">
          <tr className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
            <th className="px-4 py-2.5 font-medium">Entry</th>
            <th className="px-4 py-2.5 font-medium">Exit</th>
            <th className="px-4 py-2.5 text-right font-medium">Entry Px</th>
            <th className="px-4 py-2.5 text-right font-medium">Exit Px</th>
            <th className="px-4 py-2.5 text-right font-medium">Return</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade, idx) => {
            const ret = trade.return_pct;
            const tone =
              ret == null
                ? "text-muted-foreground"
                : ret > 0
                ? "text-bull"
                : ret < 0
                ? "text-bear"
                : "text-foreground";
            return (
              <tr
                key={`${trade.entry_date}-${trade.exit_date}-${idx}`}
                className="border-t border-rule/50 font-mono text-xs tabular-nums text-foreground/90 odd:bg-surface/90 even:bg-surface2/30"
              >
                <td className="px-4 py-2.5">{trade.entry_date}</td>
                <td className="px-4 py-2.5">{trade.exit_date || "—"}</td>
                <td className="px-4 py-2.5 text-right">{formatCurrency(trade.entry_price)}</td>
                <td className="px-4 py-2.5 text-right">
                  {trade.exit_price ? formatCurrency(trade.exit_price) : "—"}
                </td>
                <td className={`px-4 py-2.5 text-right font-medium ${tone}`}>
                  {ret !== null && ret !== undefined ? formatPercent(ret) : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
