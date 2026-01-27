import * as React from "react"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "file:text-foreground placeholder:text-terminal-dim selection:bg-terminal/30 selection:text-foreground bg-input/50 border-border/60 h-9 w-full min-w-0 rounded-sm border px-3 py-1 text-sm tracking-wide transition-all duration-200 outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-40",
        "focus-visible:border-terminal focus-visible:bg-input/80 focus-visible:shadow-[0_0_10px_var(--terminal-glow)] focus-visible:ring-0",
        "hover:border-terminal/50 hover:bg-input/70",
        "aria-invalid:border-destructive aria-invalid:shadow-[0_0_10px_oklch(0.55_0.22_25/30%)]",
        className
      )}
      {...props}
    />
  )
}

export { Input }
