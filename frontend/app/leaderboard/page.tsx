import { AppShell } from "@/components/layout/app-shell";
import { LeaderboardCard } from "@/components/cards/leaderboard-card";
import { SectionHeader } from "@/components/ui/section-header";
import { api } from "@/services/api";

export const dynamic = "force-dynamic";

export default async function LeaderboardPage() {
  const leaderboard = await api.getLeaderboard();

  return (
    <AppShell currentPath="/leaderboard">
      <SectionHeader eyebrow="Universe Pulse" title="Score leaders" />
      <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        Ranked off the latest persisted Prospect Scores. Bullish names show breakout strength; bearish names show downside pressure across news, filings, and macro.
      </p>
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <LeaderboardCard
          title="Bullish"
          subtitle="Strongest score and thesis alignment."
          items={leaderboard.bullish}
          tone="bullish"
        />
        <LeaderboardCard
          title="Bearish"
          subtitle="Where caution is showing up across the stack."
          items={leaderboard.bearish}
          tone="bearish"
        />
      </div>
    </AppShell>
  );
}
