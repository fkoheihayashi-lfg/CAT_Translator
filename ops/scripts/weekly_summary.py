import argparse
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

# local_analysis.py lives in the same directory
sys.path.insert(0, str(Path(__file__).parent))
from local_analysis import analyze

ROOT = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "data" / "vocalizations.db"
REPORTS_DIR = ROOT / "ops" / "reports"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Summarize recent vocalization logs and save a Markdown weekly report."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="How many trailing days to include from created_at (default: 7).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ignore the date window and summarize all rows.",
    )
    parser.add_argument(
        "--report-date",
        default=date.today().isoformat(),
        help="Date to use in the Markdown filename (default: today).",
    )
    return parser.parse_args()


def load_rows(days, include_all):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    base_query = """
        SELECT recording_id, created_at, primary_tendency, labeler_confidence,
               clip_quality, duration_ms, time_bucket, meal_context,
               owner_context, environment_trigger, activity_context,
               location_context, note
        FROM vocalizations
    """

    if include_all:
        raw_rows = con.execute(f"{base_query} ORDER BY datetime(created_at) DESC").fetchall()
    else:
        raw_rows = con.execute(
            f"""
            {base_query}
            WHERE datetime(created_at) >= datetime('now', ?)
            ORDER BY datetime(created_at) DESC
            """,
            (f"-{days} days",),
        ).fetchall()

    con.close()
    return raw_rows


def collect_stats(raw_rows):
    total = len(raw_rows)
    labeled_tendency = Counter(r["primary_tendency"] or "unknown" for r in raw_rows)
    quality = Counter(r["clip_quality"] or "unknown" for r in raw_rows)
    labeled_conf = Counter(r["labeler_confidence"] or "unknown" for r in raw_rows)
    unknown_count = labeled_tendency.get("unknown", 0)
    unknown_ratio = (unknown_count / total) if total else 0

    enriched = []
    all_reasons = []

    for r in raw_rows:
        result = analyze(dict(r))
        enriched.append(
            {
                "recording_id": r["recording_id"],
                "created_at": r["created_at"],
                "labeled": r["primary_tendency"] or "unknown",
                "labeler_confidence": r["labeler_confidence"] or "unknown",
                "clip_quality": r["clip_quality"] or "unknown",
                "location_context": r["location_context"],
                "activity_context": r["activity_context"],
                "owner_context": r["owner_context"],
                "meal_context": r["meal_context"],
                "time_bucket": r["time_bucket"],
                "note": r["note"] or "",
                "inferred": result["primaryIntent"],
                "inferred_conf": result["confidenceBand"],
                "reasons": result["reasons"],
            }
        )
        all_reasons.extend(result["reasons"])

    inferred_tendency = Counter(r["inferred"] for r in enriched)
    top_reasons = Counter(all_reasons)
    agreed = sum(1 for r in enriched if r["inferred"] == r["labeled"])
    diverged = total - agreed
    agree_pct = (agreed / total) if total else 0

    return {
        "total": total,
        "labeled_tendency": labeled_tendency,
        "quality": quality,
        "labeled_conf": labeled_conf,
        "unknown_count": unknown_count,
        "unknown_ratio": unknown_ratio,
        "enriched": enriched,
        "inferred_tendency": inferred_tendency,
        "top_reasons": top_reasons,
        "agreed": agreed,
        "diverged": diverged,
        "agree_pct": agree_pct,
    }


def _context_patterns(enriched):
    pattern_counts = Counter()

    for row in enriched:
        if row["location_context"] and row["location_context"] != "unknown":
            pattern_counts[f"location={row['location_context']}"] += 1
        if row["activity_context"] and row["activity_context"] != "unknown":
            pattern_counts[f"activity={row['activity_context']}"] += 1
        if row["meal_context"] and row["meal_context"] != "unknown":
            pattern_counts[f"meal={row['meal_context']}"] += 1
        if row["time_bucket"] and row["time_bucket"] != "unknown":
            pattern_counts[f"time={row['time_bucket']}"] += 1

    return pattern_counts.most_common(5)


