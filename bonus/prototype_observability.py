from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
TRACES_PATH = ROOT / "data" / "traces" / "agent_traces.json"
OUT_DIR = ROOT / "bonus"

SUMMARY_CSV = OUT_DIR / "prototype_quality_summary.csv"
EVAL_JSONL = OUT_DIR / "prototype_eval_candidates.jsonl"
OUTPUT_MD = OUT_DIR / "PROTOTYPE_OUTPUT.md"


def load_traces(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict) and "traces" in data:
        return data["traces"]

    raise ValueError("Unsupported traces format")


def walk_spans(span: dict[str, Any]) -> list[dict[str, Any]]:
    out = [span]
    for child in span.get("children", []):
        out.extend(walk_spans(child))
    return out


def span_tokens(span: dict[str, Any]) -> int:
    attrs = span.get("attributes", {})
    return int(attrs.get("gen_ai.usage.input_tokens", 0) or 0) + int(
        attrs.get("gen_ai.usage.output_tokens", 0) or 0
    )


def normalize_trace(trace: dict[str, Any]) -> dict[str, Any]:
    attrs = trace.get("attributes", {})
    spans = walk_spans(trace)

    total_tokens = sum(span_tokens(span) for span in spans)
    tool_calls = [
        span
        for span in spans
        if "tool.name" in span.get("attributes", {})
    ]

    status = trace.get("status", "unknown")
    error_type = attrs.get("error.type", "")

    return {
        "trace_id": trace.get("trace_id", ""),
        "root_span_id": trace.get("span_id", ""),
        "session_id": attrs.get("session.id", ""),
        "user_id": attrs.get("user.id", ""),
        "user_input": attrs.get("input", ""),
        "agent_output": attrs.get("output", ""),
        "status": status,
        "error_type": error_type,
        "split": attrs.get("split", "train_pool"),
        "latency_ms": int(trace.get("duration_ms", 0) or 0),
        "total_tokens": total_tokens,
        "n_spans": len(spans),
        "n_tool_calls": len(tool_calls),
        "has_error": status != "ok",
        "has_rag_miss": any(
            span.get("attributes", {}).get("rag.hit") is False
            for span in spans
        ),
    }


def build_eval_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []

    for row in rows:
        if row["split"] == "eval" and row["user_input"] and row["agent_output"]:
            candidates.append(
                {
                    "id": row["trace_id"],
                    "prompt": row["user_input"],
                    "expected_response": row["agent_output"],
                    "metadata": {
                        "status": row["status"],
                        "error_type": row["error_type"],
                        "latency_ms": row["latency_ms"],
                        "total_tokens": row["total_tokens"],
                        "n_spans": row["n_spans"],
                    },
                }
            )

    return candidates


def write_summary_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "trace_id",
        "session_id",
        "user_id",
        "status",
        "error_type",
        "split",
        "latency_ms",
        "total_tokens",
        "n_spans",
        "n_tool_calls",
        "has_error",
        "has_rag_miss",
    ]

    with SUMMARY_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fieldnames})


def write_eval_jsonl(candidates: list[dict[str, Any]]) -> None:
    with EVAL_JSONL.open("w", encoding="utf-8") as f:
        for item in candidates:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def write_output_md(rows: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> None:
    status_counts = Counter(row["status"] for row in rows)
    split_counts = Counter(row["split"] for row in rows)
    error_counts = Counter(row["error_type"] or "none" for row in rows)

    avg_latency = round(
        sum(float(row["latency_ms"] or 0) for row in rows) / max(len(rows), 1),
        2,
    )
    avg_tokens = round(
        sum(float(row["total_tokens"] or 0) for row in rows) / max(len(rows), 1),
        2,
    )
    total_spans = sum(int(row["n_spans"]) for row in rows)
    total_tool_calls = sum(int(row["n_tool_calls"]) for row in rows)
    rag_misses = sum(1 for row in rows if row["has_rag_miss"])

    lines = [
        "# Prototype Output",
        "",
        "## Pipeline",
        "",
        "agent traces -> normalized request rows -> quality summary -> eval candidates",
        "",
        "## Results",
        "",
        f"- Total traces: {len(rows)}",
        f"- Total spans: {total_spans}",
        f"- Total tool calls: {total_tool_calls}",
        f"- Eval candidates: {len(candidates)}",
        f"- RAG misses: {rag_misses}",
        f"- Average latency ms: {avg_latency}",
        f"- Average total tokens: {avg_tokens}",
        "",
        "## Status counts",
        "",
    ]

    for key, value in sorted(status_counts.items()):
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Split counts", ""])

    for key, value in sorted(split_counts.items()):
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Error type counts", ""])

    for key, value in sorted(error_counts.items()):
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Generated files",
            "",
            "- `bonus/prototype_quality_summary.csv`",
            "- `bonus/prototype_eval_candidates.jsonl`",
        ]
    )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    traces = load_traces(TRACES_PATH)
    rows = [normalize_trace(trace) for trace in traces]
    candidates = build_eval_candidates(rows)

    write_summary_csv(rows)
    write_eval_jsonl(candidates)
    write_output_md(rows, candidates)

    print("=== Bonus prototype: observability-to-training data ===")
    print(f"traces in                 : {len(rows)}")
    print(f"spans flattened            : {sum(row['n_spans'] for row in rows)}")
    print(f"eval candidates            : {len(candidates)}")
    print(f"quality summary written to : {SUMMARY_CSV}")
    print(f"eval jsonl written to      : {EVAL_JSONL}")
    print(f"markdown output written to : {OUTPUT_MD}")


if __name__ == "__main__":
    main()
