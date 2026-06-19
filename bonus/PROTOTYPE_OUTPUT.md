# Prototype Output

## Pipeline

agent traces -> normalized request rows -> quality summary -> eval candidates

## Results

- Total traces: 8
- Total spans: 21
- Total tool calls: 6
- Eval candidates: 2
- RAG misses: 1
- Average latency ms: 1462.5
- Average total tokens: 465.5

## Status counts

- error: 3
- ok: 5

## Split counts

- eval: 2
- train_pool: 6

## Error type counts

- Hallucination: 1
- Refusal: 1
- ToolError: 1
- none: 5

## Generated files

- `bonus/prototype_quality_summary.csv`
- `bonus/prototype_eval_candidates.jsonl`
