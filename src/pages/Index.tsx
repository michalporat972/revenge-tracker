import { useState, useMemo, useEffect } from "react";
import { DashboardHeader } from "@/components/DashboardHeader";
import { SourceFilter } from "@/components/SourceFilter";
import { ConflictCard } from "@/components/ConflictCard";
import { mockCycles } from "@/lib/mock-data";
import { ConflictCycle, Source } from "@/lib/types";

function useCycles() {
  const [crawled, setCrawled] = useState<ConflictCycle[]>([]);

  useEffect(() => {
    fetch(`/events.json?t=${Date.now()}`)
      .then((r) => (r.ok ? r.json() : []))
      .then((data: ConflictCycle[]) => {
        if (Array.isArray(data) && data.length > 0) {
          setCrawled(data);
        }
      })
      .catch(() => {
        // Fail silently — site works without crawled events
      });
  }, []);

  // Crawled events shown first; mock data fills the rest.
  // Deduplicate by event.id so IDs can never collide.
  const all = useMemo<ConflictCycle[]>(() => {
    const crawledIds = new Set(crawled.map((c) => c.event.id));
    const dedupedMock = mockCycles.filter((c) => !crawledIds.has(c.event.id));
    return [...crawled, ...dedupedMock];
  }, [crawled]);

  return all;
}

const Index = () => {
  const cycles = useCycles();
  const [activeSource, setActiveSource] = useState<Source | "all">("all");

  const filtered = useMemo(() => {
    if (activeSource === "all") return cycles;
    return cycles.filter((c) => c.signal.source === activeSource);
  }, [activeSource, cycles]);

  const stats = useMemo(() => ({
    pending: cycles.filter((c) => c.status === "pending").length,
    served:  cycles.filter((c) => c.status !== "pending").length,
  }), [cycles]);

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader stats={stats} />

      <main className="container py-6 space-y-4">
        <SourceFilter active={activeSource} onChange={setActiveSource} />

        <div className="space-y-4">
          {filtered.map((cycle) => (
            <ConflictCard key={cycle.event.id} cycle={cycle} />
          ))}

          {filtered.length === 0 && (
            <div className="text-center py-16 text-muted-foreground font-body">
              אין אירועים עבור מקור זה
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Index;
