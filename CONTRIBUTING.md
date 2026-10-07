# Contributing

Thanks for your interest in **CSRP Paper Skills**. This repository is a research prototype, so contributions should preserve scientific traceability and avoid implying clinical validity that has not been demonstrated.

## Development setup

```bash
git clone https://github.com/turboguan/csrp-paper-skills.git
cd csrp-paper-skills
python3 -m pip install -e '.[dev]'
pytest -q
```

## Contribution principles

1. **Provenance first.** New real-paper claims must point to a source span, page, table, figure, or another reproducible anchor.
2. **No silent causal upgrades.** Do not convert associations into causal claims.
3. **No fabricated benchmark results.** Telemetry is not evidence of architectural superiority.
4. **Safety-sensitive changes require explicit review.** The system must not autonomously generate individual suicide-risk scores or unsupported treatment recommendations.
5. **Prefer testable, minimal changes.** Add or update tests with implementation changes.

## Pull requests

Create a focused branch, run the full test suite, and explain scientific assumptions in the pull request. For evidence-family contributions, include the source record, claim-level provenance, relation labels, and adjudication status.

## Evidence relation labels

For matched claim pairs, use only:
- `SUPPORTS`
- `CONTRADICTS`
- `QUALIFIES`
- `NOT_COMPARABLE`
- `UNRELATED`

A relation should be justified by population, intervention/exposure, outcome, method, and timeframe—not lexical similarity alone.
