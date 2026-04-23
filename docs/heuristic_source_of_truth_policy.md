# Heuristic Source of Truth Policy

## Purpose
This memo defines how CAT Translator Phase 1 heuristic logic should be governed across repos and languages.

The goal is to prevent drift between:
- app runtime heuristic behavior
- ops/reporting heuristic behavior

This policy is for Phase 1 local-only work.

## Decision
TypeScript in the app repo is the single Source of Truth for Phase 1 heuristic behavior.

That means:
- app-side TypeScript logic is primary
- ops-side Python logic is secondary
- Python exists to support analysis, reporting, and review
- Python must follow TypeScript, not lead it

## Why TypeScript Is Primary

### 1. The app is the real runtime
Users experience the app behavior, not the ops scripts.

If app behavior and ops reporting disagree, app runtime behavior wins.

### 2. Phase 1 is app-facing even though it is local-only
Current priorities are:
- interpretation text quality
- actual logging
- UX polish
- minimal app reconnection

That makes the live product path the app path.

### 3. Drift is already a known risk
TypeScript and Python heuristic implementations can diverge silently if both are treated like equal authorities.

This policy removes that ambiguity.

### 4. One truth is simpler
Phase 1 should not carry two competing heuristic definitions.

## Source-of-Truth Hierarchy

### Primary
App repo TypeScript implementation

Repo:
- `[APP] ~/Desktop/cat-translator`

Relevant area:
- `src/audio/localAnalysis/`

This is authoritative for:
- scoring behavior
- fallback behavior
- confidence behavior
- patch behavior
- app-facing analysis output

### Secondary
Ops repo Python mirror

Repo:
- `[OPS] ~/Documents/CAT_Translator`

Relevant area:
- `ops/scripts/local_analysis.py`

This exists for:
- reporting
- summaries
- disagreement review
- ops-side inspection

It is not allowed to define new heuristic behavior independently.

## Operational Rules

### Rule 1
All heuristic tuning starts in TypeScript first.

### Rule 2
Python may mirror TypeScript behavior for ops/reporting, but must not introduce new scoring behavior on its own.

### Rule 3
If TypeScript and Python disagree, treat that as drift.

### Rule 4
When drift is found:
1. confirm current TypeScript behavior
2. decide whether TypeScript is correct
3. update Python to match if reporting needs the same behavior
4. record the sync decision briefly

### Rule 5
Do not tune Python first and backport later.

## Drift Definition
A drift exists when TypeScript and Python differ on any of the following:
- score weights
- context interpretation meaning
- unknown fallback behavior
- confidence rules
- patch behavior
- interpretation-driving heuristic outcomes

Examples:
- `after_noise` weighting differs
- a sleepy guard patch exists in TS but not in Python
- Python returns `unsettled` where TS would return `unknown`
- confidence behavior differs for noisy clips

## Practical Implications

### For app work
If the question is:
- what the app actually does
- what scoring is live
- what patch is real
- what behavior future tuning should follow

Use TypeScript.

### For ops/report work
If the question is:
- what weekly summary should reflect
- how disagreement review should behave
- what reporting should mirror

Python may be used, but only as a mirror of TypeScript behavior.

## Not Allowed
- Python-only heuristic evolution
- independent scoring experiments in Python without TS alignment
- treating ops reports as more authoritative than app runtime
- introducing a second source of truth for Phase 1 local heuristics

## Minimal Review Checklist
Before committing heuristic changes, ask:

1. Did the TypeScript app logic change?
2. Does Python now drift from TypeScript?
3. Does the drift matter for reporting/review?
4. If yes, should Python be updated now or explicitly left behind for a reason?
5. Was the decision recorded briefly?

## Current Status
As of this memo:
- TS is the declared Source of Truth
- Python is a mirror for ops/reporting
- drift prevention is now an explicit Phase 1 rule
- existing ops scripts remain intact
