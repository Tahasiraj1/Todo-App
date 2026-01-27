"use client"

import * as React from "react"
import * as CheckboxPrimitive from "@radix-ui/react-checkbox"
import { CheckIcon } from "lucide-react"

import { cn } from "@/lib/utils"

function Checkbox({
  className,
  ...props
}: React.ComponentProps<typeof CheckboxPrimitive.Root>) {
  return (
    <CheckboxPrimitive.Root
      data-slot="checkbox"
      className={cn(
        "peer border-terminal/40 bg-input/30 data-[state=checked]:bg-terminal data-[state=checked]:text-background data-[state=checked]:border-terminal data-[state=checked]:shadow-[0_0_8px_var(--terminal-glow)] focus-visible:border-terminal focus-visible:ring-2 focus-visible:ring-terminal/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background aria-invalid:border-destructive size-4 shrink-0 rounded-[2px] border transition-all duration-200 outline-none disabled:cursor-not-allowed disabled:opacity-40 hover:border-terminal/70 hover:bg-input/50",
        className
      )}
      {...props}
    >
      <CheckboxPrimitive.Indicator
        data-slot="checkbox-indicator"
        className="grid place-content-center text-current animate-in zoom-in-50 duration-150"
      >
        <CheckIcon className="size-3.5" />
      </CheckboxPrimitive.Indicator>
    </CheckboxPrimitive.Root>
  )
}

export { Checkbox }
