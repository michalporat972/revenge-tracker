import { ConflictCycle } from "./types";

export const mockCycles: ConflictCycle[] = [
  {
    event: {
      id: "1",
      type: "assassination",
      description: "חיסול פואד שוכר — מפקד כוח רדואן, חיזבאללה",
      details: "תקיפה אווירית בביירות. מפקד בכיר ביחידת העילית של חיזבאללה חוסל בפגיעה ממוקדת.",
      date: "2024-01-08T14:30:00Z",
      sourceUrl: "https://example.com/source1",
    },
    signal: {
      id: "s1",
      eventId: "1",
      source: "hezbollah",
      description: "חיזבאללה הודיע: ׳הדם לא ייגרע ללא מענה׳. נסראללה הבטיח נקמה כואבת.",
      sourceUrl: "https://example.com/signal1",
    },
    status: "pending",
  },
  {
    event: {
      id: "2",
      type: "assassination",
      description: "חיסול סאלח אל-עארורי — סגן ראש הלשכה המדינית של חמאס",
      details: "פיצוץ ממוקד בדאחייה, ביירות. מת יחד עם שני מפקדים נוספים של גדודי עז א-דין אל-קסאם.",
      date: "2024-01-02T18:00:00Z",
    },
    signal: {
      id: "s2",
      eventId: "2",
      source: "hamas",
      description: "חמאס הצהיר: ׳ישראל תשלם מחיר כבד׳. ירי 20 רקטות לעבר צפון ישראל כ-18 שעות אחרי החיסול.",
      date: "2024-01-03T12:00:00Z",
      sourceUrl: "https://example.com/signal2",
    },
    status: "served_hot",
  },
  {
    event: {
      id: "3",
      type: "infrastructure",
      description: "הרס מנהרת הברחות — ציר פילדלפי, רפיח",
      details: "הנדסה קרבית פוצצה רשת מנהרות באורך 3 ק״מ שחיברה בין עזה למצרים.",
      date: "2024-02-15T09:00:00Z",
    },
    signal: {
      id: "s3",
      eventId: "3",
      source: "iran",
      description: "איראן הודיעה: ׳חציית קווים אדומים תוביל לתגובה אסטרטגית׳. 3 ימים לאחר מכן שוגרו כטב״מים מעיראק.",
      date: "2024-02-18T22:00:00Z",
    },
    status: "served_cold",
  },
  {
    event: {
      id: "4",
      type: "assassination",
      description: "חיסול ראא׳ד סעד — מפקד חטיבה דרומית, חיזבאללה",
      details: "תקיפה ממוקדת בדרום לבנון. מפקד הכוחות באזור נבטייה.",
      date: "2024-03-01T11:00:00Z",
    },
    signal: {
      id: "s4",
      eventId: "4",
      source: "hezbollah",
      description: "חיזבאללה הודיע על ׳מבצע תגמול כואב׳. ירי 50 רקטות לגליל.",
      sourceUrl: "https://example.com/signal4",
    },
    status: "pending",
  },
  {
    event: {
      id: "5",
      type: "infrastructure",
      description: "הפצצת בסיס אימונים של החות׳ים — חודיידה, תימן",
      details: "תקיפה אווירית על בסיס אל-דילמי. הרס חניוני כטב״מים ומחסני תחמושת.",
      date: "2024-03-10T06:00:00Z",
    },
    signal: {
      id: "s5",
      eventId: "5",
      source: "houthis",
      description: "אנצאר אללה: ׳נמשיך לתקוף ספינות ישראליות בים האדום. הנקמה בדרך.׳",
    },
    status: "pending",
  },
];
