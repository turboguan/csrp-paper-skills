# Claim and provenance review codebook — v1

Each reviewer evaluates every candidate claim independently against the source publication.

## Claim verdict

Choose exactly one:

- `verified` — scientifically faithful as written.
- `minor_edit` — correct scientific meaning, but wording should be tightened without changing the substantive conclusion.
- `major_revision` — important scientific content, scope, direction, population, outcome, method, or uncertainty is misrepresented.
- `reject` — unsupported, materially incorrect, or unsuitable for benchmark use.

Only `verified` claims enter Gold unchanged. Claims marked `minor_edit` or `major_revision` require adjudicated replacement text before use.

## Provenance verdict

Choose exactly one:

- `verified` — locator/source span directly supports the claim.
- `locator_incomplete` — source supports the claim, but the locator is too weak or imprecise.
- `locator_wrong` — locator points to the wrong source location.
- `source_not_supportive` — cited source does not support the claim.
- `source_inaccessible` — reviewer cannot access/verify the source.

A Gold claim must end with `provenance_verdict = verified`.

## Direction verdict

Choose:
- `correct`
- `incorrect`
- `not_applicable`

Direction is about the structured label (`beneficial`, `harmful`, `null`, `mixed`, `descriptive`), not about whether the intervention should be recommended.

## Causal-language verdict

Choose:
- `acceptable`
- `too_strong`
- `too_weak`

Reviewers should judge whether the claim wording respects the study design and uncertainty.

## Structured-field verification

Reviewers answer `yes`, `no`, or `unclear` for:
- population fidelity;
- intervention/exposure fidelity;
- outcome fidelity;
- method fidelity.

## Gold inclusion rule

A claim may enter the final Gold set only when:
- final claim verdict is `verified`;
- final provenance verdict is `verified`;
- direction is correct or not applicable;
- causal-language verdict is acceptable;
- structured fields are accepted after adjudication.

Raw reviewer judgments must never be overwritten.
