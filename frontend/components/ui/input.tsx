import * as React from "react";

import { cn } from "@/lib/utils";

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-11 w-full rounded-full border border-[hsl(var(--border))] bg-black/30 px-4 text-sm text-foreground outline-none transition placeholder:text-muted-foreground/70 focus:border-[hsl(var(--accent))]",
        className
      )}
      {...props}
    />
  );
}
