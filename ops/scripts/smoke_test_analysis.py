"""
Smoke tests for local_analysis.py — mirrors analyzeLocalRecording.ts test cases.
Run before Expo app is initialized to verify heuristic behavior.
"""

from local_analysis import analyze

BASE = dict(
    recording_uri='local://test.m4a',
    duration_ms=1200,
    time_bucket='morning',
    meal_context='no_food_context',
    owner_context='owner_near',
    environment_trigger='quiet',
    activity_context='resting',
    location_context='sofa',
    clip_quality='clean',
)


def run_test(label, inp, expect_primary=None, expect_confidence=None):
    result = analyze(inp)
    ok_primary = expect_primary is None or result['primaryIntent'] == expect_primary
    ok_conf = expect_confidence is None or result['confidenceBand'] == expect_confidence
    status = 'PASS' if ok_primary and ok_conf else 'FAIL'
    print(f"[{status}] {label}")
    print(f"       primary={result['primaryIntent']}  confidence={result['confidenceBand']}")
    print(f"       secondary={result['secondaryIntents']}")
    print(f"       reasons={result['reasons']}")
    print(f"       catSubtitle: {result['catSubtitle']}")
    print()


print("=" * 55)
print("  analyzeLocalRecording — smoke tests")
print("=" * 55)
print()

run_test("strong meal context → food_like / high",
    {**BASE, 'meal_context': 'before_meal_window', 'location_context': 'kitchen', 'duration_ms': 1700},
    'food_like', 'high')

run_test("owner returned home at door → attention_like",
    {**BASE, 'owner_context': 'owner_returned_home', 'location_context': 'door', 'duration_ms': 980},
    'attention_like')

run_test("during active play → playful",
    {**BASE, 'activity_context': 'during_play', 'owner_context': 'owner_interacting', 'duration_ms': 540},
    'playful')

run_test("window + door barrier → curious",
    {**BASE, 'location_context': 'window', 'environment_trigger': 'door_or_barrier_present', 'duration_ms': 1100},
    'curious')

run_test("late night bed + bedtime → sleepy / high",
    {**BASE, 'time_bucket': 'late_night', 'activity_context': 'bedtime_or_just_woke',
     'location_context': 'bed', 'duration_ms': 1450},
    'sleepy', 'high')

print("--- Edge cases ---")
print()

run_test("edge: unusable clip → unknown / low",
    {**BASE, 'clip_quality': 'unusable', 'duration_ms': 3100},
    'unknown', 'low')

run_test("edge: very short clip (240ms) → unknown",
    {**BASE, 'duration_ms': 240, 'clip_quality': 'noisy', 'owner_context': 'owner_left_room'},
    'unknown')

run_test("edge: noisy + weak context → unknown / low",
    {**BASE, 'clip_quality': 'noisy', 'location_context': 'unknown',
     'owner_context': 'owner_left_room', 'time_bucket': 'afternoon', 'duration_ms': 900},
    'unknown', 'low')

run_test("edge: after noise + owner left → unsettled",
    {**BASE, 'environment_trigger': 'after_noise', 'owner_context': 'owner_left_room',
     'location_context': 'bed', 'duration_ms': 2100},
    'unsettled')
