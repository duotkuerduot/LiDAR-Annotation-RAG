import { FileText } from "lucide-react";

interface SourcesListProps {
  sources: string[];
}

export const SourcesList = ({ sources }: SourcesListProps) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 border-t border-border/60 pt-2.5">
      <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
        Sources
      </p>
      <ul className="flex flex-col gap-1">
        {sources.map((source, i) => (
          <li
            key={i}
            className="flex items-center gap-1.5 text-xs text-muted-foreground"
          >
            <FileText className="h-3 w-3 shrink-0 text-primary/70" />
            <span className="truncate">{source}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};