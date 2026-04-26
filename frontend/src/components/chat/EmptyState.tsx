import { MessageSquareText } from "lucide-react";

export const EmptyState = () => {
  return (
    <div className="flex h-full min-h-[60vh] flex-col items-center justify-center px-6 text-center">
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-secondary text-primary">
        <MessageSquareText className="h-7 w-7" />
      </div>
      <h2 className="mb-2 text-xl font-semibold tracking-tight text-foreground">
        MSL Cruise Knowledge Assistant
      </h2>
      <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
        Ask anything about annotation rules, edge cases, or labeling guidelines.
      </p>
    </div>
  );
};