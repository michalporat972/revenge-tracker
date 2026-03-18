import { useState, useMemo } from "react";
import { DashboardHeader } from "@/components/DashboardHeader";
import { SourceFilter } from "@/components/SourceFilter";
import { ConflictCard } from "@/components/ConflictCard";
import { mockCycles } from "@/lib/mock-data";
import { Source } from "@/lib/types";

const Index = () => {
  const [activeSource, setActiveSource] = useState<Source | "all">("all");

  const filtered = useMemo(() => {
    if (activeSource === "all") return mockCycles;
    return mockCycles.filter((c) => c.signal.source === activeSource);
  }, [activeSource]);

  const stats = useMemo(() => ({
    pending: mockCycles.filter((c) => c.status === "pending").length,
    served: mockCycles.filter((c) => c.status !== "pending").length,
  }), []);

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
