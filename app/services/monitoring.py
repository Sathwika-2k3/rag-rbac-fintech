import json
from datetime import datetime, timezone

from app.config import PROJECT_ROOT

USAGE_LOG_PATH = PROJECT_ROOT / "resources" / "usage_log.jsonl"

# Groq's published per-token pricing for openai/gpt-oss-120b, in USD per token.
# Approximate — check https://groq.com/pricing for current rates before relying on
# this for real budgeting. Groq's free tier likely means the true cost today is $0;
# this exists to demonstrate how the calculation would work on a paid provider.
PRICE_PER_INPUT_TOKEN = 0.15 / 1_000_000
PRICE_PER_OUTPUT_TOKEN = 0.75 / 1_000_000

# Flag any single request using more tokens than this as unusually large.
HIGH_USAGE_TOKEN_THRESHOLD = 2000


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return input_tokens * PRICE_PER_INPUT_TOKEN + output_tokens * PRICE_PER_OUTPUT_TOKEN


def log_usage(role: str, question: str, input_tokens: int, output_tokens: int, latency_seconds: float) -> dict:
    total_tokens = input_tokens + output_tokens
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "role": role,
        "question": question,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(estimate_cost(input_tokens, output_tokens), 8),
        "latency_seconds": round(latency_seconds, 3),
        "high_usage_alert": total_tokens > HIGH_USAGE_TOKEN_THRESHOLD,
    }
    USAGE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with USAGE_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def get_usage_report() -> dict:
    if not USAGE_LOG_PATH.exists():
        return {
            "request_count": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "average_latency_seconds": 0.0,
            "high_usage_alerts": 0,
        }

    lines = [line for line in USAGE_LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    entries = [json.loads(line) for line in lines]
    request_count = len(entries)

    return {
        "request_count": request_count,
        "total_input_tokens": sum(e["input_tokens"] for e in entries),
        "total_output_tokens": sum(e["output_tokens"] for e in entries),
        "total_tokens": sum(e["total_tokens"] for e in entries),
        "estimated_cost_usd": round(sum(e["estimated_cost_usd"] for e in entries), 6),
        "average_latency_seconds": round(sum(e["latency_seconds"] for e in entries) / request_count, 3),
        "high_usage_alerts": sum(1 for e in entries if e["high_usage_alert"]),
    }
