import { ConflictCycle, STATUS_LABELS, SOURCE_LABELS, EVENT_TYPE_LABELS } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { ArrowLeft, ExternalLink, Skull, Building2, Clock, Radio } from "lucide-react";

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("he-IL", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

function getTimeDiff(eventDate: string, revengeDate: string): string {
  const diff = new Date(revengeDate).getTime() - new Date(eventDate).getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 24) return `${hours} שעות`;
  const days = Math.floor(hours / 24);
  return `${days} ימים`;
}

const statusStyles: Record<string, string> = {
  pending: "bg-status-pending/15 text-status-pending border-status-pending/30",
  served_hot: "bg-status-hot/15 text-status-hot border-status-hot/30",
  served_cold: "bg-status-cold/15 text-status-cold border-status-cold/30",
};

export function ConflictCard({ cycle }: { cycle: ConflictCycle }) {
  const { event, signal, status } = cycle;
  const EventIcon = event.type === "assassination" ? Skull : Building2;

  return (
    <Card className="overflow-hidden border-border bg-card hover:bg-card/80 transition-colors">
      {/* Status bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-border">
        <div className="flex items-center gap-2">
          <Badge
            className={cn(
              "rounded-sm text-xs font-display font-semibold border",
              statusStyles[status]
            )}
          >
            {STATUS_LABELS[status]}
          </Badge>
          {cycle.crawled && (
            <Badge className="rounded-sm text-xs border bg-sky-500/10 text-sky-400 border-sky-500/25 flex items-center gap-1">
              <Radio className="h-2.5 w-2.5" />
              OSINT
            </Badge>
          )}
        </div>
        <span className="text-xs text-muted-foreground font-body">
          {SOURCE_LABELS[signal.source]}
        </span>
      </div>

      {/* Content */}
      <div className="grid grid-cols-[1fr_auto_1fr] gap-0">
        {/* Event side */}
        <div className="p-4 space-y-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <EventIcon className="h-3.5 w-3.5" />
            <span>{EVENT_TYPE_LABELS[event.type]}</span>
          </div>
          <p className="text-sm font-display font-semibold text-foreground leading-snug">
            {event.description}
          </p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {event.details}
          </p>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{formatDate(event.date)}</span>
          </div>
          {event.sourceUrl && (
            <a
              href={event.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
            >
              <ExternalLink className="h-3 w-3" />
              מקור
            </a>
          )}
        </div>

        {/* Arrow bridge */}
        <div className="flex items-center justify-center px-2 border-x border-border">
          <div className="flex flex-col items-center gap-1">
            <ArrowLeft className={cn(
              "h-5 w-5",
              status === "pending" ? "text-status-pending" :
              status === "served_hot" ? "text-status-hot" : "text-status-cold"
            )} />
            {signal.date && (
              <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                {getTimeDiff(event.date, signal.date)}
              </span>
            )}
          </div>
        </div>

        {/* Revenge signal side */}
        <div className="p-4 space-y-2">
          <div className="text-xs text-muted-foreground">
            תגובה / איום
          </div>
          <p className="text-sm font-body text-foreground leading-snug">
            {signal.description}
          </p>
          {signal.date && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{formatDate(signal.date)}</span>
            </div>
          )}
          {signal.sourceUrl && (
            <a
              href={signal.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
            >
              <ExternalLink className="h-3 w-3" />
              מקור
            </a>
          )}
        </div>
      </div>
    </Card>
  );
}
