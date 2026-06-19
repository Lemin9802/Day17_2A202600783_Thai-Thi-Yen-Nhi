# Bonus Design — Observability-to-Training Data Pipeline for an E-commerce AI Agent

## 1. Problem & Real Constraints

This design is based on my Day 13 Observathon e-commerce agent. The agent answers customer questions about products, stock, coupons, shipping fees, and final order totals. In Day 13, the main engineering work was not only improving the prompt, but also adding an observability and mitigation wrapper around a black-box agent.

The production problem is: how do we turn agent behavior into reliable data for monitoring, evaluation, and future model training?

The raw inputs include user questions, agent answers, status codes, tool traces, token usage, latency, repeated tool actions, cache hits, PII redaction events, and diagnosis labels such as error spike, latency spike, cost blowup, quality drift, infinite loop, tool failure, PII leak, arithmetic error, tool overuse, fabrication, and prompt injection.

The real constraints are reliability, privacy, and evaluation honesty. Agent traces can be nested and messy. Some failures are silent: the request may return `status=ok`, but the answer can still be wrong due to arithmetic errors, fake prices from prompt injection, unsupported shipping, or hallucinated totals. The pipeline must preserve raw traces, validate required fields, quarantine bad records, and create clean datasets for evaluation and future DPO/SFT training.

## 2. Open Questions, Decisions, and Trade-offs

### Question 1 — What should be stored in Bronze, Silver, and Gold?

Decision: Bronze should store raw agent runs exactly as emitted: question, answer, status, timestamp, session, turn, metadata, and trace events. Silver should contain flattened spans, normalized fields, redacted text, validated tool calls, and per-request quality signals. Gold should contain evaluation examples, preference pairs, monitoring aggregates, and training-ready datasets.

Trade-off: Keeping raw Bronze data increases storage and privacy risk, but it is necessary for debugging and reproducibility. If the parser or labeling rules change, Silver and Gold can be rebuilt from raw traces.

### Question 2 — Should the pipeline be batch, streaming, or hybrid?

Decision: The first version should be hybrid. Full dataset generation can run in batch after each simulation or production window. Critical observability signals such as error rate, latency spike, repeated tool calls, and PII leak should be processed in streaming or micro-batch mode.

Trade-off: Streaming gives faster incident detection, but it adds operational complexity. Batch is simpler and more reproducible, but it may detect failures too late.

### Question 3 — What quality gates are needed before data reaches training?

Decision: The pipeline should validate required identifiers like `qid`, `session`, `turn`, `status`, and timestamp. It should also validate trace structure, tool-call counts, latency fields, token usage, and whether PII has been redacted. Records with missing IDs, malformed traces, unsafe text, or impossible metrics should go to quarantine.

Trade-off: Strict validation protects downstream training, but it may reject useful partial traces. Quarantine is better than silently dropping records because humans can review and fix the rules.

### Question 4 — How do we prevent train/eval contamination?

Decision: Evaluation prompts must be held out before generating training datasets. Preference pairs whose prompts overlap with the eval set should be removed by decontamination. This is especially important because Day 17 converts Day 13 traces into eval rows and DPO pairs.

Trade-off: Decontamination reduces training volume, but it keeps metrics honest. Without it, the model may memorize evaluation prompts and produce inflated offline results that do not transfer to production.

### Question 5 — How should observability labels become a feedback flywheel?

Decision: The pipeline should convert diagnosed failures into structured learning signals. For example, an arithmetic error can become a negative example; a corrected answer can become the preferred response; a prompt-injection failure can become an eval case; and a PII leak can become a safety test.

Trade-off: Automated labeling scales well, but some labels need human review. High-impact categories such as PII leak, prompt injection, and hallucinated totals should not rely only on automatic heuristics.

### Question 6 — What serving features need point-in-time correctness?

Decision: Features like user session history, recent failure rate, cache hit history, and rolling quality score must be joined with an ASOF or point-in-time guard. A request from 10:00 should not use corrections, labels, or future failures generated after 10:00.

Trade-off: Point-in-time joins are more complex than simple joins, but they prevent future leakage and training-serving skew.

## 3. Rejected Option

Rejected option: Only improve `prompt.txt` and `config.json`, while keeping no structured data pipeline.

Reason: This is too fragile. Prompt and config changes may improve one run, but they do not create durable observability, eval sets, preference pairs, quarantine, or reproducible training data. Without a pipeline, failures such as prompt injection, PII leak, arithmetic error, and quality drift may be rediscovered manually every time instead of becoming systematic tests and training signals.

## 4. Architecture Diagram

