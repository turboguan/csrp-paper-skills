# Adjudication protocol v1

## Purpose

This protocol converts independent human review into a traceable Gold Evidence Family while preserving raw judgments.

## Roles

- **Reviewer A:** independently validates claims/provenance and labels relations.
- **Reviewer B:** independently performs the same tasks.
- **Adjudicator:** resolves disagreements after both reviewers have locked their sheets.

A reviewer may not serve as the sole adjudicator for a disagreement involving their own label.

## Blinding

During independent review, Reviewer A and Reviewer B must not have access to:
- `model_suggested_relation`;
- the other reviewer’s sheet;
- system outputs from RAG-only, monolithic-agent, one-paper-one-agent, or Paper-as-Skill runs;
- benchmark performance summaries.

They may access the source papers, frozen Paper Skill records, codebook, and blinded review packet.

## Phase 1 — Claim/provenance review

Each reviewer completes their own claim/provenance CSV.

For every claim, record:
- claim verdict;
- provenance verdict;
- direction verdict;
- causal-language verdict;
- structured-field fidelity;
- proposed replacement claim text if needed;
- proposed corrected provenance locator if needed;
- comments.

### Claim adjudication

If both reviewers mark a claim `verified` and provenance `verified`, it is provisionally accepted.

All other cases go to adjudication.

The adjudicator must record:
- final claim verdict;
- final claim text;
- final provenance locator;
- final structured fields if changed;
- adjudication rationale.

A rejected claim cannot participate in a Gold relation pair.

## Phase 2 — Relation labeling

Only pairs whose two claims survive Phase 1 are eligible.

Each reviewer independently labels each pair:

`SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `NOT_COMPARABLE`, or `UNRELATED`.

Reviewers must also record:
- population comparability;
- intervention/exposure comparability;
- outcome comparability;
- method/estimand comparability;
- timeframe comparability;
- dataset/programme dependency;
- free-text rationale;
- confidence: `high`, `medium`, or `low`.

## Relation adjudication

If both reviewers agree on the label:
- the agreed label becomes the adjudicated label after rationale review;
- the adjudicator may edit the final rationale for clarity but may not silently change the label.

If reviewers disagree:
- the adjudicator reads both rationales and source claims;
- selects one allowed relation label;
- records a written resolution;
- records their adjudicator ID.

The adjudicator must not use model predictions as evidence.

## Audit trail

The following are immutable raw artifacts:
- Reviewer A claim/provenance sheet;
- Reviewer B claim/provenance sheet;
- Reviewer A relation sheet;
- Reviewer B relation sheet.

The adjudicated master file is a separate artifact.

Corrections after Gold freeze require a new version and a changelog.

## Inter-rater reliability

Before adjudication:
- report raw agreement and Cohen’s kappa for nominal relation labels;
- report raw agreement for claim-verdict/provenance-verdict categories;
- weighted kappa may be reported for ordered claim verdicts if category ordering is prespecified.

Reliability statistics describe annotation consistency; they do not replace adjudication.

## Stopping rule

This Gold family is frozen when:
- all retained claims have verified claim and provenance status;
- every prespecified pair has either an adjudicated relation or a documented exclusion;
- all reviewer and adjudication fields are complete;
- a freeze manifest records the final Git commit.

No new pair may be added to v1.0 after annotation begins.
