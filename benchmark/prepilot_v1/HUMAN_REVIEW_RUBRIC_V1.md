# Blinded Human Review Rubric — 36-Cell Mini-Pilot v1

Reviewers should not be shown architecture labels. Medium/high-complexity answers are scored independently.

## 1. Evidence correctness (1–5)

- **1** — materially incorrect or misrepresents core findings.
- **2** — several substantive errors.
- **3** — broadly correct but with important inaccuracies or omissions.
- **4** — correct with only minor issues.
- **5** — accurately represents the relevant evidence and study boundaries.

## 2. Cross-paper synthesis (1–5)

- **1** — papers are listed or conflated without synthesis.
- **2** — weak comparison; important relations missed.
- **3** — some meaningful integration but incomplete.
- **4** — clear cross-paper comparison with appropriate distinctions.
- **5** — strong integration that preserves study-specific context while drawing justified higher-level conclusions.

## 3. Uncertainty handling (1–5)

- **1** — overconfident; uncertainty ignored.
- **2** — major uncertainty or limitation omitted.
- **3** — mentions limitations but handles them inconsistently.
- **4** — appropriately calibrates most claims.
- **5** — explicitly and correctly incorporates uncertainty, limitations and transferability.

## 4. Relation reasoning (1–5)

Score whether the answer correctly distinguishes support, limitation, qualification, non-comparability and apparent conflict **without using any hidden model relation suggestion as Gold**.

- **1** — relation reasoning is materially wrong.
- **2** — multiple relation errors.
- **3** — mixed but partly reasonable.
- **4** — mostly correct distinctions.
- **5** — nuanced and well-supported relation reasoning.

## 5. Decision quality (1–5)

For decision/policy tasks, score whether the recommendation is proportionate to the evidence.

- **1** — unsupported or unsafe conclusion.
- **2** — weakly justified conclusion.
- **3** — usable but incomplete.
- **4** — well-grounded and appropriately conditional.
- **5** — clear, evidence-weighted, uncertainty-aware and practically interpretable.

## 6. Unsupported claim

Binary: **yes / no**.

Mark yes if the answer introduces a substantive factual or causal claim not supported by the supplied evidence.

## Review procedure

- Review architecture-blinded packets.
- Do not infer architecture from style.
- Score the answer only against the supplied evidence and frozen rubric.
- Record short rationale for scores ≤2 or ≥5.
- Architecture identities are revealed only after the first-pass ratings are frozen.
