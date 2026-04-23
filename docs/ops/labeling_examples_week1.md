# Labeling Examples Week 1

## Purpose
These examples are meant to reduce hesitation during the first real logs. They are not diagnostic. They are short practical examples using the fixed Phase 1 schema only.

| Scenario | Probable context values | Good primary_tendency | Fill secondary_tendency? | Suggested confidence | Short reason |
| --- | --- | --- | --- | --- | --- |
| Before breakfast near bowl | `time_bucket=morning`, `meal_context=before_meal_window`, `location_context=kitchen` | `food_like` | Usually no | `high` | Meal timing and location line up cleanly |
| Food visible on counter | `meal_context=food_visible`, `owner_context=owner_near`, `location_context=kitchen` | `food_like` | Usually no | `medium` | Food context is strong even if the clip is short |
| Loud hallway noise, cat vocalizes after | `environment_trigger=after_noise`, `activity_context=resting`, `clip_quality=clean` | `unsettled` | Optional | `medium` | The reaction seems tied to the sound event |
| Cat vocalizes near front door when someone arrives | `owner_context=owner_returned_home`, `location_context=door`, `time_bucket=evening` | `attention_like` | Usually no | `high` | Greeting-style context points to attention |
| Cat looks at window and chirps once | `location_context=window`, `environment_trigger=door_or_barrier_present` or `other` | `curious` | Usually no | `medium` | The context suggests focused curiosity |
| Owner is present but not looking, single meow | `owner_context=owner_not_looking`, `location_context=sofa`, `clip_quality=clean` | `attention_like` | Optional | `medium` | Attention-seeking context seems stronger than food or play |
| Wand toy comes out and vocal burst happens | `activity_context=during_play`, `owner_context=owner_interacting`, `clip_quality=clean` | `playful` | Usually no | `high` | Active play context gives the clearest read |
| Short chirp just before play starts | `activity_context=before_play`, `owner_context=owner_interacting` | `playful` | Optional | `medium` | Pre-play setup supports playful more than attention |
| Soft vocal before curling up on bed | `activity_context=bedtime_or_just_woke`, `location_context=bed`, `time_bucket=late_night` | `sleepy` | Usually no | `high` | Low-energy bedtime context is strong |
| Cat vocalizes after owner leaves room | `owner_context=owner_left_room`, `activity_context=resting`, `clip_quality=clean` | `attention_like` | Optional | `low` | Could be attention-like, but context may still be thin |
| Clip is muddy and source is unclear | `clip_quality=clean` or `noisy`, weak context values | `unknown` | No | `low` | Better to leave it unknown than force certainty |
| Background TV or handling noise covers most of clip | `clip_quality=noisy`, any context weak | `unknown` | No | `low` | The row is still usable, but quality may be driving uncertainty |

## Notes
- If `clip_quality=unusable`, prefer `primary_tendency=unknown`.
- Only fill `secondary_tendency` if it adds real value quickly.
- If the clip is not strong enough, use `unknown` and move on.
