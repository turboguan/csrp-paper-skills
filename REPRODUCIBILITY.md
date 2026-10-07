# Reproducibility

## Current reproducible scope

Version 0.2 provides a deterministic architecture path that does not require an LLM API key. The goal is to make schema validation, registry behavior, graph construction, routing, Evidence Judge logic, Safety Supervisor logic, and integration tests reproducible before introducing model variance.

## Environment

- Python >= 3.10
- Dependencies are declared in `pyproject.toml`
- Development dependencies include `pytest`

Install and run:

```bash
python3 -m pip install -e '.[dev]'
python3 demo.py
python3 real_demo.py
pytest -q
```

## What is deterministic

- structured Paper Skill fixtures;
- registry filters and exact-ID retrieval;
- current evidence-graph construction;
- rule-based Evidence Judge behavior;
- safety preflight and rule-based Safety Supervisor;
- demo serialization.

## What is not yet a benchmark result

Local runtime, latency, or graph-size telemetry from v0.2 must not be interpreted as evidence that Paper-as-Skill is faster or more accurate than any baseline. Scientific comparison begins only after matched system runners, a frozen corpus, expert gold labels, and a predefined evaluation protocol are in place.

## Future reproducibility requirements

The v0.3+ benchmark should record:
- corpus snapshot and source checksums;
- Paper Skill schema version;
- extraction model and prompt version, if used;
- retrieval configuration;
- base model and decoding parameters;
- token/API-call/latency telemetry;
- benchmark question IDs;
- gold claim-pair labels and adjudication status;
- software commit SHA.
