"use client";

import { Button } from "@/components/ui/button";

export default function BacktestPageError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="mx-auto mt-16 flex min-h-[50vh] w-full max-w-3xl flex-col items-center justify-center border border-bear/30 bg-bear/[0.05] p-8 text-center">
      <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-bear">
        Backtest unavailable
      </p>
      <h2 className="mt-3 text-2xl font-semibold tracking-tight text-white">
        Strategy could not run
      </h2>
      <p className="mt-3 max-w-xl text-xs leading-relaxed text-muted-foreground">
        Check that the backend API is reachable, then retry the simulation.
      </p>
      <p className="mt-4 max-w-2xl truncate border border-rule/70 bg-surface/90 px-3 py-1.5 font-mono text-[11px] text-muted-foreground">
        {error.message}
      </p>
      <Button className="mt-6" variant="primary" onClick={reset}>
        Try again
      </Button>
    </div>
  );
}
