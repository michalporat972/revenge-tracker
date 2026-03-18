import { Crosshair } from "lucide-react";

interface Stats {
  pending: number;
  served: number;
}

export function DashboardHeader({ stats }: { stats: Stats }) {
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container flex items-center justify-between py-4">
        <div className="flex items-center gap-3">
          <Crosshair className="h-8 w-8 text-primary" />
          <h1 className="text-2xl font-display font-bold tracking-tight text-foreground">
            Revenge<span className="text-primary">4</span>who
          </h1>
        </div>

        <div className="flex items-center gap-6 text-sm font-body">
          <div className="flex items-center gap-2">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-status-pending animate-pulse-glow" />
            <span className="text-muted-foreground">בדרך</span>
            <span className="font-display font-bold text-foreground">{stats.pending}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-status-hot" />
            <span className="text-muted-foreground">הוגשו</span>
            <span className="font-display font-bold text-foreground">{stats.served}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
