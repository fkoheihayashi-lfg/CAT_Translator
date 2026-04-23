# Heuristic Eval Workflow

## Purpose
This workflow explains how to use a small external reference set safely while keeping the operational SQLite workflow intact.

## Separation Rule
Keep these layers separate:

### Operational DB
Use `vocalizations.db` for:

- local operational clips
- manual labels
- structured context logging
- regular weekly and disagreement review

### Reference Corpus
Use `reference_corpus/` for:

- external source tracking
- licensed audio references
- paper or evidence-only references
- hold/exclude/reference-only decisions

### Eval Set
Use a small eval subset for:

- heuristic spot-checking only
- adult domestic cat clips with clear provenance and licensing

## Hold / Exclude / Reference Only

### Hold
Use `Hold` when:

- the clip may become usable later
- license posture needs review
- age group or interaction context is not yet clear

### Exclude
Exclude from current Phase 1 heuristic eval when:

- license is unclear
- the source is non-reusable
- the audio is mother/kitten or kitten-only
- context certainty is too low
- there is no local copy for an audio item

### Reference Only
Use `Reference Only` when:

- the material is useful for notes or interpretation awareness
- the source is not appropriate for direct eval use
- the item is a paper or evidence summary without reusable audio

## Practical Eval Steps
1. add candidate external items to the reference manifest
2. use `manifest.json` as the working file and keep `manifest_template.json` untouched as an example
3. keep provenance, license, age, and context notes explicit
4. run `eval_reference_manifest.py`
5. remove or hold anything the helper flags
6. use only the remaining adult domestic clips for cautious heuristic spot-checking

## Safe Current Policy
For current Phase 1 adult heuristic eval:

- prefer a very small number of clearly licensed adult domestic clips
- do not mix operational logs and external references into the same table
- do not let eval material change the schema or pipeline
- do not tune around weak or ambiguous external sources

## Why This Matters
This approach allows heuristic checking with outside material while preserving:

- the operational role of `vocalizations.db`
- the current review script flow
- provenance clarity
- license clarity
- adult Phase 1 evaluation focus
