from __future__ import annotations

import logging
import os
from statistics import mean
from typing import Any

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def handler(event: dict, context: Any) -> dict:
    del context
    event = event or {}

    try:
        shards = event.get("results", event.get("FanOut", []))
        if not shards and isinstance(event.get("Payload"), list):
            shards = event["Payload"]

        recalls = [float(shard.get("metrics", {}).get("recall_at_k", 0.0)) for shard in shards]
        p50s = [float(shard.get("metrics", {}).get("p50_latency_ms", 0.0)) for shard in shards]

        aggregate = {
            "total_runs": len(shards),
            "avg_recall_at_k": mean(recalls) if recalls else 0.0,
            "avg_p50_latency_ms": mean(p50s) if p50s else 0.0,
            "runs": shards,
        }
        return {"aggregate": aggregate, "key": "eval/aggregate.json"}
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("eval_aggregate_failed", extra={"error": str(exc)})
        raise
