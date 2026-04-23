import sys
from collections import Counter
from datetime import date
from pathlib import Path

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

INTENTS = ["attention_like", "food_like", "playful", "curious", "unsettled", "sleepy", "unknown"]


def analyze_rows(rows):
    analysis_cache = {}
    enriched = []
    for row in rows:
        recording_id = row["recording_id"]
        if recording_id not in analysis_cache:
            analysis_cache[recording_id] = analyze(dict(row))
        result = analysis_cache[recording_id]
        enriched.append(
            {
                "recording_id": recording_id,
                "labeled_tendency": row["primary_tendency"] or "unknown",
                "inferred_tendency": result["primaryIntent"],
                "clip_quality": row["clip_quality"] or "unknown",
                "labeler_confidence": row["labeler_confidence"] or "unknown",
                "time_bucket": row["time_bucket"] or "unknown",
                "meal_context": row["meal_context"] or "unknown",
                "owner_context": row["owner_context"] or "unknown",
                "environment_trigger": row["environment_trigger"] or "unknown",
                "activity_context": row["activity_context"] or "unknown",
                "location_context": row["location_context"] or "unknown",
                "reasons": result["reasons"],
            }
        )
    return enriched


def distribution_stats(rows):
    total = len(rows)
    labeled = Counter(row["labeled_tendency"] for row in rows)
    inferred = Counter(row["inferred_tendency"] for row in rows)
    stats = []
    for intent in INTENTS:
        labeled_count = labeled.get(intent, 0)
        inferred_count = inferred.get(intent, 0)
        labeled_ratio = (labeled_count / total) if total else 0
        inferred_ratio = (inferred_count / total) if total else 0
        gap_count = inferred_count - labeled_count
        gap_ratio = inferred_ratio - labeled_ratio
        relative_gap = (gap_count / labeled_count) if labeled_count else (1.0 if inferred_count else 0.0)
        stats.append(
            {
                "intent": intent,
                "labeled_count": labeled_count,
                "inferred_count": inferred_count,
                "labeled_ratio": labeled_ratio,
                "inferred_ratio": inferred_ratio,
                "gap_count": gap_count,
                "gap_ratio": gap_ratio,
                "relative_gap": relative_gap,
            }
        )
    return stats


def flagged_rows(rows):
    flagged = []
    for row in rows:
        if row["labeled_tendency"] != row["inferred_tendency"]:
            flagged.append(row)
            continue
        if row["clip_quality"] in {"noisy", "unusable"}:
            flagged.append(row)
            continue
        if row["labeler_confidence"] == "low":
            flagged.append(row)
            continue
        if row["inferred_tendency"] == "unknown":
            flagged.append(row)
    return flagged


def representation_groups(stats):
    overrepresented = [item for item in stats if item["gap_count"] > 0]
    underrepresented = [item for item in stats if item["gap_count"] < 0]
    overrepresented.sort(key=lambda item: (-item["gap_count"], -item["gap_ratio"]))
    underrepresented.sort(key=lambda item: (item["gap_count"], item["gap_ratio"]))
    return overrepresented[:4], underrepresented[:4]


def cautious_observations(rows, stats, flagged):
    observations = []
    inferred = Counter(row["inferred_tendency"] for row in rows)
    context_clusters = top_context_clusters(flagged, limit=4)
    reason_clusters = top_reason_clusters(flagged, limit=4)

    if inferred.get("sleepy", 0):
        sleepy_rows = [row for row in rows if row["inferred_tendency"] == "sleepy"]
        sleepy_contexts = Counter()
        for row in sleepy_rows:
            for field in ("location_context", "activity_context"):
                if row[field] and row[field] != "unknown":
                    sleepy_contexts[row[field]] += 1
        top_sleepy = ", ".join(f"{name} ({count})" for name, count in sleepy_contexts.most_common(2))
        if top_sleepy:
            observations.append(f"Sleepy may be receiving repeated support from {top_sleepy} style contexts.")

    unknown_flagged = [row for row in flagged if row["inferred_tendency"] == "unknown" or row["labeled_tendency"] == "unknown"]
    if unknown_flagged:
        poor_quality = sum(1 for row in unknown_flagged if row["clip_quality"] in {"noisy", "unusable"})
        observations.append(
            f"Unknown rows may be driven more by clip quality than by label mismatch, with {poor_quality} of {len(unknown_flagged)} flagged unknown rows landing in noisy or unusable audio."
        )

    if context_clusters:
        text = ", ".join(f"{cluster} ({count})" for cluster, count in context_clusters[:2])
        observations.append(f"Flagged rows seem to repeat around a small set of contexts, especially {text}.")
    if reason_clusters:
        text = ", ".join(f"{reason} ({count})" for reason, count in reason_clusters[:2])
        observations.append(f"A few heuristic reasons appear repeatedly in flagged rows, including {text}.")

    return observations[:4]


