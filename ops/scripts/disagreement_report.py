import csv
import sys
from collections import Counter
from datetime import date
from pathlib import Path

# local_analysis.py lives in the same directory
sys.path.insert(0, str(Path(__file__).parent))
from local_analysis import analyze
from report_utils import (
    REPORTS_DIR,
    compute_dataset_health,
    load_vocalization_rows,
    ratio_text,
    top_context_clusters,
    top_reason_clusters,
    update_reports_index,
)

ROOT = Path(__file__).parent.parent.parent
CSV_PATH = ROOT / "data" / "exports" / "disagreement_rows.csv"

CSV_HEADERS = [
    "recording_id",
    "created_at",
    "labeled_tendency",
    "inferred_tendency",
    "analysis_confidence",
    "clip_quality",
    "time_bucket",
    "meal_context",
    "owner_context",
    "environment_trigger",
    "activity_context",
    "location_context",
    "top_reasons",
    "note",
    "disagreement_type",
    "review_priority",
]


def analyze_with_cache(row, cache):
    recording_id = row["recording_id"]
    if recording_id not in cache:
        cache[recording_id] = analyze(dict(row))
    return cache[recording_id]


def classify_row(row, analysis, dominant_labels):
    labeled = row["primary_tendency"] or "unknown"
    inferred = analysis["primaryIntent"]
    analysis_conf = analysis["confidenceBand"]
    clip_quality = row["clip_quality"] or "unknown"
    label_conf = row["labeler_confidence"] or "unknown"
    reasons = analysis["reasons"]

    mismatch = labeled != inferred
    any_unknown = labeled == "unknown" or inferred == "unknown"
    weak_signal = clip_quality in {"noisy", "unusable"} or analysis_conf == "low" or label_conf == "low"
    strong_signal = analysis_conf in {"medium", "high"} and clip_quality == "clean"

    disagreement_type = None

    if mismatch and labeled in dominant_labels and inferred != "unknown" and analysis_conf in {"medium", "high"}:
        disagreement_type = "overdominance_candidate"
    elif mismatch and not any_unknown:
        disagreement_type = "hard_mismatch"
    elif any_unknown and clip_quality == "unusable":
        disagreement_type = "unknown_unusable"
    elif any_unknown and clip_quality == "noisy":
        disagreement_type = "unknown_noisy"
    elif any_unknown:
        disagreement_type = "unknown_clean"
    elif labeled == inferred and weak_signal:
        disagreement_type = "fragile_match"

    if disagreement_type is None:
        return None, None, "; ".join(reasons[:4])

    review_priority = "low"

    if disagreement_type == "hard_mismatch":
        review_priority = "high" if strong_signal or label_conf in {"medium", "high"} else "medium"
    elif disagreement_type in {"unknown_unusable", "unknown_noisy", "unknown_clean"}:
        review_priority = "high" if clip_quality == "clean" and analysis_conf in {"medium", "high"} else "medium"
    elif disagreement_type == "overdominance_candidate":
        review_priority = "medium" if clip_quality != "unusable" else "low"
    elif disagreement_type == "fragile_match":
        review_priority = "medium" if clip_quality == "clean" and analysis_conf == "low" else "low"

    return disagreement_type, review_priority, "; ".join(reasons[:4])


def enrich_rows(raw_rows):
    labeled_counts = Counter(row["primary_tendency"] or "unknown" for row in raw_rows)
    if labeled_counts:
        top_count = labeled_counts.most_common(1)[0][1]
        dominant_labels = {
            label
            for label, count in labeled_counts.items()
            if label != "unknown" and count >= max(2, top_count)
        }
    else:
        dominant_labels = set()

    analysis_cache = {}
    enriched = []
    for row in raw_rows:
        analysis = analyze_with_cache(row, analysis_cache)
        disagreement_type, review_priority, top_reasons = classify_row(row, analysis, dominant_labels)
        if disagreement_type is None:
            continue
        enriched.append(
            {
                "recording_id": row["recording_id"],
                "created_at": row["created_at"],
                "labeled_tendency": row["primary_tendency"] or "unknown",
                "inferred_tendency": analysis["primaryIntent"],
                "analysis_confidence": analysis["confidenceBand"],
                "clip_quality": row["clip_quality"] or "unknown",
                "time_bucket": row["time_bucket"] or "unknown",
                "meal_context": row["meal_context"] or "unknown",
                "owner_context": row["owner_context"] or "unknown",
                "environment_trigger": row["environment_trigger"] or "unknown",
                "activity_context": row["activity_context"] or "unknown",
                "location_context": row["location_context"] or "unknown",
                "reasons": analysis["reasons"],
                "top_reasons": top_reasons,
                "note": row["note"] or "",
                "disagreement_type": disagreement_type,
                "review_priority": review_priority,
            }
        )

    return enriched, dominant_labels, len(raw_rows), analysis_cache


def export_csv(rows):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in CSV_HEADERS} for row in rows)


