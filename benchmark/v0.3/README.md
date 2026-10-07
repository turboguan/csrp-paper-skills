# v0.3 Evidence-Family Benchmark

This directory contains the **candidate-stage** material for the first scientifically testable benchmark of the Paper-as-Skill architecture.

Nothing in this directory is benchmark gold yet.

## Why evidence families?

The v0.2 five-paper demo is intentionally heterogeneous. It is useful for architecture validation but not for testing whether a system correctly preserves cross-paper scientific relationships. v0.3 therefore groups papers around matched scientific questions.

Current candidate families:

1. `means_restriction_charcoal`
2. `media_celebrity_reporting`
3. `school_youth_mental_health`

The candidate manifest currently contains **13 papers**. Three are already represented by v0.2 Paper Skills; the rest still require ingestion and expert validation.

## Primary relation labels

Every matched claim pair is eventually adjudicated as exactly one of:

- `SUPPORTS`
- `CONTRADICTS`
- `QUALIFIES`
- `NOT_COMPARABLE`
- `UNRELATED`

`NOT_COMPARABLE` is distinct from `CONTRADICTS`. A short-term positive intervention result and a longer-term null follow-up may, for example, qualify one another when implementation fidelity or timeframe differs rather than forming a direct contradiction.

## Dependency handling

Papers from the same programme, cohort, or underlying dataset must be marked explicitly. They are useful for testing duplicate-evidence handling but must not be counted as independent support in the primary benchmark.

## Gold-label rule

A relation record is **not** gold unless:

- two reviewers have independently labeled it;
- disagreements are adjudicated;
- a written rationale is stored;
- population, intervention/exposure, outcome, method, timeframe and dataset dependency are recorded.

No model-curated relation is silently promoted to benchmark truth.
