import type { ReactNode } from "react";
import Link from "next/link";

import { demoTickers } from "@/lib/constants";
import { cn } from "@/lib/utils";

const navigation = [
  { href: "/", label: "Terminal" },
  { href: "/leaderboard", label: "Leaderboard" },
  { href: "/backtest", label: "Backtest" }
];

export function AppShell({
  children,
  currentPath
}: {
  children: ReactNode;
  currentPath?: string;
}) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(72,184,211,0.16),transparent_34%),linear-gradient(180deg,#06090b,#020406)] text-foreground">
      <div className="pointer-events-none fixed inset-0 bg-grid bg-[size:54px_54px] opacity-40" />
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(238,184,78,0.12),transparent_24%),radial-gradient(circle_at_80%_0%,rgba(82,191,214,0.14),transparent_22%)]" />
      <div className="relative mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-8 flex flex-col gap-6 rounded-[32px] border border-white/10 bg-black/20 px-5 py-4 backdrop-blur md:flex-row md:items-center md:justify-between">
          <div>
            <Link href="/" className="font-mono text-lg uppercase tracking-[0.3em] text-cyan-200">
              Prospect Terminal
            </Link>
            <p className="mt-2 max-w-xl text-sm text-muted-foreground">
              Signal, not noise.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <nav className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 p-1">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "rounded-full px-4 py-2 text-sm text-muted-foreground transition hover:text-foreground",
                    currentPath === item.href && "bg-white/10 text-foreground"
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="hidden items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/5 px-3 py-2 text-xs text-cyan-100 lg:flex">
              {demoTickers.map((ticker) => (
                <Link key={ticker} href={`/stocks/${ticker}`} className="hover:text-white">
                  {ticker}
                </Link>
              ))}
            </div>
          </div>
        </header>
        {children}
      </div>
    </div>
  );
}
