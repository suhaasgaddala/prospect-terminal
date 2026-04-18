import { AppShell } from "@/components/layout/app-shell";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function LoadingStockPage() {
  return (
    <AppShell>
      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <div className="rounded-[32px] border border-white/10 bg-white/[0.03] p-6 shadow-panel">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="mt-4 h-12 w-2/3" />
          <Skeleton className="mt-4 h-8 w-1/3" />
          <Skeleton className="mt-6 h-[220px] w-full" />
        </div>
        <div className="space-y-6">
          <Card>
            <Skeleton className="h-4 w-28" />
            <Skeleton className="mt-4 h-3 w-full" />
            <Skeleton className="mt-2 h-3 w-full" />
            <Skeleton className="mt-2 h-3 w-4/5" />
          </Card>
          <Card>
            <Skeleton className="h-4 w-24" />
            <Skeleton className="mt-4 h-10 w-28" />
            <Skeleton className="mt-4 h-3 w-full" />
            <Skeleton className="mt-2 h-3 w-11/12" />
          </Card>
        </div>
      </section>
      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <Skeleton className="h-[320px] w-full" />
        <Skeleton className="h-[340px] w-full" />
      </section>
      <section className="mt-6 grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Skeleton className="h-[320px] w-full" />
        <Skeleton className="h-[320px] w-full" />
      </section>
    </AppShell>
  );
}
