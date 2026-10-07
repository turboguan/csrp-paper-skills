# v0.2 real-paper catalog

This version replaces the purely synthetic demonstration with **five real CSRP-linked publications** selected to stress different parts of the architecture. The Paper Skills are model-curated from public sources and are **not yet expert-validated gold annotations**.

| ID | Paper | Role in MVP | Prevention level |
|---|---|---|---|
| CSRP-REAL-001 | S.H.I.E.L.D.S. student leadership / gatekeeper programme | Youth, school, mixed-method programme evaluation | Selective |
| CSRP-REAL-002 | Hong Kong spatial-temporal suicide clusters | Surveillance, geography, ecological inference boundary | Universal |
| CSRP-REAL-003 | Postdischarge caring contact after self-harm | High-risk postdischarge intervention, small pragmatic RCT | Indicated |
| CSRP-REAL-004 | Restricting retail access to charcoal | Means restriction, community controlled intervention | Universal |
| CSRP-REAL-005 | Celebrity suicide and Hong Kong suicide rates | Media exposure, population natural-experiment evidence | Universal |

## Why these five?

The first v0.2 goal is architecture validation, not meta-analysis. The set intentionally spans several study designs, populations and prevention levels so that routing, structured retrieval, evidence boundaries, graph construction and safety behavior can all be exercised.

The set is **not** designed to claim that five papers provide a complete view of CSRP research. It also does not yet provide enough matched paper pairs for a strong contradiction-resolution benchmark. The next corpus expansion should deliberately add matched evidence families (same or closely related intervention, outcome and population) so `SUPPORTS`, `CONTRADICTS` and `QUALIFIES` relations can be evaluated against expert labels.

## Validation status

Every record has:
- real DOI/publication metadata;
- claim-level source anchors;
- explicit applicability and safety boundaries;
- `human_validation_status = model_curated_not_expert_validated`.

Before these records become benchmark gold data, a domain expert should independently check population, intervention/exposure, outcome, effect estimate, claim wording, causal language and source location.
