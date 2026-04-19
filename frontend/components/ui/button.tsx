import * as React from "react";

import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  asChild?: boolean;
  variant?: "default" | "primary" | "secondary" | "ghost" | "outline";
  size?: "sm" | "md";
};

export function Button({
  className,
  variant = "default",
  size = "md",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-sm border font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accentWarm/60",
        size === "sm" ? "h-8 px-3 text-xs" : "h-9 px-4 text-sm",
        (variant === "default" || variant === "primary") &&
          "border-accentWarm/60 bg-accentWarm/15 text-accentWarm hover:bg-accentWarm/25",
        variant === "secondary" &&
          "border-rule/70 bg-surface2/60 text-foreground hover:border-foreground/40",
        variant === "outline" &&
          "border-rule/70 bg-transparent text-foreground hover:border-foreground/40",
        variant === "ghost" &&
          "border-transparent text-muted-foreground hover:text-foreground",
        className
      )}
      {...props}
    />
  );
}
