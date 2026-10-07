# Statistical Analysis Plan v1

**Study:** Paper-as-Skill Evidence-Family Benchmark  
**Pilot family:** Means restriction / charcoal burning  
**Plan version:** 1.0  
**Status:** prespecified before Gold annotation and before four-system LLM benchmarking

## 1. Objective

Evaluate whether the Paper-as-Skill architecture preserves cross-paper scientific relations and provenance more reliably than matched alternative architectures.

The four architectures are:

1. RAG-only
2. Monolithic agent
3. One-paper-one-agent
4. Paper-as-Skill

The principal architectural contrast is:

**Paper-as-Skill vs One-paper-one-agent**

because this most directly tests the hypothesis that shared evidence context outperforms isolated paper-level reasoning contexts for cross-paper synthesis.

## 2. Pilot versus confirmatory scope

The initial means-restriction family contains four papers and four prespecified relation pairs.

This is a **pilot/mechanism benchmark**.

Because four relation pairs are too few for credible confirmatory significance testing, the means-family pilot will report descriptive performance and uncertainty only. It may demonstrate feasibility, expose failure modes, and validate the evaluation pipeline, but it must not support a standalone claim of architectural superiority.

Confirmatory inference is deferred until multiple Gold Evidence Families are available.

## 3. Experimental unit

The primary scientific unit is the **Gold claim pair** for relation-classification tasks.

For synthesis tasks, the unit is the **prespecified benchmark query**.

Model replicates are repeated measurements, not independent scientific units. Replicates must not be treated as if they increase the number of independent claim pairs or queries.

## 4. Frozen experimental conditions

Before model execution, freeze:

- benchmark corpus and Paper Skill versions;
- Gold claim/provenance records;
- Gold relation labels;
- benchmark query set;
- base LLM;
- model version/date;
- system prompts;
- retrieval method;
- top-k/evidence budget;
- maximum context and output token limits;
- temperature and sampling settings;
- tool availability;
- retry policy;
- number of replicates;
- software commit SHA.

Only architecture-specific coordination/context structure may differ across the four systems.

## 5. Replicates

If the selected model/API supports deterministic decoding, use the most deterministic supported configuration and run **5 replicates per architecture-query cell** to measure residual platform/model variability.

If a fixed random seed is supported, record it.

Replicate-level outputs are retained, but statistical resampling is clustered at the query or claim-pair level.

## 6. Primary endpoint

For the full multi-family benchmark:

**Cross-paper relation classification accuracy on adjudicated Gold claim pairs.**

A prediction is correct only when the system selects the exact Gold label among:

`SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `NOT_COMPARABLE`, `UNRELATED`.

The primary contrast is the paired difference in accuracy:

`Paper-as-Skill − One-paper-one-agent`.

## 7. Key secondary endpoints

1. **Macro-F1 across relation labels**
2. **Contradiction false-positive rate**  
   Fraction of non-`CONTRADICTS` Gold pairs incorrectly labeled `CONTRADICTS`.
3. **Claim-level provenance precision**
4. **Claim-level provenance recall**
5. **Evidence coverage**  
   Fraction of prespecified required Gold claims surfaced in the answer.
6. **Unsupported-claim rate**
7. **Abstention/calibration performance**
8. **Safety compliance**
9. **Coordination-message burden**
10. **Input/output tokens**
11. **LLM/tool-call count**
12. **Latency and estimated API cost**

## 8. Synthesis quality

For multi-paper synthesis questions, blinded human raters will score:
- scientific correctness;
- completeness/evidence coverage;
- distinction between contradiction and heterogeneity/qualification;
- uncertainty calibration;
- provenance quality;
- applicability reasoning.

A fixed rubric and scoring range must be frozen before confirmatory runs.

## 9. Pilot analysis — means family

For the four-pair pilot, report:

- exact number correct / 4 for each architecture;
- label-level confusion table;
- contradiction false positives;
- provenance precision/recall;
- evidence coverage;
- raw token/call/latency telemetry;
- all individual outputs.

No p-value from the four relation pairs will be interpreted as confirmatory evidence.

Exact binomial confidence intervals may be shown descriptively, with an explicit warning that pairs are few and scientifically heterogeneous.

## 10. Confirmatory paired analysis

Once the benchmark contains enough independent Gold units across evidence families:

### Primary comparison
Use a **paired cluster bootstrap** over Gold scientific units (claim pairs for relation tasks; queries for synthesis tasks), with **10,000 resamples**, to estimate:
- mean paired difference in primary metric;
- 95% percentile bootstrap confidence interval.

Replicates remain nested within the resampled scientific unit.

### Binary paired sensitivity analysis
For relation correctness, use **McNemar’s exact test** for the primary Paper-as-Skill vs One-paper-one-agent comparison when the number of discordant pairs is sufficient to make the test meaningful.

The bootstrap effect estimate remains primary.

## 11. Multiple comparisons

There is one prespecified primary contrast:
- Paper-as-Skill vs One-paper-one-agent.

Comparisons with:
- RAG-only;
- Monolithic agent

are secondary.

If inferential p-values are reported for the three architecture contrasts on one endpoint, control family-wise error using **Holm correction**.

Do not apply significance testing separately to every telemetry metric.

## 12. Scaling analysis

Evidence load will be manipulated at prespecified levels where corpus size permits:

`1 → 3 → 5 → 10 → 20 → 40` relevant papers.

Primary scaling outcome:
- cross-paper relation accuracy.

Secondary scaling outcomes:
- provenance recall;
- unsupported-claim rate;
- coordination messages;
- tokens;
- latency.

The principal descriptive quantity is the architecture-by-evidence-load performance curve.

If sample size is adequate, a secondary mixed-effects model may be fit with:
- fixed effects: architecture, log2(evidence load), architecture × load;
- random intercept: benchmark question/evidence family.

This model is secondary and will not replace paired bootstrap results.

## 13. Inter-rater reliability

Before adjudication:

### Relation labels
Report:
- raw percent agreement;
- Cohen’s kappa for the five nominal labels.

### Claim/provenance review
Report raw agreement for claim verdict and provenance verdict. Weighted kappa may additionally be reported for claim verdict if the ordering `verified < minor_edit < major_revision < reject` is retained.

Reliability is reported before adjudication.

## 14. Missing or invalid outputs

A system output is marked invalid if:
- no parseable relation label is produced when one is required;
- required provenance format is absent;
- execution fails after the frozen retry policy.

Invalid outputs count as incorrect for accuracy and as missing for the relevant provenance component.

Do not silently rerun only low-performing architectures.

## 15. Exclusions

Exclude from the primary Gold analysis only by prespecified rule:
- claim rejected during source/provenance review;
- source cannot be verified;
- pair contains a rejected claim;
- pair is formally removed before benchmark execution because the scientific estimand was incorrectly specified.

All exclusions and reasons must be logged before systems are run.

## 16. No outcome-driven changes

After the first four-system benchmark run:
- do not change Gold labels;
- do not rewrite queries;
- do not change the primary endpoint;
- do not change the primary architecture contrast.

Any post-hoc experiment must be labeled exploratory and versioned separately.

## 17. Reporting

Report:
- Gold-set composition;
- annotation agreement;
- adjudication counts;
- all architecture settings;
- primary and secondary metrics;
- paired effect estimates and confidence intervals when sample size permits;
- failure taxonomy;
- exact benchmark/software version.

Negative or null findings will be reported alongside positive findings.
