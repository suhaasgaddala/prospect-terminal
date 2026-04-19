import type { ReactNode } from "react";
import Link from "next/link";

import { CommandBar } from "@/components/layout/command-bar";
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
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b border-rule/60 bg-background/95 backdrop-blur">
        <div className="mx-auto flex max-w-[1400px] items-center gap-6 px-6 py-2.5">
          <Link href="/" className="flex items-center">
            <span className="text-[15px] font-semibold leading-none tracking-tight text-foreground">
              Prospect <span className="font-normal text-foreground/70">Terminal</span>
            </span>
          </Link>
          <nav className="ml-2 flex items-center">
            {navigation.map((item) => {
              const active = currentPath === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "border-b border-transparent px-3.5 py-2.5 font-mono text-[11px] font-medium uppercase leading-none tracking-[0.26em] text-muted-foreground transition-colors hover:text-foreground",
                    active && "border-accentWarm text-foreground"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="ml-auto" aria-hidden />
        </div>
        <CommandBar />
      </header>
      <main className="mx-auto max-w-[1400px] px-6 py-8">{children}</main>
      <footer className="mx-auto max-w-[1400px] border-t border-rule/60 px-6 py-6">
        <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-muted-foreground">
          Prospect Terminal · Sources: SEC · Yahoo Finance · NewsAPI · Reddit · X
        </p>
      </footer>
    </div>
  );
}
