"""
OSINT Crawler - revenge-tracker
Fetches Hebrew-language news from Google News RSS and appends new
ConflictCycle entries to public/events.json.

Output schema matches src/lib/types.ts -> ConflictCycle
"""

import feedparser
import json
import hashlib
import os
import time
from datetime import datetime, timezone
from urllib.parse import quote

# -- Search keywords -------------------------------------------------------------
KEYWORDS = [
    "נקמה", "ננקום", "לנקום", "נקמנו",
    "חוסל", "מחוסל", "חיסלנו", "חוסלו",
]

# -- FILTER: article MUST contain at least one enemy/country entity --------------
# Without this, Hebrew revenge words appear in sports, politics, crime, etc.
ENEMY_WORDS = [
    "איראן", "איראני", "חיזבאללה", "חזבאללה", "חיזבאלה",
    "חמאס", "קסאם", "עז א-דין", "עז אל-דין",
    "חות'ים", "חות\u05f3ים", "הות'ים", "הות\u05f3ים", "אנצאר אללה",
    "הג'יהאד", "הג\u05f3יהאד", "דאעש", "ISIS",
    "נסראללה", "סינוואר", "הנייה", "חנייה",
    "קודס", "חמינאי", "ח'מינאי", "ח\u05f3מינאי",
    "עזה", "רצועת עזה",
    "לבנון", "ביירות", "דאחייה",
    "תימן", "תימני",
    "עיראק", "עיראקי",
    "סוריה", "סורי",
    "פלסטיני", "פלסטינים",
]

# -- FILTER: article MUST also contain at least one military/security term -------
SECURITY_WORDS = [
    "חיסול", "חוסל", "מחוסל", "חיסלנו", "חוסלו",
    "תקיפה", "תקף", "תקפו", "תקפנו",
    "ירי", "ירה", "ירו",
    "שיגור", "שיגר", "שיגרו", "שיגרנו", "שוגר",
    "רקטה", "רקטות", "טיל", "טילים",
    "כטב\"מ", "כטב\u05f4מ", "מל\"ט",
    "מחבל", "מחבלים", "פיגוע",
    "מנהרה", "נשק", "תחמושת",
    "מבצע צבאי", "מבצע תגמול", "מבצע",
    "חיל", "לוחם", "כוחות",
    "הרס", "פיצוץ", "פוצץ",
    "נקמה", "נקמנו", "ננקום",
    "תגמול", "תגובה צבאית",
    "אזעקה", "יירוט",
    "נהרג", "הרוג", "מפקד", "בכיר",
]

# -- Event type classification ---------------------------------------------------
ASSASSINATION_WORDS = [
    "חיסול", "חוסל", "מחוסל", "חיסלנו", "חוסלו",
    "נהרג", "הרוג", "נפל", "מפקד", "בכיר", "מנהיג",
]
INFRASTRUCTURE_WORDS = [
    "תשתית", "מנהרה", "מחסן", "בסיס", "מבנה",
    "פיצוץ", "הרס", "השמיד", "פוצץ",
    "מפעל", "נמל", "שדה תעופה",
]

# -- Enemy source detection ------------------------------------------------------
SOURCE_MAP = {
    "hezbollah": ["חיזבאללה", "חזבאללה", "חיזבאלה", "נסראללה", "לבנון"],
    "hamas":     ["חמאס", "קסאם", "סינוואר", "הנייה", "חנייה", "עזה"],
    "houthis":   ["חות'ים", "חות\u05f3ים", "הות'ים", "הות\u05f3ים", "אנצאר", "תימן"],
    "iran":      ["איראן", "איראני", "קודס", "חמינאי", "ח'מינאי"],
}

# -- Revenge status: served indicators -------------------------------------------

# Past-tense actions that CONFIRM revenge was carried out
SERVED_STRONG = [
    "נקמנו", "שיגרנו", "ירינו", "פגענו", "תקפנו",
    "חיסלנו", "הרסנו", "ביצענו", "השמדנו",
    "פוצץ בתגובה", "תקף בתגובה", "ירה בתגובה",
    "בוצע תגמול",
]

# Contextual phrases implying revenge was served (need an action verb too)
SERVED_CONTEXT = [
    "מבצע תגמול", "בתגובה ל", "כנקמה על",
    "תגובה על", "נקמה על",
    "לאחר החיסול", "בעקבות הרצח",
    "בעקבות הפיגוע", "בעקבות החיסול",
]
SERVED_ACTION_VERBS = [
    "תקף", "ירה", "שיגר", "פגע", "הרס",
    "פוצץ", "הושמד", "בוצע", "יצא",
]

# -- Revenge status: pending indicators ------------------------------------------
PENDING_STRONG = [
    "ננקום", "לנקום", "יינקם", "נקמה בדרך",
    "נקמה תבוא", "יבוא החשבון",
    "הבטיח נקמה", "הכריז נקמה",
    "הדם לא ייגרע", "לא ייסלח",
]
PENDING_CONTEXT = [
    "הזהיר", "איים", "הבטיח", "הודיע",
    "ישלם מחיר", "לא ישכח", "נשבע",
    "נקמה כואבת",
]

# Articles <= this many hours old when served -> served_hot, else served_cold
SERVED_CUTOFF_HOURS = 72

MAX_PER_KEYWORD   = 15
SLEEP_BETWEEN_SEC = 1.5

REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(REPO_ROOT, "public", "events.json")


