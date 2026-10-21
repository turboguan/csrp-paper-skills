<p align="center">
  <img src="docs/assets/logo.svg" alt="CSRP Paper Skills logo" width="760"/>
</p>

<p align="center">
  <a href="https://github.com/turboguan/csrp-paper-skills/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/turboguan/csrp-paper-skills/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB">
  <img alt="Version" src="https://img.shields.io/badge/version-0.3.0--dev-2a7f78">
  <img alt="Status" src="https://img.shields.io/badge/status-research%20prototype-lightgrey">
</p>

# Virtual CSRP

**An institutional AI architecture for suicide prevention research, policy, practice and bounded community support.**

> **Core principle:** papers provide evidence and capabilities; agents provide reasoning and coordination.

Virtual CSRP extends the repository from a paper-level architecture question to an **institution-level organizational design problem**. The evidence foundation still uses provenance-preserving Paper Skills and a shared Evidence Graph, while the institutional layer adds a Director / PI Agent, Chief of Staff / Query Router, five specialized divisions, an Evidence Judge, a Safety Supervisor and four service pathways.

The central research question is:

> **How does organizational design shape collective reasoning, evidence integration and decision quality in AI co-scientists?**

Three organizational forms are implemented for matched comparison:

1. **Functional Virtual Institute** — functionally differentiated agents coordinated in a shared evidence context.
2. **Paper-Agent Committee** — paper-level expert agents deliberate under a chair/orchestrator.
3. **Shared-Knowledge Umbrella** — a small institutional reasoning layer works over shared Paper Skills and an Evidence Graph.

The project does **not** assume that one architecture is universally superior. The intended management-science framing is an **Architecture × Task Characteristics** contingency test.

## Current recommended architecture — Minimal Virtual CSRP

<p align="center">
  <img src="docs/assets/minimal_virtual_csrp_architecture.svg" alt="Minimal Virtual CSRP architecture" width="100%"/>
</p>

The current operating design no longer tries to reproduce a human research-center org chart literally.

Virtual CSRP now uses **four core agent capabilities**:

```text
Research Coordinator
        ↓
Evidence & Data
        ↓
Analysis & Methods      (activated only when needed)
        ↓
Synthesis & Decision
        ↓
Quality & Safety Gate   (not an agent)
```

All agents share institutional infrastructure: **Paper Skills, Evidence Graph, provenance registry, datasets, analysis artifacts and prior outputs**.

For evidence-only tasks, only three agents need to be active: Coordinator → Evidence & Data → Synthesis & Decision. The Analysis & Methods Agent is activated only for tasks requiring statistical or computational work.

This replaces the earlier Director / Chief of Staff / department-style hierarchy. The design principle is:

> **Create an autonomous agent only when it performs a distinct information-processing function.**

See [docs/V1.1_MINIMAL_VIRTUAL_CSRP.md](docs/V1.1_MINIMAL_VIRTUAL_CSRP.md).

## Architecture

<p align="center">
  <img src="docs/assets/architecture.svg" alt="Paper-as-Skill architecture" width="100%"/>
</p>

The system follows:

```text
Papers
  ↓
Paper-to-Skill Factory
  ↓
Shared Paper Skill Registry + Shared Evidence Graph
  ↓
Few persistent Domain Agents
  ↓
Evidence Judge
  ↓
Safety Supervisor
  ↓
Evidence-grounded answer + claim-level provenance
```

The key distinction is that **Paper Skill ≠ Persistent Agent**. Multiple paper skills can be loaded into one shared reasoning workspace so cross-paper relations can be evaluated without spawning one isolated agent per paper.

## What v0.2 contains

- Pydantic Paper Skill schema and JSON Schema export
- claim-level provenance and source anchors
- in-memory structured Skill Registry
- NetworkX evidence graph
- Universal / Selective / Indicated persistent domain roles
- rule-based Evidence Judge
- safety preflight + Safety Supervisor
- synthetic regression fixtures
- five real CSRP-linked structured Paper Skills
- deterministic end-to-end demos
- benchmark runner interfaces
- unit and integration tests

The current real-paper records are **model-curated research artifacts, not expert-validated gold annotations**.

## Quick start

```bash
git clone https://github.com/turboguan/csrp-paper-skills.git
cd csrp-paper-skills
python3 -m pip install -e '.[dev]'
python3 real_demo.py
pytest -q
```

The real-paper demo writes structured outputs to:

```text
outputs/real/real_demo_output.json
outputs/real/graph_summary.json
```

## Research questions this repository is designed to test

The future matched benchmark will compare:

1. RAG-only
2. single monolithic agent
3. one-paper-one-agent
4. **Paper-as-Skill (ours)**

under increasing evidence load and matched retrieval budgets.

Primary outcomes include:

- cross-paper relation accuracy
- claim-level factuality
- provenance precision / recall
- contradiction vs heterogeneity resolution
- evidence coverage
- calibration / abstention
- safety compliance
- latency / tokens / API calls
- coordination-message burden

