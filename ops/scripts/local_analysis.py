"""
Local heuristic analysis — Python port of analyzeLocalRecording.ts.
Phase 1: context signals only. No ML, no external dependencies.
Import this module; do not run it directly.
"""

VALID_TENDENCY = {'food_like', 'attention_like', 'playful', 'curious', 'unsettled', 'sleepy', 'unknown'}

SUMMARY_TEXT = {
    'food_like':      'Sounds like food might be on the mind — these kinds of vocalizations often show up around meal time.',
    'attention_like': 'Seems like your cat might be looking for a bit of company right now.',
    'playful':        "Sounds like play mode might be activating — something's caught the hunting instinct.",
    'curious':        'Something nearby seems to have caught some serious attention.',
    'unsettled':      'Sounds like something in the environment might have been a little startling or unexpected.',
    'sleepy':         'Seems like winding down time — this kind of sound often comes just before a long nap.',
    'unknown':        "Hard to say with this one — the signal wasn't strong enough to read clearly.",
}

CAT_SUBTITLE = {
    'food_like':      'Keeping a close eye on the bowl situation',
    'attention_like': "Just checking if you're paying attention",
    'playful':        'Ready for something to chase',
    'curious':        'Watching something very carefully',
    'unsettled':      'Not totally sure about that noise',
    'sleepy':         'Almost definitely about to nap',
    'unknown':        'Keeping their thoughts private',
}

# Neutral fallbacks for any NULL context fields from the DB
FIELD_DEFAULTS = {
    'duration_ms':          1000,
    'clip_quality':         'clean',
    'time_bucket':          'morning',
    'meal_context':         'no_food_context',
    'owner_context':        'owner_near',
    'environment_trigger':  'quiet',
    'activity_context':     'resting',
    'location_context':     'unknown',
    'recording_uri':        '',
}


def _fill_defaults(inp):
    return {k: (inp.get(k) or FIELD_DEFAULTS.get(k, '')) for k in FIELD_DEFAULTS}


def score_all(inp):
    inp = _fill_defaults(inp)
    s = {k: 0 for k in VALID_TENDENCY}
    reasons = []
    d = inp['duration_ms']

    # food_like
    if inp['meal_context'] == 'before_meal_window':   s['food_like'] += 3; reasons.append('meal window context')
    if inp['meal_context'] == 'food_visible':         s['food_like'] += 3; reasons.append('food visible')
    if inp['meal_context'] == 'owner_preparing_food': s['food_like'] += 2; reasons.append('owner preparing food')
    if inp['location_context'] == 'kitchen':          s['food_like'] += 2; reasons.append('kitchen location')
    if inp['time_bucket'] in ('morning', 'evening'):  s['food_like'] += 1
    if 500 <= d <= 2000:                              s['food_like'] += 1

    # attention_like
    if inp['owner_context'] == 'owner_returned_home': s['attention_like'] += 3; reasons.append('owner just returned')
    if inp['owner_context'] == 'owner_not_looking':   s['attention_like'] += 2; reasons.append('owner not looking')
    if inp['owner_context'] == 'owner_near':          s['attention_like'] += 1
    if inp['location_context'] == 'door':             s['attention_like'] += 2; reasons.append('near door')
    if inp['location_context'] == 'sofa':             s['attention_like'] += 1
    if inp['meal_context'] == 'after_meal_recent':    s['attention_like'] += 1; reasons.append('after recent meal')

    # playful
    if inp['activity_context'] == 'during_play':      s['playful'] += 3; reasons.append('during active play')
    if inp['activity_context'] == 'before_play':      s['playful'] += 3; reasons.append('pre-play context')
    if inp['owner_context'] == 'owner_interacting':   s['playful'] += 1; reasons.append('owner interacting')
    if 0 < d < 800:                                   s['playful'] += 1; reasons.append('short clip duration')

    # curious
    if inp['location_context'] == 'window':                     s['curious'] += 3; reasons.append('window location')
    if inp['environment_trigger'] == 'door_or_barrier_present': s['curious'] += 3; reasons.append('door or barrier present')
    if inp['environment_trigger'] == 'other':                   s['curious'] += 1; reasons.append('unusual trigger')
    if 500 <= d <= 1500:                                        s['curious'] += 1

    # unsettled
    if inp['environment_trigger'] == 'after_noise':       s['unsettled'] += 4; reasons.append('after loud noise')
    if inp['environment_trigger'] == 'unfamiliar_person': s['unsettled'] += 3; reasons.append('unfamiliar person present')
    if inp['environment_trigger'] == 'unfamiliar_animal': s['unsettled'] += 3; reasons.append('unfamiliar animal present')
    if inp['owner_context'] == 'owner_left_room':         s['unsettled'] += 2; reasons.append('owner left room')
    if d > 1500:                                          s['unsettled'] += 1

    # sleepy
    if inp['activity_context'] == 'bedtime_or_just_woke': s['sleepy'] += 3; reasons.append('bedtime or wake context')
    if inp['time_bucket'] == 'late_night':                s['sleepy'] += 2; reasons.append('late night time bucket')
    if inp['time_bucket'] == 'early_morning':             s['sleepy'] += 1
    if inp['location_context'] == 'bed':                  s['sleepy'] += 2; reasons.append('on the bed')
    if inp['activity_context'] == 'resting':              s['sleepy'] += 1
    if inp['location_context'] == 'sofa' and inp['activity_context'] == 'resting': s['sleepy'] += 1
    if d > 1000:                                          s['sleepy'] += 1

    # unknown — force when clip is unusable or too short
    if inp['clip_quality'] == 'unusable': s['unknown'] += 10; reasons.append('clip unusable')
    if 0 < d < 300:                       s['unknown'] += 3;  reasons.append('clip too short to read')
    max_content = max(s[k] for k in VALID_TENDENCY if k != 'unknown')
    if inp['clip_quality'] == 'noisy' and max_content <= 2:
        s['unknown'] += 2; reasons.append('noisy clip with weak context')

    return s, list(dict.fromkeys(reasons))


def top_intent(scores):
    return max(scores, key=scores.get)


def secondary_intents(primary, scores):
    top = scores[primary]
    threshold = max(2, top * 0.5)
    return sorted(
        [k for k in scores if k != primary and k != 'unknown' and scores[k] >= threshold],
        key=lambda k: -scores[k],
    )[:2]


def derive_confidence(primary, scores, clip_quality):
    if primary == 'unknown' or clip_quality == 'unusable':
        return 'low'
    sorted_scores = sorted(scores.values(), reverse=True)
    top, gap = sorted_scores[0], sorted_scores[0] - sorted_scores[1]
    if clip_quality == 'noisy':
        return 'medium' if top >= 4 and gap >= 2 else 'low'
    if top >= 6 and gap >= 3: return 'high'
    if top >= 3 and gap >= 2: return 'medium'
    return 'low'


def analyze(inp):
    scores, reasons = score_all(inp)
    primary = top_intent(scores)
    secondary = secondary_intents(primary, scores)
    confidence = derive_confidence(primary, scores, inp.get('clip_quality', 'clean'))
    return {
        'primaryIntent': primary,
        'secondaryIntents': secondary,
        'confidenceBand': confidence,
        'summaryText': SUMMARY_TEXT[primary],
        'catSubtitle': CAT_SUBTITLE[primary],
        'analysisMode': 'local_heuristic',
        'scoreBreakdown': scores,
        'reasons': reasons,
    }