def top_mismatch_pairs(rows):
    pairs = Counter()
    for row in rows:
        if row["labeled_tendency"] != row["inferred_tendency"]:
            key = f"{row['labeled_tendency']} -> {row['inferred_tendency']}"
            pairs[key] += 1
    return pairs.most_common(5)


def cluster_contexts(rows):
    return top_context_clusters([row for row in rows if row["review_priority"] != "low"], limit=8)


def cluster_reasons(rows):
    return top_reason_clusters([row for row in rows if row["review_priority"] != "low"], limit=8)


def executive_snapshot(rows, inspected_total):
    total = len(rows)
    by_type = Counter(row["disagreement_type"] for row in rows)
    by_priority = Counter(row["review_priority"] for row in rows)
    mismatches = sum(1 for row in rows if row["labeled_tendency"] != row["inferred_tendency"])
    return {
        "inspected_total": inspected_total,
        "flagged_total": total,
        "mismatches": mismatches,
        "by_type": by_type,
        "by_priority": by_priority,
    }


def high_priority_rows(rows):
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(
        [row for row in rows if row["review_priority"] == "high"],
        key=lambda row: (order[row["review_priority"]], row["created_at"]),
        reverse=True,
    )[:6]


def tuning_suggestions(rows, mismatch_pairs, context_clusters, reason_clusters):
    suggestions = []

    hard_mismatch_count = sum(1 for row in rows if row["disagreement_type"] == "hard_mismatch")
    unknown_pressure_count = sum(
        1 for row in rows if row["disagreement_type"] in {"unknown_unusable", "unknown_noisy", "unknown_clean"}
    )
    unknown_clean_count = sum(1 for row in rows if row["disagreement_type"] == "unknown_clean")

    if hard_mismatch_count:
        suggestions.append(
            f"Hard mismatches appear often enough ({hard_mismatch_count} row(s)) that a few label definitions may need a gentler pass for consistency."
        )
    if mismatch_pairs:
        top_pair, count = mismatch_pairs[0]
        suggestions.append(
            f"The pair `{top_pair}` shows up most often ({count} row(s)), which might be a useful place to compare notes before tuning anything broader."
        )
    if context_clusters:
        cluster, count = context_clusters[0]
        suggestions.append(
            f"The context cluster `{cluster}` appears repeatedly in review rows ({count} hits), so that context may be worth watching more closely."
        )
    if reason_clusters:
        reason, count = reason_clusters[0]
        suggestions.append(
            f"The reason `{reason}` comes up often in flagged rows ({count} times), which could mean that signal is doing more work than expected."
        )
    if unknown_pressure_count:
        suggestions.append(
            f"Unknown rows may be driven more by clip quality than by label mismatch right now, with {unknown_pressure_count} flagged unknown row(s)."
        )
    if unknown_clean_count:
        suggestions.append(
            f"{unknown_clean_count} clean unknown row(s) may be the clearest place to check whether the heuristic needs a small adjustment."
        )

    return suggestions[:4]


def observation_lines(rows):
    observations = []
    by_inferred = Counter(row["inferred_tendency"] for row in rows)
    context_text = ", ".join(f"{cluster} ({count})" for cluster, count in cluster_contexts(rows)[:2])
    reason_text = ", ".join(f"{reason} ({count})" for reason, count in cluster_reasons(rows)[:2])

    if by_inferred.get("unknown", 0):
        observations.append("Unknown rows may be driven more by clip quality than by label mismatch in this pass.")
    if by_inferred.get("sleepy", 0):
        observations.append("Sleepy may be receiving repeated support from bed and resting style contexts when those appear together.")
    if context_text:
        observations.append(f"Flagged rows seem to cluster around a small set of contexts: {context_text}.")
    if reason_text:
        observations.append(f"A few reasons appear repeatedly in flagged rows: {reason_text}.")

    return observations[:4]


