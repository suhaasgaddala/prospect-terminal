import * as React from "react";

import { cn } from "@/lib/utils";

type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  shape?: "square" | "pill";
};

export function Input({ className, shape = "square", ...props }: InputProps) {
  return (
    <input
      className={cn(
        "h-9 w-full border border-rule/70 bg-surface2/60 px-3 font-mono text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground/70 focus:border-accentWarm/60",
        shape === "pill" ? "rounded-full px-4" : "rounded-sm",
        className
      )}
      {...props}
    />
  );
}
