import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-md border border-rule/70 bg-surface/90 p-5 text-foreground",
        className
      )}
      {...props}
    />
  );
}
