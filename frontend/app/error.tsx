"use client";

import { Button } from "@/components/ui/button";

export default function GlobalError({
  error,
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="mx-auto mt-16 flex min-h-[50vh] w-full max-w-3xl flex-col items-center justify-center border border-bear/30 bg-bear/[0.05] p-8 text-center">
      <p className="font-mono text-[10px] uppercase tracking-[0.32em] text-bear">
        Application error
      </p>
      <h2 className="mt-3 text-2xl font-semibold tracking-tight text-white">
        Unable to load this page
      </h2>
      <p className="mt-3 max-w-2xl text-xs leading-relaxed text-muted-foreground">
        If the backend is not running, start it on port 8000 and ensure{" "}
        <code className="border border-rule/70 bg-surface/90 px-1 py-0.5 font-mono text-[11px]">API_BASE_URL</code>{" "}
        in{" "}
        <code className="border border-rule/70 bg-surface/90 px-1 py-0.5 font-mono text-[11px]">.env.local</code>{" "}
        points to your API.
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
