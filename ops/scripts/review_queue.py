import csv
import sqlite3
import sys
from pathlib import Path

# local_analysis.py lives in the same directory
sys.path.insert(0, str(Path(__file__).parent))
from local_analysis import analyze

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "data" / "vocalizations.db"
OUT_PATH = ROOT / "data" / "exports" / "review_queue.csv"

HEADERS = [
    "recording_id",
    "created_at",
    "recording_uri",
    "primary_tendency",
    "analysis_primary",
    "analysis_confidence",
    "labeler_confidence",
    "clip_quality",
    "review_reasons",
    "note",
]


def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT recording_id, created_at, recording_uri, duration_ms,
               clip_quality, time_bucket, meal_context, owner_context,
               environment_trigger, activity_context, location_context,
               primary_tendency, labeler_confidence, note
        FROM vocalizations
        ORDER BY datetime(created_at) DESC, recording_id DESC
        """
    ).fetchall()
    con.close()

    review_rows = []

    for row in rows:
        result = analyze(dict(row))
        reasons = []

        if row["primary_tendency"] == "unknown":
            reasons.append("primary_tendency=unknown")
        if row["labeler_confidence"] == "low":
            reasons.append("labeler_confidence=low")
        if row["clip_quality"] in {"noisy", "unusable"}:
            reasons.append(f"clip_quality={row['clip_quality']}")
        if result["primaryIntent"] != row["primary_tendency"]:
            reasons.append("analysis_diverges_from_label")

        if not reasons:
            continue

        review_rows.append(
            {
                "recording_id": row["recording_id"],
                "created_at": row["created_at"],
                "recording_uri": row["recording_uri"],
                "primary_tendency": row["primary_tendency"],
                "analysis_primary": result["primaryIntent"],
                "analysis_confidence": result["confidenceBand"],
                "labeler_confidence": row["labeler_confidence"],
                "clip_quality": row["clip_quality"],
                "review_reasons": "; ".join(reasons),
                "note": row["note"] or "",
            }
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(review_rows)

    print(f"Exported {len(review_rows)} review rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
