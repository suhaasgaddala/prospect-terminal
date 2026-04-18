import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-[28px] border border-[hsl(var(--border))] bg-[linear-gradient(180deg,rgba(10,15,17,0.92),rgba(6,9,11,0.96))] p-5 shadow-panel backdrop-blur",
        className
      )}
      {...props}
    />
  );
}
