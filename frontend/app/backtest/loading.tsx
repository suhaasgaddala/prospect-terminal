import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function LoadingBacktestPage() {
  return (
    <AppShell currentPath="/backtest">
      <section className="mb-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="mt-4 h-12 w-2/3" />
        <Skeleton className="mt-3 h-5 w-full max-w-2xl" />
      </section>
      <Card className="mb-6">
        <div className="grid gap-4 md:grid-cols-6">
          <Skeleton className="h-11 w-full" />
          <Skeleton className="h-11 w-full" />
          <Skeleton className="h-11 w-full" />
          <Skeleton className="h-11 w-full" />
          <Skeleton className="h-11 w-full" />
          <Skeleton className="h-11 w-full" />
        </div>
      </Card>
      <section className="grid gap-4 md:grid-cols-5">
        {Array.from({ length: 5 }).map((_, index) => (
          <Card key={index}>
            <Skeleton className="h-4 w-24" />
            <Skeleton className="mt-4 h-10 w-20" />
          </Card>
        ))}
      </section>
      <section className="mt-6">
        <Skeleton className="h-[360px] w-full" />
      </section>
      <section className="mt-6">
        <Skeleton className="h-[280px] w-full" />
      </section>
    </AppShell>
  );
}
