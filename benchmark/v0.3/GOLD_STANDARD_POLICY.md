# Gold-standard policy

A benchmark relation is not gold because a model, repository maintainer, or single reviewer finds it plausible.

## Required process

1. The underlying Paper Skill claim and provenance anchor are checked against the source.
2. Reviewer 1 labels the pair independently.
3. Reviewer 2 labels the pair independently.
4. If they agree, the shared label may be accepted after rationale review.
5. If they disagree, an adjudicator records the final label and rationale.
6. The relation record is then changed to `status = adjudicated`.

## Allowed labels

- `SUPPORTS`
- `CONTRADICTS`
- `QUALIFIES`
- `NOT_COMPARABLE`
- `UNRELATED`

## What reviewers must consider

- population and setting;
- intervention / exposure;
- outcome definition;
- study design and analytic method;
- follow-up window;
- effect direction and uncertainty;
- shared dataset or programme dependency;
- whether the two claims address the same scientific estimand.

## Model suggestions

`model_suggested_relation` may be retained for workflow triage but is never used as gold, never included in reviewer instructions, and never scored as a ground-truth label.
