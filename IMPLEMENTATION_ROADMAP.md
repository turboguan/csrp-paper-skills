# Implementation roadmap — updated after v0.2

## M0 — Deterministic architecture skeleton — COMPLETE
- Pydantic schema and JSON Schema.
- Five synthetic paper skills.
- In-memory registry.
- NetworkX evidence graph.
- Three persistent domain roles.
- Evidence Judge and Safety Supervisor.
- End-to-end demo and tests.

## M0.2 — Five-real-paper architecture validation — CURRENT / COMPLETE AS PROTOTYPE
- Five real CSRP-linked Paper Skills created from public sources.
- Claim-level provenance, applicability and safety boundaries.
- Weighted lexical retrieval and query-aware claim selection.
- Query-level safety preflight.
- Explicit `heterogeneous` judge behavior for unlike outcomes.
- Curated `RELATED_TO` paper links without fabricated claim relations.
- Real-paper demo outputs and graph summary.
- 17 automated tests passing.

**Important:** these five records are model-curated, not expert-validated benchmark gold data.

## M1 — 10–15 paper evidence-family pilot — NEXT
Instead of immediately scaling to 50 heterogeneous papers, add 2–3 matched evidence families with multiple papers per scientific question.

Suggested families:
1. means restriction / charcoal-burning prevention;
2. media reporting / celebrity-suicide effects;
3. school/youth gatekeeper or mental-health promotion.

For every paper:
- freeze immutable source ID, DOI and checksum;
- use layout-aware extraction;
- validate population, intervention/exposure, comparator, outcome, effect estimate and uncertainty;
- validate every claim against a page/table/figure/source span;
- record extraction confidence and human adjudication status.

For every matched claim pair:
- expert label `SUPPORTS`, `CONTRADICTS`, `QUALIFIES`, `UNRELATED`, or `NOT_COMPARABLE`;
- document why the relation holds (population, outcome, method, timeframe).

**Exit criterion:** expert-reviewed Paper Skills plus a small gold cross-paper relation set.

## M2 — 30–50 paper benchmark corpus
- Freeze a representative heterogeneous corpus.
- Add GROBID/layout-aware extraction and robust table parsing.
- Add provider-neutral LLM extraction adapter with structured outputs.
- Hybrid retrieval: lexical + embedding + graph filters.
- Store corpus version and provenance snapshots reproducibly.

**Exit criterion:** expert-reviewed Evidence Cards and claim provenance across the 30–50 paper corpus.

## M3 — LLM reasoning adapters
- Add provider-neutral LLM interface.
- Keep all benchmark systems on the same base model/retriever wherever possible.
- Enforce structured answers and claim-level citation constraints.
- Track token, latency, API-call and coordination-message telemetry.
- Preserve deterministic fallback tests.

## M4 — Matched architecture benchmark
Compare:
1. RAG-only
2. Monolithic agent
3. One-paper-one-agent
4. Paper-as-skill

Task families:
- single-paper factual retrieval
- multi-paper synthesis
- contradiction/heterogeneity resolution
- population applicability
- method comparison
- safety-sensitive questions

Scaling loads:
`1 → 3 → 5 → 10 → 20 → 40` relevant papers.

Primary outcomes:
- claim-level factuality
- provenance precision/recall
- cross-paper relation accuracy
- contradiction detection
- evidence coverage
- calibration/abstention
- safety compliance
- latency/tokens/cost
- coordination-message burden

## M5 — Ablations
- no evidence graph
- no Evidence Judge
- no structured Evidence Cards
- no claim-level provenance
- no executable tools
- no shared workspace

## M6 — Human expert evaluation
- blinded system identity
- predefined rubric
- inter-rater reliability
- error taxonomy
- adjudication of claim-pair relations and final synthesis quality

## M7 — Full institutional corpus and external validation
- Scale registry/graph only after the benchmark pipeline is stable.
- Freeze the full CSRP corpus version rather than treating paper count itself as proof of scalability.
- Repeat a subset of the benchmark in a second scientific domain to test architectural generality.