## Current scientific status

### Demonstrated in v0.2
- the architecture runs end to end;
- multiple paper skills can coexist in a shared evidence workspace;
- claim-level provenance can be carried through the pipeline;
- individual suicide-risk scoring is blocked before evidence retrieval;
- deterministic tests cover registry, graph, judge, safety, and orchestration logic.

### Not yet demonstrated
- superiority over RAG or multi-agent baselines;
- validated systematic-review quality;
- clinical utility;
- expert-level contradiction adjudication;
- scaling performance on the full institutional corpus.

See [V0.2_STATUS.md](V0.2_STATUS.md) for the exact boundary between implementation status and scientific evidence.

## v0.3 — Evidence-Family Benchmark

**Current development status:** the repository now includes a normal `src/`, `tests/`, `schemas/` and `benchmark/v0.3/` source tree; the embedded v0.2 ZIP is no longer required.

The first implemented family is **means restriction / charcoal burning**, with four papers spanning short-term intervention evidence, long-term follow-up and regional epidemiological context. Candidate claim-pair relations remain non-gold until two-reviewer adjudication.

The next milestone is a **10–15 paper, 2–3 family benchmark** built around matched scientific questions rather than simply adding more heterogeneous papers.

Candidate families:

- means restriction / charcoal-burning prevention
- media reporting / celebrity-suicide effects
- school/youth gatekeeper or mental-health promotion interventions

For every matched claim pair, experts will adjudicate:

`SUPPORTS` · `CONTRADICTS` · `QUALIFIES` · `NOT_COMPARABLE` · `UNRELATED`

This will create the first gold dataset capable of testing the central architectural hypothesis.

See [docs/V0.3_ROADMAP.md](docs/V0.3_ROADMAP.md).

## v0.8 — Virtual CSRP institutional layer

The repository now includes a complete institutional scaffold above the existing Paper Skill, Evidence Graph and A/B/C organization implementations.

Virtual CSRP contains five institutional divisions:

- Surveillance & Epidemiology;
- Intervention & Evaluation;
- Policy & Implementation;
- Practitioner & Community Support;
- Methods & Evidence.

The cross-cutting governance layer contains an **Evidence Judge** and **Safety Supervisor**. The user-facing service layer contains **Research Co-Scientist**, **Policy Intelligence**, **Practitioner Guidance**, and bounded **Community / Individual Support**.

See [docs/V0.8_VIRTUAL_CSRP.md](docs/V0.8_VIRTUAL_CSRP.md) and [benchmark/v0.8/virtual_csrp_manifest.json](benchmark/v0.8/virtual_csrp_manifest.json).

The four-paper Means Restriction pilot remains the first matched experimental substrate and is not altered by the v0.8 institutional framing.

## Repository guide

| File / directory | Purpose |
|---|---|
| `src/csrp_skills/` | Core implementation |
| `schemas/` | Paper Skill schema |
| `sample_skills/` | Synthetic regression fixtures |
| `real_skills/` | Real-paper structured records |
| `tests/` | Unit and integration tests |
| `architecture.md` | System architecture notes |
| `REAL_PAPER_CATALOG.md` | Real-paper catalog |
| `SOURCE_MANIFEST.md` | Source/provenance manifest |
| `REPRODUCIBILITY.md` | Reproducibility policy |
| `CONTRIBUTING.md` | Contribution guidelines |
| `DISCLAIMER.md` | Research and clinical-use disclaimer |

## Safety boundary

This repository is an **academic research prototype**, not a clinical decision-support system.

It must not be used for:
- autonomous individual suicide-risk scoring;
- diagnosis or triage;
- treatment selection;
- unsupported clinical recommendation.

Individual-facing uses would require substantially stronger validation, governance, privacy protections, and human oversight.

See [DISCLAIMER.md](DISCLAIMER.md) and [SECURITY.md](SECURITY.md).

## Citation

Citation metadata is provided in [CITATION.cff](CITATION.cff). GitHub will expose a **Cite this repository** action after it is merged into the default branch.

Suggested project citation:

> Guan, J. (2026). *CSRP Paper-as-Skill: A provenance-preserving architecture for institutional scientific AI* (v0.2.0). GitHub repository.

A DOI should be added later through an archival release service once the benchmark corpus and first stable research release are frozen.

## Contributing

Contributions are welcome, especially around:

- evidence-family construction;
- claim-level provenance validation;
- graph relation adjudication;
- benchmark runners;
- reproducibility tooling;
- safety and uncertainty evaluation.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Project status

**Research prototype — v0.8 Virtual CSRP scaffold**

Current work combines institutional AI design, Paper Skills, evidence graphs and matched organizational experiments. The immediate scientific programme is to compare the three organizational forms under controlled evidence, model and token budgets, beginning with the four-paper Means Restriction pilot.

**Tagline:** *From paper-level evidence to institutional intelligence.*
