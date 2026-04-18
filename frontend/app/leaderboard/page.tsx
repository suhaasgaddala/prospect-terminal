import { AppShell } from "@/components/layout/app-shell";
import { LeaderboardCard } from "@/components/cards/leaderboard-card";
import { api } from "@/services/api";

export default async function LeaderboardPage() {
  const leaderboard = await api.getLeaderboard();

  return (
    <AppShell currentPath="/leaderboard">
      <section className="mb-6">
        <p className="font-mono text-xs uppercase tracking-[0.32em] text-cyan-200">
          Leaderboard
        </p>
        <h1 className="mt-4 text-5xl font-semibold text-white">Current score leaders</h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-muted-foreground">
          Ranked off the latest persisted score data so the terminal can show both breakout strength and downside pressure.
        </p>
      </section>
      <div className="grid gap-6 lg:grid-cols-2">
        <LeaderboardCard
          title="Bullish"
          subtitle="Names with the strongest score and thesis alignment."
          items={leaderboard.bullish}
          tone="bullish"
        />
        <LeaderboardCard
          title="Bearish"
          subtitle="Names where caution is showing up across the stack."
          items={leaderboard.bearish}
          tone="bearish"
        />
      </div>
    </AppShell>
  );
}
