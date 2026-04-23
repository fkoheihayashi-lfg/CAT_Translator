# Heuristic Source of Truth Policy

## Purpose
This memo defines how CAT Translator Phase 1 heuristic logic should be governed across repos and languages.

The immediate goal is to prevent drift between:
- the app runtime heuristic
- the ops/reporting heuristic

This policy is for Phase 1 local-only work.

---

## Decision

**TypeScript is the single Source of Truth for Phase 1 heuristic behavior.**

Specifically:
- the app-side TypeScript local analysis logic is primary
- Python ops-side heuristic logic is secondary
- Python exists as a mirror for analysis/reporting workflows
- Python must follow TypeScript, not lead it

---

## Why This Decision Exists

### 1. The app is the real runtime
Users experience the app behavior, not the ops scripts.

If app behavior and ops reporting disagree, the app runtime must win.

### 2. Phase 1 is local-only and app-first
Current Phase 1 priorities are:
- interpretation text quality
- actual logging
- UX polish
- minimal app reconnection

That means the live product path is the app path.

### 3. Drift already appeared
TypeScript and Python implementations already showed signs of scoring drift.
If this continues, reports and app behavior will silently diverge.

### 4. Simplicity matters
Phase 1 should avoid multiple competing “truths.”
One heuristic truth is simpler, safer, and easier to maintain.

---

## Scope

This policy applies to Phase 1 local heuristic logic related to:
- context interpretation
- lightweight feature use
- intent scoring
- confidence behavior
- unknown fallback behavior
- interpretation-facing heuristic outcomes

This policy does **not** require:
- backend work
- model training
- Flask/YAMNet revival
- cloud architecture
- Phase 2 redesign

---

## Source of Truth Hierarchy

### Primary
**App repo TypeScript implementation**

Repo:
- `[APP] ~/Desktop/cat-translator`

Relevant area:
- `src/audio/localAnalysis/`

This is the authoritative implementation for:
- scoring behavior
- fallback rules
- patch behavior
- app-facing analysis output behavior

### Secondary
**Ops repo Python mirror**

Repo:
- `[OPS] ~/Documents/CAT_Translator`

Relevant area:
- `ops/scripts/local_analysis.py`

This implementation exists to support:
- review
- reporting
- summary generation
- ops-side inspection

It is not allowed to define new heuristic behavior independently.

---

## Operational Rules

### Rule 1
All heuristic tuning starts in TypeScript first.

### Rule 2
Python may mirror TypeScript logic for ops/reporting, but must not introduce new scoring behavior on its own.

### Rule 3
If TypeScript and Python disagree, treat that as drift.

### Rule 4
When drift is found:
1. confirm current TypeScript behavior
2. decide whether TypeScript is correct
3. update Python to match TypeScript if needed
4. record the sync decision briefly

### Rule 5
Do not tune Python first and “backport later.”
That creates two competing truths.

---

## Practical Implication

### For app work
If the question is:
- “What does the app actually do?”
- “What scoring is live?”
- “What patch is real?”
- “What logic should future app tuning follow?”

Use TypeScript.

### For ops/report work
If the question is:
- “What should weekly summary reflect?”
- “How should disagreement review behave?”
- “What should reporting mirror?”

Python may be used, but only as a mirror of TypeScript behavior.

---

## Drift Definition

A drift exists when any of the following differ between TS and Python:
- score weights
- context bucket meaning
- unknown fallback behavior
- confidence rules
- patch behavior
- interpretation-driving heuristic outcomes

Examples:
- `after_noise` weighting differs
- sleepy guard patch exists in TS but not in Python
- Python returns `unsettled` where TS would return `unknown`
- confidence logic differs for noisy clips

---

## Allowed Future Pattern

The preferred future pattern is:

1. tune TypeScript
2. validate app behavior
3. decide whether the tuning should be retained
4. update Python mirror if reporting needs the same behavior
5. note the sync briefly in docs or commit message

---

## Not Allowed

- Python-only heuristic evolution
- independent scoring experiments in Python without TS alignment
- treating ops reports as more authoritative than app runtime
- introducing a second source of truth for Phase 1 local heuristics

---

## Recommended Working Rule

When touching heuristic logic, always check both:

### [APP]
- `~/Desktop/cat-translator`
- `src/audio/localAnalysis/`

### [OPS]
- `~/Documents/CAT_Translator`
- `ops/scripts/local_analysis.py`

But remember:
- TS decides
- Python follows

---

## Minimal Review Checklist

Before merging or committing heuristic changes, ask:

1. Did the TS app logic change?
2. Does Python now drift from TS?
3. Does the drift matter for reporting/review?
4. If yes, should Python be updated now or explicitly left behind for a reason?
5. Was the decision recorded somewhere briefly?

---

## Current Status

As of this memo:
- TS is the declared truth
- Python is a mirror
- drift prevention is now an explicit policy
- future Phase 1 tuning should follow this rule unless a later decision memo replaces it
