import * as React from "react";

import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  asChild?: boolean;
  variant?: "default" | "ghost" | "outline";
};

export function Button({ className, variant = "default", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-full px-4 text-sm font-medium transition duration-200",
        variant === "default" &&
          "bg-[linear-gradient(135deg,rgba(76,190,214,0.2),rgba(237,191,88,0.18))] text-foreground shadow-panel hover:brightness-110",
        variant === "ghost" && "text-muted-foreground hover:text-foreground",
        variant === "outline" &&
          "border border-[hsl(var(--border))] bg-transparent text-foreground hover:border-[hsl(var(--accent))]",
        className
      )}
      {...props}
    />
  );
}
