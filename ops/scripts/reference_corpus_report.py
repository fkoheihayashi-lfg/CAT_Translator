import json
from collections import Counter
from datetime import date
from json import JSONDecodeError
from pathlib import Path

MANIFEST_PATH = Path("reference_corpus") / "manifest.json"
EVAL_SUBSET_PATH = Path("reference_corpus") / "eval_subset.generated.json"
REPORTS_DIR = Path("ops") / "reports"
VIEW_ONLY_SOURCE_TYPES = {"social_video", "youtube_video", "web_video", "youtube_audio"}


def load_items(path):
    with open(path, encoding="utf-8") as handle:
        parsed = json.load(handle)

    if not isinstance(parsed, dict) or not isinstance(parsed.get("items"), list):
        raise ValueError("Manifest must be an object containing an 'items' list.")
    return parsed["items"]


def load_optional_subset(path):
    if not path.exists():
        return [], None
    try:
        return load_items(path), None
    except (JSONDecodeError, ValueError) as exc:
        return [], f"Eval subset could not be read cleanly: {exc}"


def block_reasons(item):
    reasons = []
    if item.get("decision") != "eval_ready":
        reasons.append("decision_not_eval_ready")
    if item.get("verification_status") != "verified":
        reasons.append("verification_not_verified")
    if item.get("audio_reuse_ok") is not True:
        reasons.append("audio_reuse_not_ok")
    if not item.get("local_path"):
        reasons.append("missing_local_path")
    if item.get("age_group") != "adult":
        reasons.append("not_adult")
    if item.get("interaction_type") == "mother_kitten":
        reasons.append("mother_kitten")
    if item.get("context_certainty") == "low":
        reasons.append("low_context_certainty")
    if item.get("source_type") in VIEW_ONLY_SOURCE_TYPES or item.get("license_status") == "view_only":
        reasons.append("view_only_source")
    return reasons


def cautious_recommendations(items, eval_subset_count, block_counts):
    recommendations = []
    provisional = sum(1 for item in items if item.get("verification_status") != "verified")
    if provisional:
        recommendations.append(
            f"{provisional} item(s) are still provisional, so verification work may matter more than adding another batch immediately."
        )
    if eval_subset_count == 0:
        recommendations.append(
            "The strict eval subset is still empty, so it may be better to verify a few adult clips before doing broader heuristic spot-checking."
        )
    if block_counts.get("verification_not_verified", 0):
        recommendations.append(
            "Verification status is still blocking several items, so a small source-review pass may unlock more value than collecting loosely."
        )
    if block_counts.get("missing_local_path", 0):
        recommendations.append(
            "Missing local files still block some items, so local file organization may be worth tightening before the next review."
        )
    if not recommendations:
        recommendations.append("The corpus looks usable for a cautious spot-check pass, but it should still stay separate from the operational DB.")
    return recommendations[:3]


def main():
    items = load_items(MANIFEST_PATH)
    eval_subset_items, subset_note = load_optional_subset(EVAL_SUBSET_PATH)
    eval_subset_count = len(eval_subset_items)

    block_counts = Counter()
    blocked_count = 0
    for item in items:
        reasons = block_reasons(item)
        if reasons:
            blocked_count += 1
            block_counts.update(reasons)

    report_date = date.today().isoformat()
    out_path = REPORTS_DIR / f"reference_corpus_report_{report_date}.md"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    decision_counts = Counter(item.get("decision") or "missing" for item in items)
    verification_counts = Counter(item.get("verification_status") or "missing" for item in items)
    age_counts = Counter(item.get("age_group") or "missing" for item in items)
    interaction_counts = Counter(item.get("interaction_type") or "missing" for item in items)
    likely_usable = sum(1 for item in items if item.get("decision") == "eval_ready" and item.get("age_group") == "adult")
    recommendations = cautious_recommendations(items, eval_subset_count, block_counts)

    lines = [
        f"# Reference Corpus Report - {report_date}",
        "",
        "## Executive Snapshot",
        f"- Total candidate count: {len(items)}",
        f"- Eval-ready count in manifest: {decision_counts.get('eval_ready', 0)}",
        f"- Verified eval subset count: {eval_subset_count}",
        f"- Blocked-for-now count: {blocked_count}",
        "",
        "## Decision Distribution",
    ]

    for key, value in decision_counts.most_common():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Verification Status Distribution"])
    for key, value in verification_counts.most_common():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Block Reasons",
            f"- Top block reasons reflect the current strict Phase 1 gate and may still be provisional rather than final quality judgments.",
        ]
    )
    if block_counts:
        for key, value in block_counts.most_common(6):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- No block reasons stood out in this pass.")

    lines.extend(["", "## Age Group / Interaction Type Split"])
    for key, value in age_counts.most_common():
        lines.append(f"- age_group={key}: {value}")
    for key, value in interaction_counts.most_common():
        lines.append(f"- interaction_type={key}: {value}")

    lines.extend(
        [
            "",
            "## Current Phase 1 Eval Posture",
            f"- Likely usable for current Phase 1 eval: {likely_usable}",
            f"- Strict generated eval subset available: {eval_subset_count}",
        ]
    )
    if subset_note:
        lines.append(f"- Eval subset note: {subset_note}")
    if eval_subset_count == 0:
        lines.append("- No item has cleared the strict verified gate yet, so the corpus still seems partly provisional.")

    lines.extend(["", "## Next-Step Recommendations"])
    for recommendation in recommendations:
        lines.append(f"- {recommendation}")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=" * 60)
    print("  Reference Corpus Report")
    print("=" * 60)
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Report: {out_path}")
    print(f"Total candidate count: {len(items)}")
    print(f"Verified eval subset count: {eval_subset_count}")
    print(f"Blocked-for-now count: {blocked_count}")
    if subset_note:
        print(subset_note)


if __name__ == "__main__":
    main()
