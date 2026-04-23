import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "data" / "vocalizations.db"
REPORTS_DIR = ROOT / "ops" / "reports"

CONTEXT_FIELDS = [
    "time_bucket",
    "meal_context",
    "owner_context",
    "environment_trigger",
    "activity_context",
    "location_context",
]


def load_vocalization_rows():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT recording_id, created_at, primary_tendency, labeler_confidence,
               clip_quality, duration_ms, time_bucket, meal_context,
               owner_context, environment_trigger, activity_context,
               location_context, note
        FROM vocalizations
        ORDER BY datetime(created_at) DESC, recording_id DESC
        """
    ).fetchall()
    con.close()
    return rows


def compute_dataset_health(rows):
    total = len(rows)
    quality = Counter(row["clip_quality"] or "unknown" for row in rows)
    confidence = Counter(row["labeler_confidence"] or "unknown" for row in rows)
    tendency = Counter(row["primary_tendency"] or "unknown" for row in rows)

    distinct_contexts = {}
    for field in CONTEXT_FIELDS:
        values = {row[field] for row in rows if row[field] not in (None, "", "unknown")}
        distinct_contexts[field] = len(values)

    return {
        "total": total,
        "quality": quality,
        "confidence": confidence,
        "unknown_count": tendency.get("unknown", 0),
        "unknown_ratio": ((tendency.get("unknown", 0) / total) if total else 0),
        "distinct_contexts": distinct_contexts,
    }


def ratio_text(count, total):
    if not total:
        return "0 (0.0%)"
    return f"{count} ({count / total:.1%})"


def top_context_clusters(rows, limit=8):
    clusters = Counter()
    for row in rows:
        for field in CONTEXT_FIELDS:
            value = row.get(field)
            if value and value != "unknown":
                clusters[f"{field}={value}"] += 1
    return clusters.most_common(limit)


def top_reason_clusters(rows, limit=8):
    reasons = Counter()
    for row in rows:
        for reason in row.get("reasons", []):
            if reason:
                reasons[reason] += 1
    return reasons.most_common(limit)


def update_reports_index(report_date):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    index_path = REPORTS_DIR / "index.md"
    weekly_path = REPORTS_DIR / f"weekly_summary_{report_date}.md"
    disagreement_path = REPORTS_DIR / f"disagreement_report_{report_date}.md"
    intent_bias_path = REPORTS_DIR / f"intent_bias_report_{report_date}.md"

    lines = [
        "# Reports Index",
        "",
        f"Latest report date: {report_date}",
        "",
        "## Reports",
        f"- Weekly summary: {weekly_path.name if weekly_path.exists() else 'not generated yet'}",
        f"- Disagreement report: {disagreement_path.name if disagreement_path.exists() else 'not generated yet'}",
        f"- Intent bias report: {intent_bias_path.name if intent_bias_path.exists() else 'not generated yet'}",
        "",
        "## Paths",
        f"- Weekly summary path: {weekly_path if weekly_path.exists() else 'not generated yet'}",
        f"- Disagreement report path: {disagreement_path if disagreement_path.exists() else 'not generated yet'}",
        f"- Intent bias report path: {intent_bias_path if intent_bias_path.exists() else 'not generated yet'}",
    ]
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return index_path
