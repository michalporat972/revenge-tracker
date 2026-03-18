import { cn } from "@/lib/utils";
import { Source, SOURCE_LABELS } from "@/lib/types";

const SOURCES: (Source | "all")[] = ["all", "iran", "hezbollah", "hamas", "houthis", "other"];

const SOURCE_DISPLAY: Record<string, string> = {
  all: "הכל",
  ...SOURCE_LABELS,
};

interface SourceFilterProps {
  active: Source | "all";
  onChange: (source: Source | "all") => void;
}

export function SourceFilter({ active, onChange }: SourceFilterProps) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto py-3 px-1">
      {SOURCES.map((source) => (
        <button
          key={source}
          onClick={() => onChange(source)}
          className={cn(
            "px-4 py-1.5 rounded-sm text-sm font-body font-medium transition-colors whitespace-nowrap border",
            active === source
              ? "bg-primary text-primary-foreground border-primary"
              : "bg-secondary text-secondary-foreground border-border hover:bg-accent"
          )}
        >
          {SOURCE_DISPLAY[source]}
        </button>
      ))}
    </div>
  );
}
