from __future__ import annotations

import json
import logging
import os
from typing import Any

from pokedex.db.client import get_connection
from pokedex.embeddings.titan import embed
from pokedex.search.engine import QUERY_VECTOR_SENTINEL, build_search_sql

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def _response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload),
    }


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in vector) + "]"


def handler(event: dict, context: Any) -> dict:
    del context
    event = event or {}

    try:
        body = json.loads(event.get("body", "{}"))
        query = body.get("query", "").strip()
        if not query:
            return _response(400, {"error": "query is required"})

        strategy = body.get("strategy", "v1")
        model = body.get("model", "titan")
        top_k = int(body.get("top_k", 10))
        ef_search = int(body.get("ef_search", 40))
        filters = body.get("filters", {})

        query_vector = _vector_literal(embed(query))
        sql, params = build_search_sql(
            strategy=strategy,
            model=model,
            filters=filters,
            top_k=top_k,
            ef_search=ef_search,
        )
        params = [query_vector if p == QUERY_VECTOR_SENTINEL else p for p in params]
        set_sql, select_sql = sql.split(";\n", maxsplit=1)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(set_sql)
                cur.execute(select_sql, params)
                rows = cur.fetchall()

        results = [
            {
                "id": row[0],
                "name": row[1],
                "generation": row[2],
                "types": row[3],
                "tier": row[4],
                "similarity": float(row[5]),
            }
            for row in rows
        ]

        return _response(200, {"results": results, "count": len(results)})
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("search_failed", extra={"error": str(exc)})
        return _response(500, {"error": "internal server error"})
