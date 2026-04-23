# CAT Translator — Local Logging System

## Phase 1 Direction
- Fully local-only
- No backend / no API
- SQLite will be source of truth

## Logging Rules (Week 1)
- Target: 3 entries per day
- If unsure → use `unknown`
- `secondary_tendency` optional
- Avoid overusing `food_like`

## Structure
- data/ → DB + recordings
- ops/scripts → automation
- ops/reports → summaries

## Intent Labels
- attention_like
- food_like
- playful
- curious
- unsettled
- sleepy
- unknown

## Logging Rules (Week 1)
- Target: 3 entries per day
- If unsure → use `unknown`
- `secondary_tendency` optional
- Avoid overusing `food_like`