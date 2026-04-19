import { AppShell } from "@/components/layout/app-shell";
import { Skeleton } from "@/components/ui/skeleton";

export default function LoadingBacktestPage() {
  return (
    <AppShell currentPath="/backtest">
      <Skeleton className="h-3 w-32" />
      <Skeleton className="mt-3 h-8 w-2/3" />
      <Skeleton className="mt-3 h-3 w-full max-w-2xl" />
      <div className="mt-6 border border-rule/70 bg-surface/90 p-5">
        <div className="grid gap-3 md:grid-cols-12">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-9 md:col-span-2" />
          ))}
        </div>
      </div>
      <section className="mt-6 grid gap-px overflow-hidden border border-rule/70 bg-rule/60 sm:grid-cols-2 lg:grid-cols-5">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="bg-surface/90 p-5">
            <Skeleton className="h-3 w-20" />
            <Skeleton className="mt-3 h-7 w-24" />
          </div>
        ))}
      </section>
      <Skeleton className="mt-8 h-[360px] w-full" />
      <Skeleton className="mt-8 h-64 w-full" />
    </AppShell>
  );
}
