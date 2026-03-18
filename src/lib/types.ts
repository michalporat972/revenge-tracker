export type EventType = "assassination" | "infrastructure";
export type Source = "iran" | "hezbollah" | "hamas" | "houthis" | "other";
export type RevengeStatus = "pending" | "served_hot" | "served_cold";

export interface ConflictEvent {
  id: string;
  type: EventType;
  description: string;
  details: string;
  date: string; // ISO
  sourceUrl?: string;
}

export interface RevengeSignal {
  id: string;
  eventId: string;
  source: Source;
  description: string;
  date?: string; // ISO — when revenge was served
  sourceUrl?: string;
}

export interface ConflictCycle {
  event: ConflictEvent;
  signal: RevengeSignal;
  status: RevengeStatus;
  crawled?: boolean; // true = auto-fetched by OSINT crawler
}

export const SOURCE_LABELS: Record<Source, string> = {
  iran: "איראן",
  hezbollah: "חיזבאללה",
  hamas: "חמאס",
  houthis: "חות׳ים",
  other: "אחר",
};

export const STATUS_LABELS: Record<RevengeStatus, string> = {
  pending: "נקמה בדרך",
  served_hot: "הוגשה חמה 🔥",
  served_cold: "הוגשה קרה 🧊",
};

export const EVENT_TYPE_LABELS: Record<EventType, string> = {
  assassination: "חיסול",
  infrastructure: "הרס תשתית",
};
