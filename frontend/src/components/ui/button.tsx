import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center cursor-pointer! justify-center gap-2 whitespace-nowrap rounded-sm text-sm font-medium transition-all duration-200 disabled:pointer-events-none disabled:opacity-40 disabled:cursor-not-allowed [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-terminal focus-visible:ring-offset-2 focus-visible:ring-offset-background aria-invalid:ring-destructive/20 aria-invalid:border-destructive uppercase tracking-wider",
  {
    variants: {
      variant: {
        default: "bg-terminal text-background hover:bg-terminal-bright hover:shadow-[0_0_15px_var(--terminal-glow)] active:scale-[0.98]",
        destructive:
          "bg-destructive/80 text-white hover:bg-destructive hover:shadow-[0_0_15px_oklch(0.55_0.22_25/30%)] active:scale-[0.98]",
        outline:
          "border border-terminal/50 bg-transparent text-terminal hover:bg-terminal/10 hover:border-terminal hover:shadow-[0_0_10px_var(--terminal-glow)] active:scale-[0.98]",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80 hover:text-terminal active:scale-[0.98]",
        ghost:
          "text-muted-foreground hover:bg-accent hover:text-terminal active:scale-[0.98]",
        link: "text-terminal underline-offset-4 hover:underline hover:text-terminal-bright",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-sm gap-1.5 px-3 has-[>svg]:px-2.5 text-xs",
        lg: "h-10 rounded-sm px-6 has-[>svg]:px-4",
        icon: "size-9",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
