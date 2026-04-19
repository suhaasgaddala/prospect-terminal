import { AppShell } from "@/components/layout/app-shell";
import { Skeleton } from "@/components/ui/skeleton";

export default function LoadingStockPage() {
  return (
    <AppShell>
      <section className="border-b border-rule/60 pb-6">
        <Skeleton className="h-3 w-32" />
        <Skeleton className="mt-3 h-10 w-2/3" />
        <div className="mt-6 grid gap-px overflow-hidden border border-rule/70 bg-rule/60 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-surface/90 p-5">
              <Skeleton className="h-3 w-20" />
              <Skeleton className="mt-3 h-8 w-24" />
              <Skeleton className="mt-2 h-3 w-16" />
            </div>
          ))}
        </div>
      </section>
      <section className="mt-8 grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <Skeleton className="h-72 w-full" />
        <div className="space-y-6">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-32 w-full" />
        </div>
      </section>
      <section className="mt-8 grid gap-6 xl:grid-cols-2">
        <Skeleton className="h-[300px] w-full" />
        <Skeleton className="h-[320px] w-full" />
      </section>
    </AppShell>
  );
}