def render_markdown(report_date, rows, inspected_total, raw_rows):
    snapshot = executive_snapshot(rows, inspected_total)
    health = compute_dataset_health(raw_rows)
    mismatch_pairs = top_mismatch_pairs(rows)
    priority_rows = high_priority_rows(rows)
    context_clusters = cluster_contexts(rows)
    reason_clusters = cluster_reasons(rows)
    suggestions = tuning_suggestions(rows, mismatch_pairs, context_clusters, reason_clusters)
    observations = observation_lines(rows)

    lines = [
        f"# Disagreement Report - {report_date}",
        "",
        "## Executive Snapshot",
        f"- Rows inspected: {snapshot['inspected_total']}",
        f"- Flagged review rows: {snapshot['flagged_total']}",
        f"- Labeled vs inferred mismatches among flagged rows: {snapshot['mismatches']}",
        f"- High priority rows: {snapshot['by_priority'].get('high', 0)}",
        f"- Medium priority rows: {snapshot['by_priority'].get('medium', 0)}",
        f"- Low priority rows: {snapshot['by_priority'].get('low', 0)}",
        f"- hard_mismatch: {snapshot['by_type'].get('hard_mismatch', 0)}",
        f"- fragile_match: {snapshot['by_type'].get('fragile_match', 0)}",
        f"- unknown_unusable: {snapshot['by_type'].get('unknown_unusable', 0)}",
        f"- unknown_noisy: {snapshot['by_type'].get('unknown_noisy', 0)}",
        f"- unknown_clean: {snapshot['by_type'].get('unknown_clean', 0)}",
        f"- overdominance_candidate: {snapshot['by_type'].get('overdominance_candidate', 0)}",
        "",
        "## Dataset Health",
        f"- Total rows: {health['total']}",
        f"- Clean ratio: {ratio_text(health['quality'].get('clean', 0), health['total'])}",
        f"- Noisy ratio: {ratio_text(health['quality'].get('noisy', 0), health['total'])}",
        f"- Unusable ratio: {ratio_text(health['quality'].get('unusable', 0), health['total'])}",
        f"- Low confidence ratio: {ratio_text(health['confidence'].get('low', 0), health['total'])}",
        f"- Medium confidence ratio: {ratio_text(health['confidence'].get('medium', 0), health['total'])}",
        f"- High confidence ratio: {ratio_text(health['confidence'].get('high', 0), health['total'])}",
        f"- Unknown ratio: {ratio_text(health['unknown_count'], health['total'])}",
        f"- Distinct time_bucket values: {health['distinct_contexts']['time_bucket']}",
        f"- Distinct meal_context values: {health['distinct_contexts']['meal_context']}",
        f"- Distinct owner_context values: {health['distinct_contexts']['owner_context']}",
        f"- Distinct environment_trigger values: {health['distinct_contexts']['environment_trigger']}",
        f"- Distinct activity_context values: {health['distinct_contexts']['activity_context']}",
        f"- Distinct location_context values: {health['distinct_contexts']['location_context']}",
        "",
        "## Top Mismatch Pairs",
    ]

    if mismatch_pairs:
        for pair, count in mismatch_pairs:
            lines.append(f"- {pair}: {count}")
    else:
        lines.append("- No mismatch pairs stood out in this pass; most rows seem to line up with the current heuristic.")

    lines.extend(["", "## High-Priority Review Rows"])
    if priority_rows:
        for row in priority_rows:
            lines.append(
                f"- {row['recording_id']}: labeled={row['labeled_tendency']}, inferred={row['inferred_tendency']}, "
                f"type={row['disagreement_type']}, reasons={row['top_reasons'] or 'none noted'}"
            )
    else:
        lines.append("- No rows reached high priority in this pass; the current set may mostly need lighter monitoring.")

    lines.extend(["", "## Context Clusters"])
    if context_clusters:
        for cluster, count in context_clusters:
            lines.append(f"- {cluster}: {count}")
    else:
        lines.append("- No repeated context cluster clearly stood out beyond the background mix.")

    lines.extend(["", "## Reason Clusters"])
    if reason_clusters:
        for reason, count in reason_clusters:
            lines.append(f"- {reason}: {count}")
    else:
        lines.append("- No repeated reason cluster clearly stood out in flagged rows.")

    lines.extend(["", "## Cautious Observations"])
    if observations:
        for observation in observations:
            lines.append(f"- {observation}")
    else:
        lines.append("- No cautious observation stands out yet beyond the current flagged rows.")

    lines.extend(["", "## Tuning Suggestions"])
    if suggestions:
        for suggestion in suggestions:
            lines.append(f"- {suggestion}")
    else:
        lines.append("- The current disagreement layer does not yet suggest a clear tuning move; a little more data may help.")

    return "\n".join(lines) + "\n"


def save_markdown(report_date, content):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"disagreement_report_{report_date}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def print_console_summary(rows, inspected_total, report_path):
    snapshot = executive_snapshot(rows, inspected_total)
    print("=" * 55)
    print("  Disagreement Report")
    print("=" * 55)
    print(f"Rows inspected: {snapshot['inspected_total']}")
    print(f"Flagged review rows: {snapshot['flagged_total']}")
    print(f"Mismatches: {snapshot['mismatches']}")
    print(f"High priority: {snapshot['by_priority'].get('high', 0)}")
    print(f"Medium priority: {snapshot['by_priority'].get('medium', 0)}")
    print(f"Low priority: {snapshot['by_priority'].get('low', 0)}")
    print(f"CSV export: {CSV_PATH}")
    print(f"Markdown report: {report_path}")


def main():
    raw_rows = load_vocalization_rows()
    if not raw_rows:
        print("No logs found.")
        return

    rows, _dominant_labels, inspected_total, _analysis_cache = enrich_rows(raw_rows)
    export_csv(rows)

    report_date = date.today().isoformat()
    markdown = render_markdown(report_date, rows, inspected_total, raw_rows)
    report_path = save_markdown(report_date, markdown)
    update_reports_index(report_date)
    print_console_summary(rows, inspected_total, report_path)


if __name__ == "__main__":
    main()