```text
E-commerce Agent
- user questions
- answers
- tool calls
- telemetry
- run_output.json
- traces
        |
        v
Bronze Layer
- raw runs
- raw traces
- raw telemetry logs
        |
        v
Validation + Quarantine
- required fields
- trace structure
- PII scan
- latency/token sanity checks
- tool-call consistency
        |
        v
Silver Layer
- flattened spans
- normalized requests
- redacted text
- per-request metrics
- diagnosis labels
        |
        v
Gold Layer
- eval_golden.jsonl
- preference_pairs.jsonl
- failure dashboards
- point-in-time features
- safety regression tests
        |
        v
Serving + Learning
- monitoring
- prompt regression tests
- SFT/DPO training
- future agent improvement
```

## 5. Optional Prototype

A minimal prototype would reuse the Day 17 pipeline shape. It would ingest a small `run_output.json`, flatten each result into request-level rows, validate required fields, quarantine malformed records, and output two datasets: an eval JSONL for held-out questions and a preference JSONL for corrected or preferred answers.

The current Day 17 lab already demonstrates the core pieces: Bronze/Silver/Gold order processing, trace-to-dataset flywheel, decontamination, point-in-time feature joins, RAG ingestion, and Knowledge Graph traversal. A production version would connect these pieces to real Day 13 agent telemetry and continuously turn observed failures into evaluation and training data.
## 6. Prototype Run

I also added a small runnable prototype in `bonus/prototype_observability.py`.

The prototype reads `data/traces/agent_traces.json`, recursively flattens nested spans, extracts request-level observability fields, and writes three bonus artifacts:

- `bonus/PROTOTYPE_OUTPUT.md`
- `bonus/prototype_quality_summary.csv`
- `bonus/prototype_eval_candidates.jsonl`

The run produced 8 normalized traces, 21 flattened spans, 6 tool calls, and 2 eval candidates. It also surfaced 1 RAG miss, 5 successful traces, and 3 error traces. This supports the design goal: converting raw agent observability into monitoring data and training/evaluation candidates.

## 7. Concrete Agent Improvement Brainstorm

The goal of this bonus is not only to store traces, but to use the pipeline to improve the e-commerce agent as much as possible.

### Improvement 1 — Grounded answers with policy retrieval

The agent should not answer returns, warranty, shipping, or coupon questions only from the prompt. It should retrieve the relevant policy or catalog chunk first, then answer with grounded facts. This reduces hallucination and makes policy changes easier to update.

### Improvement 2 — Deterministic tools for arithmetic and order totals

The agent should not calculate final prices, discounts, or shipping fees only with natural language reasoning. It should use deterministic tools for subtotal, coupon validation, shipping fee, and final total. This directly reduces arithmetic errors and fake totals.

### Improvement 3 — Prompt-injection resistance

The agent should treat user messages as untrusted input. If a user says “ignore previous policy” or invents a fake price, the agent should continue to use retrieved policy and tool outputs as the source of truth. Prompt-injection failures should become safety regression tests.

### Improvement 4 — PII protection

The wrapper should redact or block sensitive information before logs become training data. PII events should be counted, quarantined, and reviewed. This prevents private customer data from leaking into eval sets, preference pairs, or future fine-tuning datasets.

### Improvement 5 — Tool-use discipline

The agent should avoid repeated tool calls and infinite loops. The pipeline should track `n_tool_calls`, repeated actions, tool errors, and latency. When tool overuse appears, the case should become a debugging example and possibly a training signal.

### Improvement 6 — Better eval suite from observed failures

Every important failure category should become an eval group: arithmetic error, hallucination, refusal, tool failure, PII leak, prompt injection, quality drift, and RAG miss. This turns one-time bugs into permanent regression tests.

### Improvement 7 — Preference data for future DPO/SFT

When the agent gives a bad answer and a corrected answer exists, the pipeline should create a preference pair. The chosen answer should be grounded, policy-compliant, and concise. The rejected answer should preserve the original failure mode, such as hallucination or wrong arithmetic.

### Improvement 8 — Online monitoring and rollback

The agent should be monitored by error rate, latency, cost, tool failure rate, RAG miss rate, and unsafe-output rate. If a new prompt, config, or model version causes a spike, the system should rollback or flag the version for review.

### Improvement 9 — Knowledge Graph for multi-hop business logic

Flat vector retrieval is useful for direct lookup, but the agent also needs multi-hop reasoning. For example, “Where does a widget ship from?” requires connecting product → category → fulfillment center. A small Knowledge Graph can support these questions more reliably.

### Improvement 10 — Human-in-the-loop review

High-impact failures such as PII leak, prompt injection, hallucinated policy, or wrong order total should not be fully automated. The pipeline should route these records to human review before they become training data.
