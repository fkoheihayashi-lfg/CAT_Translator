import json
from collections import Counter
from pathlib import Path

MANIFEST_PATH = Path("reference_corpus") / "manifest.json"
VIEW_ONLY_SOURCE_TYPES = {"social_video", "youtube_video", "web_video", "youtube_audio"}
UNCLEAR_LICENSES = {"unclear", "unknown", "needs_review", "view_only", "dataset_restricted"}


def load_items(path):
    with open(path, encoding="utf-8") as handle:
        parsed = json.load(handle)

    if not isinstance(parsed, dict) or not isinstance(parsed.get("items"), list):
        raise ValueError("Manifest must be an object containing an 'items' list.")
    return parsed["items"]


def blocker_reasons(item):
    reasons = []
    if item.get("verification_status") != "verified":
        reasons.append("not_verified")
    if item.get("decision") != "eval_ready":
        reasons.append("not_eval_ready")
    if not item.get("local_path"):
        reasons.append("no_local_path")
    if item.get("audio_reuse_ok") is not True:
        reasons.append("audio_reuse_not_yes")
    if item.get("age_group") != "adult":
        reasons.append("age_group_not_adult")
    if item.get("interaction_type") == "mother_kitten":
        reasons.append("interaction_type_mother_kitten")
    if item.get("context_certainty") == "low":
        reasons.append("context_certainty_low")
    if item.get("license_status") in UNCLEAR_LICENSES:
        reasons.append("unclear_license")
    if item.get("source_type") in VIEW_ONLY_SOURCE_TYPES:
        reasons.append("view_only_source")
    return reasons


def main():
    items = load_items(MANIFEST_PATH)
    blocked = []
    blocker_counts = Counter()

    for item in items:
        reasons = blocker_reasons(item)
        if reasons:
            blocked.append(item)
            blocker_counts.update(reasons)

    print("=" * 60)
    print("  Explain Eval Blockers")
    print("=" * 60)
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Blocked items: {len(blocked)}")

    print("\nPer-item blockers")
    if not blocked:
        print("  none")
    else:
        for item in blocked:
            reasons = blocker_reasons(item)
            print(
                f"  {item.get('source_id', '?')}: "
                f"decision={item.get('decision', 'missing')}, "
                f"verification_status={item.get('verification_status', 'missing')} "
                f"[{', '.join(dict.fromkeys(reasons))}]"
            )

    print("\nGrouped blocker reasons")
    if not blocker_counts:
        print("  none")
    else:
        for reason, count in blocker_counts.most_common():
            print(f"  {reason}: {count}")


if __name__ == "__main__":
    main()
