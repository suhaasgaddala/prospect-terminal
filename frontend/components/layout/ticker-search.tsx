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
    <div className="space-y-5">
      <form onSubmit={onSubmit} className="flex flex-col gap-3 sm:flex-row">
        <Input
          value={ticker}
          onChange={(event) => setTicker(event.target.value.toUpperCase())}
          placeholder="Search ticker"
          className="flex-1"
        />
        <Button type="submit" className="sm:w-40">
          Open Signal
        </Button>
      </form>
      <div className="flex flex-wrap gap-2">
        {demoTickers.map((item) => (
          <button
            key={item}
            onClick={() => router.push(`/stocks/${item}`)}
            className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.22em] text-muted-foreground transition hover:border-cyan-400/40 hover:text-white"
            type="button"
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}
