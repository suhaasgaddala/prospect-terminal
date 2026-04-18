"use client";

import { Button } from "@/components/ui/button";

export default function StockPageError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="mx-auto flex min-h-[60vh] w-full max-w-3xl flex-col items-center justify-center rounded-[32px] border border-rose-500/20 bg-rose-500/5 p-8 text-center">
      <p className="font-mono text-xs uppercase tracking-[0.28em] text-rose-200">Stock page unavailable</p>
      <h2 className="mt-4 text-3xl font-semibold text-white">Unable to load this ticker right now</h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
        The API may be starting up or temporarily unavailable. Retry to continue the demo flow.
      </p>
      <p className="mt-4 rounded-full border border-white/10 bg-black/30 px-4 py-2 font-mono text-xs text-muted-foreground">
        {error.message}
      </p>
      <Button className="mt-6" onClick={reset}>
        Try again
      </Button>
    </div>
  );
}
