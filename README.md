# Day 17 Track 2 - Submission Summary

## Student Work Summary

This submission completes the Day 17 Track 2 Data Pipeline Lab. It includes the core Medallion-style data pipeline, validation and quarantine flow, Silver deduplication, Gold aggregation, streaming idempotency, agent trace flywheel, point-in-time feature correctness, RAG ingestion, Knowledge Graph demo, dbt optional track, and a bonus agent-improvement design with a runnable prototype.

## Final Status

| Area | Status |
|---|---|
| Core pipeline | PASS |
| `verify.py` | 16/16 checks - ALL PASS |
| Pytest | 18 passed |
| dbt optional track | PASS=11, ERROR=0 |
| Generated datasets | Included |
| Reflection | Included |
| Bonus design | Included |
| Bonus prototype | Included |

## Core Verification

Command:

```powershell
python verify.py
```

Result:

```text
RESULT: 16/16 checks - ALL PASS
```

Saved output:

```text
submission/VERIFY_OUTPUT.md
```

The verification covers raw order extraction, validation and quarantine, Silver deduplication, Gold aggregation, streaming idempotency, document ingestion, agent trace flywheel, eval set generation, preference-pair decontamination, point-in-time ASOF feature joins, Knowledge Graph construction, multi-hop graph query, and the vector RAG limitation on multi-hop retrieval.

## Test Results

Command:

```powershell
python -m pytest -q
```

Result:

```text
18 passed
```

Saved output:

```text
submission/PYTEST_OUTPUT.md
```

## dbt Optional Track

Command:

```powershell
cd dbt_project
$env:DBT_PROFILES_DIR="."
dbt build
```

Result:

```text
Completed successfully
PASS=11 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=11
```

Saved output:

```text
submission/DBT_BUILD_OUTPUT.md
```

The dbt build includes 1 seed, 2 models, 7 data tests, and 1 unit test.

## Generated Datasets

The agent trace flywheel generated the required datasets:

```text
datasets/eval_golden.jsonl
datasets/preference_pairs.jsonl
```

Summary:

- `eval_golden.jsonl`: 2 eval rows
- `preference_pairs.jsonl`: 1 clean preference pair after decontamination

## Reflection

The required reflection is included at:

```text
submission/REFLECTION.md
```

It answers the four required prompts: flywheel failure mode, decontamination risk, point-in-time leakage, and graph vs vector retrieval.

## Bonus Work

The bonus work is included in:

```text
bonus/DESIGN.md
```

Bonus topic:

```text
Observability-to-Training Data Pipeline for an E-commerce AI Agent
```

The bonus is based on the Day 13 Observathon e-commerce agent and brainstorms how to improve the agent using observability, evaluation, data flywheel, safety regression tests, preference data, monitoring, and future SFT/DPO training.

The design includes Bronze/Silver/Gold architecture for agent traces, quality gates, quarantine, train/eval decontamination, point-in-time correctness, feedback flywheel, a rejected design option, an architecture diagram, a Concrete Agent Improvement Brainstorm, and a runnable prototype.

## Bonus Prototype

A small runnable prototype is included:

```text
bonus/prototype_observability.py
```

Command:

```powershell
python bonus/prototype_observability.py
```

Result:

```text
traces in                 : 8
spans flattened            : 21
eval candidates            : 2
```

Generated prototype files:

```text
bonus/PROTOTYPE_OUTPUT.md
bonus/prototype_quality_summary.csv
bonus/prototype_eval_candidates.jsonl
```

The prototype reads `data/traces/agent_traces.json`, recursively flattens nested spans, extracts request-level observability fields, produces a quality summary, and produces eval candidate JSONL.

## Important Files for Grading

```text
submission/REFLECTION.md
submission/VERIFY_OUTPUT.md
submission/PYTEST_OUTPUT.md
submission/DBT_BUILD_OUTPUT.md

datasets/eval_golden.jsonl
datasets/preference_pairs.jsonl

bonus/DESIGN.md
bonus/prototype_observability.py
bonus/PROTOTYPE_OUTPUT.md
bonus/prototype_eval_candidates.jsonl
bonus/prototype_quality_summary.csv
```

## Recommended Reproduction Commands

From the repository root:

```powershell
python verify.py
python -m pytest -q
python flywheel.py
python kg_demo.py
python bonus/prototype_observability.py
```

For dbt:

```powershell
cd dbt_project
$env:DBT_PROFILES_DIR="."
dbt build
```

---
