"""
OSINT Crawler — revenge-tracker
Fetches Hebrew-language news from Google News RSS and appends new
ConflictCycle entries to public/events.json.

Output schema matches src/lib/types.ts → ConflictCycle
"""

import feedparser
import json
import hashlib
import os
import time
from datetime import datetime, timezone
from urllib.parse import quote

# ── Keywords ────────────────────────────────────────────────────────────────────
KEYWORDS = [
    "נקמה", "ננקום", "לנקום", "נקמנו",
    "חוסל", "מחוסל", "חיסלנו", "חוסלו",
]

# ── Classification maps ──────────────────────────────────────────────────────────
ASSASSINATION_WORDS   = ["חוסל", "מחוסל", "חיסלנו", "חוסלו", "חיסול", "ירה", "נהרג", "בכיר"]
INFRASTRUCTURE_WORDS  = ["תשתית", "מנהרה", "מחסן", "בסיס", "מבנה", "פיצוץ", "הרס", "השמיד"]

SOURCE_MAP = {
    "hezbollah": ["חיזבאללה", "חזבאללה", "נסראללה"],
    "hamas":     ["חמאס", "קסאם", "סינוואר", "הנייה"],
    "houthis":   ["חות'ים", "חות׳ים", "אנצאר", "תימן", "הות'ים"],
    "iran":      ["איראן", "פסד", "קודס", "חמינאי"],
}

REVENGE_SERVED_WORDS  = ["נקמנו", "שיגרנו", "ירינו", "פגענו"]
REVENGE_PENDING_WORDS = ["ננקום", "לנקום", "נקמה", "יינקם", "הדם לא"]

MAX_PER_KEYWORD   = 15
SLEEP_BETWEEN_SEC = 1.5

# Resolve path relative to repo root (crawler/ is one level deep)
REPO_ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE  = os.path.join(REPO_ROOT, "public", "events.json")


def google_news_url(keyword: str) -> str:
    return (
        f"https://news.google.com/rss/search"
        f"?q={quote(keyword)}&hl=iw&gl=IL&ceid=IL:iw"
    )


def make_id(entry) -> str:
    key = (entry.get("link", "") + entry.get("title", "")).encode("utf-8")
    return "crawled_" + hashlib.md5(key).hexdigest()[:12]


def detect_event_type(text: str) -> str:
    if any(w in text for w in ASSASSINATION_WORDS):
        return "assassination"
    if any(w in text for w in INFRASTRUCTURE_WORDS):
        return "infrastructure"
    return "assassination"  # default


def detect_source(text: str) -> str:
    for source, keywords in SOURCE_MAP.items():
        if any(kw in text for kw in keywords):
            return source
    return "other"


def detect_status(text: str) -> str:
    if any(w in text for w in REVENGE_SERVED_WORDS):
        return "served_hot"
    if any(w in text for w in REVENGE_PENDING_WORDS):
        return "pending"
    return "pending"


def parse_date(entry) -> str:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.isoformat()
    return datetime.now(timezone.utc).isoformat()


def get_publisher(entry) -> str:
    if hasattr(entry, "source") and hasattr(entry.source, "title"):
        return entry.source.title
    return ""


def entry_to_cycle(entry) -> dict:
    eid      = make_id(entry)
    title    = entry.get("title", "").strip()
    link     = entry.get("link", "")
    date_iso = parse_date(entry)
    pub      = get_publisher(entry)

    event_type = detect_event_type(title)
    source     = detect_source(title)
    status     = detect_status(title)

    # Generate a terse signal description from the title
    if status == "served_hot":
        signal_desc = f"[OSINT] נקמה הוגשה — {title}"
    elif status == "pending":
        signal_desc = f"[OSINT] איום נקמה — {title}"
    else:
        signal_desc = f"[OSINT] {title}"

    return {
        "event": {
            "id": eid,
            "type": event_type,
            "description": title,
            "details": f"מקור: {pub}" if pub else "נאסף אוטומטית",
            "date": date_iso,
            "sourceUrl": link,
        },
        "signal": {
            "id": f"sig_{eid}",
            "eventId": eid,
            "source": source,
            "description": signal_desc,
            "sourceUrl": link,
        },
        "status": status,
        "crawled": True,
    }


def load_existing() -> list:
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save(cycles: list) -> None:
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cycles, f, ensure_ascii=False, indent=2)


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting OSINT crawl…")

    existing    = load_existing()
    existing_ids = {c["event"]["id"] for c in existing if "event" in c}
    new_cycles  = []
    seen        = set()

    for keyword in KEYWORDS:
        print(f"  → {keyword}")
        try:
            feed = feedparser.parse(google_news_url(keyword))
            for entry in feed.entries[:MAX_PER_KEYWORD]:
                eid = make_id(entry)
                if eid in existing_ids or eid in seen:
                    continue
                title = entry.get("title", "").strip()
                if not title:
                    continue
                new_cycles.append(entry_to_cycle(entry))
                seen.add(eid)
            time.sleep(SLEEP_BETWEEN_SEC)
        except Exception as exc:
            print(f"  ✗ error on '{keyword}': {exc}")

    if new_cycles:
        # Prepend new cycles so newest appear first
        all_cycles = new_cycles + existing
        save(all_cycles)
        print(f"✓ Added {len(new_cycles)} new cycles. Total: {len(all_cycles)}")
    else:
        print("✓ No new events found.")


if __name__ == "__main__":
    main()