# -- Helpers ---------------------------------------------------------------------

def google_news_url(keyword):
    return (
        "https://news.google.com/rss/search"
        "?q={}&hl=iw&gl=IL&ceid=IL:iw".format(quote(keyword))
    )


def make_id(entry):
    key = (entry.get("link", "") + entry.get("title", "")).encode("utf-8")
    return "crawled_" + hashlib.md5(key).hexdigest()[:12]


def is_relevant(title):
    """Block domestic news: must name an enemy AND have military/security context."""
    has_enemy    = any(w in title for w in ENEMY_WORDS)
    has_security = any(w in title for w in SECURITY_WORDS)
    return has_enemy and has_security


def detect_event_type(title):
    if any(w in title for w in ASSASSINATION_WORDS):
        return "assassination"
    if any(w in title for w in INFRASTRUCTURE_WORDS):
        return "infrastructure"
    return "assassination"


def detect_source(title):
    for source, keywords in SOURCE_MAP.items():
        if any(kw in title for kw in keywords):
            return source
    return "other"


def detect_status(title, article_date):
    """
    served_hot  = confirmed retaliation, article <= 72 h old
    served_cold = confirmed retaliation, article >  72 h old
    pending     = threat / promise of future revenge
    """
    now = datetime.now(timezone.utc)
    age_hours = (now - article_date).total_seconds() / 3600

    # Strong served
    if any(w in title for w in SERVED_STRONG):
        return "served_hot" if age_hours <= SERVED_CUTOFF_HOURS else "served_cold"

    # Contextual served (phrase + action verb)
    if any(p in title for p in SERVED_CONTEXT):
        if any(v in title for v in SERVED_ACTION_VERBS):
            return "served_hot" if age_hours <= SERVED_CUTOFF_HOURS else "served_cold"

    # Strong pending
    if any(w in title for w in PENDING_STRONG):
        return "pending"

    # Contextual pending
    if any(w in title for w in PENDING_CONTEXT):
        return "pending"

    return "pending"


def build_signal_description(title, status, source):
    actor_labels = {
        "hezbollah": "חיזבאללה",
        "hamas":     "חמאס",
        "houthis":   "חות'ים",
        "iran":      "איראן",
        "other":     "גורם עוין",
    }
    actor = actor_labels.get(source, "גורם עוין")

    if status == "served_hot":
        return "[OSINT] {} - נקמה הוגשה חמה: {}".format(actor, title)
    if status == "served_cold":
        return "[OSINT] {} - נקמה הוגשה (מאוחרת): {}".format(actor, title)
    return "[OSINT] {} - איום/הצהרת נקמה: {}".format(actor, title)


def parse_date(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def get_publisher(entry):
    if hasattr(entry, "source") and hasattr(entry.source, "title"):
        return entry.source.title
    return ""


def entry_to_cycle(entry):
    eid       = make_id(entry)
    title     = entry.get("title", "").strip()
    link      = entry.get("link", "")
    pub       = get_publisher(entry)
    art_date  = parse_date(entry)
    date_iso  = art_date.isoformat()

    event_type  = detect_event_type(title)
    source      = detect_source(title)
    status      = detect_status(title, art_date)
    signal_desc = build_signal_description(title, status, source)
    served      = status in ("served_hot", "served_cold")

    return {
        "event": {
            "id":          eid,
            "type":        event_type,
            "description": title,
            "details":     "מקור: {}".format(pub) if pub else "נאסף אוטומטית מ-Google News",
            "date":        date_iso,
            "sourceUrl":   link,
        },
        "signal": {
            "id":          "sig_{}".format(eid),
            "eventId":     eid,
            "source":      source,
            "description": signal_desc,
            "date":        date_iso if served else None,
            "sourceUrl":   link,
        },
        "status":  status,
        "crawled": True,
    }


def load_existing():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save(cycles):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cycles, f, ensure_ascii=False, indent=2)


# -- Main ------------------------------------------------------------------------

def main():
    print("[{}] Starting OSINT crawl...".format(datetime.now(timezone.utc).isoformat()))

    existing     = load_existing()
    existing_ids = {c["event"]["id"] for c in existing if "event" in c}
    new_cycles   = []
    seen         = set()
    skipped      = 0

    for keyword in KEYWORDS:
        print("  -> {}".format(keyword))
        try:
            feed = feedparser.parse(google_news_url(keyword))
            for entry in feed.entries[:MAX_PER_KEYWORD]:
                eid   = make_id(entry)
                title = entry.get("title", "").strip()

                if eid in existing_ids or eid in seen:
                    continue
                if not title:
                    continue
                if not is_relevant(title):
                    skipped += 1
                    print("     x filtered: {}".format(title[:70]))
                    continue

                cycle = entry_to_cycle(entry)
                new_cycles.append(cycle)
                seen.add(eid)
                print("     + [{}] {}".format(cycle["status"], title[:70]))

            time.sleep(SLEEP_BETWEEN_SEC)

        except Exception as exc:
            print("  x error on '{}': {}".format(keyword, exc))

    print("\nFiltered out {} irrelevant articles.".format(skipped))

    if new_cycles:
        all_cycles = new_cycles + existing
        save(all_cycles)
        print("Done. Added {} new cycles. Total: {}".format(len(new_cycles), len(all_cycles)))
    else:
        print("Done. No new events found.")


if __name__ == "__main__":
    main()