def _pattern_observations(enriched):
    observations = []

    by_location = defaultdict(list)
    for row in enriched:
        if row["location_context"] and row["location_context"] != "unknown":
            by_location[row["location_context"]].append(row["inferred"])

    for loc, intents in sorted(by_location.items(), key=lambda item: -len(item[1])):
        if len(intents) < 2:
            continue
        top, count = Counter(intents).most_common(1)[0]
        ratio = count / len(intents)
        if ratio >= 0.67 and top != "unknown":
            observations.append(
                f"{count} of {len(intents)} clips around {loc.replace('_', ' ')} lean {top.replace('_', ' ')}."
            )

    by_activity = defaultdict(list)
    for row in enriched:
        if row["activity_context"] and row["activity_context"] != "unknown":
            by_activity[row["activity_context"]].append(row["inferred"])

    for activity, intents in sorted(by_activity.items(), key=lambda item: -len(item[1])):
        if len(intents) < 2:
            continue
        top, count = Counter(intents).most_common(1)[0]
        ratio = count / len(intents)
        if ratio >= 0.67 and top != "unknown":
            observations.append(
                f"{count} of {len(intents)} {activity.replace('_', ' ')} clips read as {top.replace('_', ' ')}."
            )

    return observations[:3]


def _summary_sentences(labeled_tendency, quality, total, unknown_ratio, agree_pct):
    sentences = []
    top_labeled, top_n = labeled_tendency.most_common(1)[0]
    top_pct = top_n / total
    top_label = top_labeled.replace("_", " ")

    if top_labeled != "unknown" and top_pct >= 0.3:
        sentences.append(
            f"This week's logs lean most often toward {top_label}, showing up in {top_n} of {total} clips."
        )
    else:
        sentences.append(
            f"This week's logs feel fairly mixed, with {top_label} appearing slightly more often than the rest."
        )

    if agree_pct >= 0.85:
        sentences.append(
            f"The local analysis generally lines up with manual labels, which suggests the logged context is holding together reasonably well."
        )
    elif agree_pct >= 0.6:
        sentences.append(
            f"The local analysis and manual labels line up often enough to be useful, though a few recordings may deserve a second look."
        )
    else:
        sentences.append(
            f"The local analysis and manual labels part ways fairly often right now, which may mean some clips need richer context notes."
        )

    clean_pct = quality.get("clean", 0) / total
    if clean_pct >= 0.8:
        sentences.append("Clip quality looks steady overall, with most recordings staying clean enough for quick review.")
    elif clean_pct >= 0.5:
        sentences.append("Clip quality looks usable overall, though some noisier recordings may still slow down labeling.")
    else:
        sentences.append("Clip quality looks a bit uneven this week, so recording conditions may be worth watching more closely.")

    if unknown_ratio >= 0.3:
        sentences[0] = (
            f"A noticeable share of this week's clips still sit in unknown, so the dataset may still be in a clarification phase."
        )

    return sentences[:3]


def _quality_notes(quality, labeled_conf, unknown_ratio, total):
    notes = []

    if quality.get("unusable", 0) > 0:
        notes.append(f"{quality['unusable']} clip(s) were marked unusable, so those likely add noise more than signal.")
    if quality.get("noisy", 0) > 0:
        notes.append(f"{quality['noisy']} clip(s) were marked noisy, which may be softening confidence on nearby labels.")
    if total and (labeled_conf.get("low", 0) / total) > 0.2:
        notes.append(f"{labeled_conf['low']} clip(s) carry low label confidence, so the review queue may stay active.")
    if unknown_ratio > 0.25:
        notes.append("Unknown labels are still a meaningful slice of the set, so interpretation should stay tentative.")

    return notes[:3]


def _watch_next(labeled_tendency, inferred_tendency, quality, enriched):
    watches = []

    if labeled_tendency.get("unknown", 0) > 0:
        watches.append("Watch whether unknown clips start clustering around one context or time bucket.")

    diverged_rows = [
        row for row in enriched if row["inferred"] != row["labeled"] and row["inferred"] != "unknown"
    ]
    if diverged_rows:
        watches.append(
            f"Watch the {len(diverged_rows)} clip(s) where analysis and labels diverged to see whether a repeat pattern emerges."
        )

    for label in ("unsettled", "curious", "attention_like"):
        if max(labeled_tendency.get(label, 0), inferred_tendency.get(label, 0)) >= 2:
            watches.append(f"Watch for more {label.replace('_', ' ')} clips to see if the pattern keeps repeating.")

    if quality.get("unusable", 0) > 0:
        watches.append("Watch the unusable rate in case a mic position or room condition is getting in the way.")

    if not watches:
        watches.append("Nothing stands out strongly yet; steady logging should make next week's comparisons more useful.")

    return watches[:3]


