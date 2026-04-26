import { Sparkles } from "lucide-react";

export const Header = () => {
  return (
    <header className="sticky top-0 z-20 border-b border-border bg-surface/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-4xl items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <Sparkles className="h-4 w-4" />
          </div>
          <h1 className="text-sm font-semibold tracking-tight text-foreground sm:text-base">
            MSL Cruise Assistant
          </h1>
        </div>
        <span className="rounded-full border border-border bg-surface-muted px-2.5 py-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          DDD Internal Tool
        </span>
      </div>
    </header>
  );
};