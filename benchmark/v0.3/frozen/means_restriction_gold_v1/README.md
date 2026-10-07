# Means Restriction Gold Benchmark v1 — Protocol Freeze

**Freeze type:** pre-gold protocol freeze  
**Benchmark family:** `means_restriction_charcoal`  
**Freeze version:** `means-gold-v1.0`  
**Status:** locked protocol; human annotation pending

This directory freezes the materials required to convert the four-paper means-restriction evidence family into the first human-adjudicated Gold Evidence Family.

## Frozen scientific objects

Four source records are in scope:

1. `CSRP-REAL-004` — Hong Kong short-term controlled intervention (2010)
2. `V03-MEANS-002` — New Taipei short-term quasi-experimental intervention (2015)
3. `V03-MEANS-003` — New Taipei long-term controlled interrupted time-series follow-up (2021)
4. `V03-MEANS-004` — East/Southeast Asia regional time-trend context (2014)

The exact Git blob SHA for each Paper Skill is stored in `corpus_manifest.json`. Reviewers should adjudicate against those frozen records and the cited source publications.

## Frozen annotation workflow

The workflow has two independent stages:

### Stage A — Claim/provenance validation
Each reviewer independently checks all nine candidate claims for:
- scientific fidelity;
- effect/direction fidelity;
- causal-language appropriateness;
- population/intervention/outcome/method representation;
- provenance accuracy and sufficiency.

### Stage B — Claim-pair relation labeling
Each reviewer independently labels the four prespecified claim pairs as exactly one of:
- `SUPPORTS`
- `CONTRADICTS`
- `QUALIFIES`
- `NOT_COMPARABLE`
- `UNRELATED`

Reviewers must not see model-suggested labels or one another’s labels during independent review.

## Gold creation rule

A relation is eligible for Gold status only after:

1. both underlying claims are accepted or adjudicated into accepted form;
2. Reviewer A and Reviewer B have independently completed the relation sheet;
3. agreement is confirmed, **or** a named adjudicator resolves disagreement;
4. a final rationale is stored;
5. the raw reviewer sheets remain unchanged.

## Frozen statistical plan

`STATISTICAL_ANALYSIS_PLAN_v1.md` is the first prespecified analysis plan. It explicitly treats this four-pair family as a **pilot/mechanism benchmark**, not a sufficiently powered confirmatory experiment.

No inferential superiority claim may be made from four relation pairs alone.

## Change control

Files inside this directory are immutable after the freeze PR is merged. Corrections require a new version directory, for example:

`means_restriction_gold_v1_1/`

Do not overwrite v1.0 annotation instruments after reviewers begin.