def print_console_summary(stats, patterns, pattern_observations, summary_sentences, quality_notes, watch_items):
    print("=" * 55)
    print("  Weekly Summary")
    print("=" * 55)
    print(f"\nTotal logs: {stats['total']}")

    print("\n-- Labeled Tendencies --")
    for key, value in stats["labeled_tendency"].most_common():
        print(f"  {key}: {value}")

    print(f"\n  unknown: {stats['unknown_count']}  ({stats['unknown_ratio']:.1%} of logs)")

    print("\n-- Clip Quality --")
    for key, value in stats["quality"].most_common():
        print(f"  {key}: {value}")

    print("\n-- Labeler Confidence --")
    for key, value in stats["labeled_conf"].most_common():
        print(f"  {key}: {value}")

    print("\n-- Analysis (local_heuristic) --")
    print(f"  Ran on {stats['total']} rows")
    print(f"  Label ↔ Analysis agreement: {stats['agreed']}/{stats['total']} ({stats['agree_pct']:.0%})")
    if stats["diverged"]:
        print(f"  Diverged: {stats['diverged']} clip(s)")

    print("\n-- Top Recurring Reasons --")
    for reason, count in stats["top_reasons"].most_common(6):
        print(f"  {reason}: {count}")

    print("\n-- Top Context Patterns --")
    for pattern, count in patterns[:5]:
        print(f"  {pattern}: {count}")
    for observation in pattern_observations:
        print(f"  {observation}")

    print("\n-- This Week --")
    for sentence in summary_sentences:
        print(f"  {sentence}")

    if quality_notes:
        print("\n-- Data Quality Notes --")
        for note in quality_notes:
            print(f"  {note}")

    print("\n-- Things to Watch Next Week --")
    for item in watch_items:
        print(f"  {item}")


def render_markdown(report_date, stats, patterns, summary_sentences, quality_notes, watch_items):
    lines = [
        f"# Weekly Summary - {report_date}",
        "",
        f"- Total logs: {stats['total']}",
        f"- Unknown: {stats['unknown_count']} ({stats['unknown_ratio']:.1%})",
        "",
        "## Count by Primary Tendency",
    ]

    for key, value in stats["labeled_tendency"].most_common():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Count by Clip Quality"])
    for key, value in stats["quality"].most_common():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Count by Labeler Confidence"])
    for key, value in stats["labeled_conf"].most_common():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Analysis Agreement",
            f"- Agreement: {stats['agreed']}/{stats['total']} ({stats['agree_pct']:.0%})",
            f"- Diverged: {stats['diverged']}",
        ]
    )

    if stats["diverged"]:
        lines.append("- Divergence is interpretive only and may reflect thin context rather than a true mismatch.")

    lines.extend(["", "## Top Recurring Reasons"])
    for reason, count in stats["top_reasons"].most_common(6):
        lines.append(f"- {reason}: {count}")

    lines.extend(["", "## Top Context Patterns"])
    for pattern, count in patterns[:5]:
        lines.append(f"- {pattern}: {count}")

    lines.extend(["", "## Weekly Readout"])
    for sentence in summary_sentences:
        lines.append(f"- {sentence}")

    lines.extend(["", "## Data Quality Notes"])
    if quality_notes:
        for note in quality_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- No immediate data quality notes stood out this week.")

    lines.extend(["", "## Things to Watch Next Week"])
    for item in watch_items:
        lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def save_markdown(report_date, content):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / f"weekly_summary_{report_date}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main():
    args = parse_args()
    raw_rows = load_rows(args.days, args.all)

    if not raw_rows:
        print("No logs found for the requested period.")
        return

    stats = collect_stats(raw_rows)
    patterns = _context_patterns(stats["enriched"])
    pattern_observations = _pattern_observations(stats["enriched"])
    summary_sentences = _summary_sentences(
        stats["labeled_tendency"],
        stats["quality"],
        stats["total"],
        stats["unknown_ratio"],
        stats["agree_pct"],
    )
    quality_notes = _quality_notes(
        stats["quality"],
        stats["labeled_conf"],
        stats["unknown_ratio"],
        stats["total"],
    )
    watch_items = _watch_next(
        stats["labeled_tendency"],
        stats["inferred_tendency"],
        stats["quality"],
        stats["enriched"],
    )

    print_console_summary(
        stats,
        patterns,
        pattern_observations,
        summary_sentences,
        quality_notes,
        watch_items,
    )

    markdown = render_markdown(
        args.report_date,
        stats,
        patterns,
        summary_sentences,
        quality_notes,
        watch_items,
    )
    out_path = save_markdown(args.report_date, markdown)
    print(f"\nSaved Markdown report to {out_path}")


if __name__ == "__main__":
    main()
