import json
from collections import Counter
from pathlib import Path

MANIFEST_PATH = Path("reference_corpus") / "manifest.json"
OUT_PATH = Path("reference_corpus") / "eval_subset.generated.json"
VIEW_ONLY_SOURCE_TYPES = {"social_video", "youtube_video", "web_video", "youtube_audio"}


def load_items(path):
    with open(path, encoding="utf-8") as handle:
        parsed = json.load(handle)

    if not isinstance(parsed, dict) or not isinstance(parsed.get("items"), list):
        raise ValueError("Manifest must be an object containing an 'items' list.")
    return parsed["items"]


def exclusion_reasons(item):
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


def main():
    items = load_items(MANIFEST_PATH)
    included = []
    excluded = []
    exclusion_counts = Counter()

    for item in items:
        reasons = exclusion_reasons(item)
        if reasons:
            excluded.append((item, reasons))
            exclusion_counts.update(reasons)
        else:
            included.append(item)

    payload = {
        "generated_from": str(MANIFEST_PATH),
        "generated_item_count": len(included),
        "items": included,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("=" * 60)
    print("  Build Eval Subset")
    print("=" * 60)
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Output: {OUT_PATH}")
    print(f"Included: {len(included)}")
    print(f"Excluded: {len(excluded)}")

    print("\nTop exclusion reasons")
    if not exclusion_counts:
        print("  none")
    else:
        for reason, count in exclusion_counts.most_common():
            print(f"  {reason}: {count}")


if __name__ == "__main__":
    main()