def recommendation(health, stats, flagged):
    total = health["total"]
    if total < 20 or health["distinct_contexts"]["environment_trigger"] < 3 or health["distinct_contexts"]["location_context"] < 3:
        return "collect more data first"

    big_gap = any(abs(item["gap_ratio"]) >= 0.15 for item in stats)
    poor_quality_ratio = (
        (health["quality"].get("noisy", 0) + health["quality"].get("unusable", 0)) / total if total else 0
    )
    if big_gap and poor_quality_ratio < 0.25:
        return "tune now"
    if big_gap:
        return "mixed: small tuning + more data"
    if flagged:
        return "mixed: small tuning + more data"
    return "collect more data first"


def render_markdown(report_date, rows):
    health = compute_dataset_health(rows)
    enriched = analyze_rows(rows)
    stats = distribution_stats(enriched)
    flagged = flagged_rows(enriched)
    overrepresented, underrepresented = representation_groups(stats)
    context_clusters = top_context_clusters(flagged, limit=8)
    reason_clusters = top_reason_clusters(flagged, limit=8)
    observations = cautious_observations(enriched, stats, flagged)
    next_step = recommendation(health, stats, flagged)

    lines = [
        f"# Intent Bias Report - {report_date}",
        "",
        "## Executive Snapshot",
        f"- Rows inspected: {health['total']}",
        f"- Flagged comparison rows: {len(flagged)}",
        f"- Suggested next step: {next_step}",
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
        "## Intent Distribution Gaps",
    ]

    for item in stats:
        lines.append(
            f"- {item['intent']}: labeled={item['labeled_count']} ({item['labeled_ratio']:.1%}), "
            f"inferred={item['inferred_count']} ({item['inferred_ratio']:.1%}), "
            f"gap={item['gap_count']} ({item['gap_ratio']:+.1%})"
        )

    lines.extend(["", "## Overrepresented Inferred Intents"])
    if overrepresented:
        for item in overrepresented:
            lines.append(
                f"- {item['intent']}: inference runs {item['gap_count']} row(s) above labels, which may suggest a mild heuristic lean."
            )
    else:
        lines.append("- No inferred intent currently looks overrepresented against the labeled distribution.")

    lines.extend(["", "## Underrepresented Inferred Intents"])
    if underrepresented:
        for item in underrepresented:
            lines.append(
                f"- {item['intent']}: inference runs {abs(item['gap_count'])} row(s) below labels, which may suggest caution before treating it as a strong signal."
            )
    else:
        lines.append("- No inferred intent currently looks underrepresented against the labeled distribution.")

    lines.extend(["", "## Top Recurring Reasons In Flagged Rows"])
    if reason_clusters:
        for reason, count in reason_clusters:
            lines.append(f"- {reason}: {count}")
    else:
        lines.append("- No recurring reason pattern stands out yet in flagged rows.")

    lines.extend(["", "## Top Recurring Contexts In Flagged Rows"])
    if context_clusters:
        for cluster, count in context_clusters:
            lines.append(f"- {cluster}: {count}")
    else:
        lines.append("- No recurring context cluster stands out yet in flagged rows.")

    lines.extend(["", "## Cautious Observations"])
    if observations:
        for observation in observations:
            lines.append(f"- {observation}")
    else:
        lines.append("- The current dataset may still be too even to support a stronger observation.")

    lines.extend(["", "## Recommendation"])
    lines.append(f"- {next_step}")

    return "\n".join(lines) + "\n"


def main():
    rows = load_vocalization_rows()
    if not rows:
        print("No logs found.")
        return

    report_date = date.today().isoformat()
    markdown = render_markdown(report_date, rows)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"intent_bias_report_{report_date}.md"
    out_path.write_text(markdown, encoding="utf-8")
    index_path = update_reports_index(report_date)

    print("=" * 55)
    print("  Intent Bias Report")
    print("=" * 55)
    print(f"Rows inspected: {len(rows)}")
    print(f"Markdown report: {out_path}")
    print(f"Reports index: {index_path}")


if __name__ == "__main__":
    main()
