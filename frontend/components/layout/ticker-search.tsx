"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { demoTickers } from "@/lib/constants";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function TickerSearch() {
  const router = useRouter();
  const [ticker, setTicker] = useState("NVDA");

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!ticker.trim()) return;
    router.push(`/stocks/${ticker.trim().toUpperCase()}`);
  }

  return (
    <div className="space-y-3">
      <form onSubmit={onSubmit} className="flex flex-col gap-2 sm:flex-row">
        <Input
          value={ticker}
          onChange={(event) => setTicker(event.target.value.toUpperCase())}
          placeholder="ENTER TICKER"
          className="flex-1 uppercase tracking-[0.18em]"
          spellCheck={false}
        />
        <Button type="submit" variant="primary" className="sm:w-44">
          Open Dossier
        </Button>
      </form>
      <div className="flex flex-wrap gap-1.5">
        {demoTickers.map((item) => (
          <button
            key={item}
            onClick={() => router.push(`/stocks/${item}`)}
            type="button"
            className="rounded-sm border border-rule/70 bg-surface2/40 px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground transition-colors hover:border-accentWarm/50 hover:text-foreground"
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}
