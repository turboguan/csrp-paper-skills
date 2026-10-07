# Architecture-runner status

The four-arm benchmark interface exists, but only one deterministic architecture path is currently executable.

| Architecture | v0.3 status | Scientific-use status |
|---|---|---|
| RAG-only | adapter stub | not benchmark-ready |
| Monolithic agent | adapter stub | not benchmark-ready |
| One-paper-one-agent | adapter stub | not benchmark-ready |
| Paper-as-Skill | deterministic shared-workspace path | architecture dry-run only |

This is deliberate. The three baselines must be connected to the **same base model, corpus, retriever and resource budget** before any comparison is scientifically interpretable.

Run:

```bash
python scripts/v03_means_dry_run.py
```

The script records missing baselines as `not_ready`; it does not fabricate outputs or benchmark scores.
