from __future__ import annotations

import logging
import os
import time
from statistics import median
from typing import Any

from pokedex.db.client import get_connection
from pokedex.embeddings.titan import embed
from pokedex.search.engine import build_search_sql

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in vector) + "]"


def handler(event: dict, context: Any) -> dict:
    del context
    event = event or {}

    try:
        experiment = event.get("experiment", {})
        queries = event.get("queries", [])

        strategy = experiment.get("strategy", "v1")
        model = experiment.get("model", "titan")
        top_k = int(experiment.get("top_k", 10))
        ef_search = int(experiment.get("ef_search", 40))

        latencies_ms: list[float] = []
        hits = 0

        with get_connection() as conn:
            with conn.cursor() as cur:
                for query in queries:
                    started = time.perf_counter()
                    q_embedding = _vector_literal(embed(query["text"]))
                    sql, params = build_search_sql(
                        strategy=strategy,
                        model=model,
                        filters=query.get("filters", {}),
                        top_k=top_k,
                        ef_search=ef_search,
                    )
                    params[-3] = q_embedding
                    params[-2] = q_embedding
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                    latency_ms = (time.perf_counter() - started) * 1000
                    latencies_ms.append(latency_ms)

                    expected = set(query.get("expected_top_k", []))
                    found = {row[1] for row in rows}
                    if expected.intersection(found):
                        hits += 1

        recall = hits / len(queries) if queries else 0.0
        return {
            "experiment": experiment,
            "metrics": {
                "recall_at_k": recall,
                "mrr_at_k": 0.0,
                "p50_latency_ms": median(latencies_ms) if latencies_ms else 0.0,
            },
        }
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("eval_run_failed", extra={"error": str(exc)})
        raise
