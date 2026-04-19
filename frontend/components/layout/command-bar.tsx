"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { demoTickers } from "@/lib/constants";

function formatUtc(date: Date) {
  const hh = String(date.getUTCHours()).padStart(2, "0");
  const mm = String(date.getUTCMinutes()).padStart(2, "0");
  const ss = String(date.getUTCSeconds()).padStart(2, "0");
  return `${hh}:${mm}:${ss} UTC`;
}

function marketState(date: Date) {
  // Approximation using UTC. NYSE 14:30-21:00 UTC during DST.
  const day = date.getUTCDay();
  const minutes = date.getUTCHours() * 60 + date.getUTCMinutes();
  if (day === 0 || day === 6) return { label: "CLOSED", tone: "muted" as const };
  if (minutes >= 14 * 60 + 30 && minutes < 21 * 60) {
    return { label: "OPEN", tone: "bull" as const };
  }
  if (minutes >= 8 * 60 && minutes < 14 * 60 + 30) {
    return { label: "PRE-MKT", tone: "warm" as const };
  }
  if (minutes >= 21 * 60 && minutes < 24 * 60) {
    return { label: "AFTER-HRS", tone: "warm" as const };
  }
  return { label: "CLOSED", tone: "muted" as const };
}

export function CommandBar() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [now, setNow] = useState<Date | null>(null);

  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ticker = query.trim().toUpperCase();
    if (!ticker) return;
    router.push(`/stocks/${ticker}`);
  }

  const state = now ? marketState(now) : { label: "—", tone: "muted" as const };
  const stateColor =
    state.tone === "bull"
      ? "text-bull"
      : state.tone === "warm"
      ? "text-accentWarm"
      : "text-muted-foreground";

  return (
    <div className="border-b border-rule/60 bg-surface/80">
      <div className="mx-auto flex max-w-[1400px] flex-wrap items-center gap-x-6 gap-y-2 px-6 py-2 font-mono text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
        <div className="flex items-center gap-2">
          <span className={`h-1.5 w-1.5 rounded-full ${state.tone === "bull" ? "bg-bull" : state.tone === "warm" ? "bg-accentWarm" : "bg-muted-foreground/50"}`} />
          <span className={stateColor}>{state.label}</span>
        </div>
        <span className="tabular-nums text-foreground/80">{now ? formatUtc(now) : "--:--:-- UTC"}</span>
        <form onSubmit={onSubmit} className="ml-auto flex items-center gap-2">
          <span className="hidden md:inline">JUMP</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="TICKER"
            spellCheck={false}
            className="h-7 w-24 rounded-sm border border-rule/70 bg-background px-2 font-mono text-xs uppercase tracking-[0.2em] text-foreground outline-none placeholder:text-muted-foreground/60 focus:border-accentWarm/60"
          />
          <button
            type="submit"
            className="h-7 rounded-sm border border-accentWarm/50 bg-accentWarm/10 px-3 text-[10px] uppercase tracking-[0.22em] text-accentWarm hover:bg-accentWarm/20"
          >
            Open
          </button>
        </form>
        <div className="flex w-full items-center gap-3 overflow-x-auto pt-1 text-[10px] tracking-[0.22em] md:w-auto md:pt-0">
          <span className="text-muted-foreground/70">WATCH</span>
          {demoTickers.map((ticker) => (
            <Link
              key={ticker}
              href={`/stocks/${ticker}`}
              className="text-foreground/80 hover:text-accentWarm"
            >
              {ticker}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
