from __future__ import annotations

import json
import logging
import os
from typing import Any

import boto3

from pokedex.db.client import get_connection

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in vector) + "]"


def _upsert_record(cur, item: dict[str, Any], strategy: str) -> None:
    pokemon = item["pokemon"]
    vector = item.get("embedding_titan", [])
    text_field = f"text_{strategy}"
    emb_field = f"emb_{strategy}_titan"

    sql = f"""
    INSERT INTO pokemon (id, name, generation, types, tier, stats, metadata, {text_field}, {emb_field})
    VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s::vector)
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        generation = EXCLUDED.generation,
        types = EXCLUDED.types,
        tier = EXCLUDED.tier,
        stats = EXCLUDED.stats,
        metadata = EXCLUDED.metadata,
        {text_field} = EXCLUDED.{text_field},
        {emb_field} = EXCLUDED.{emb_field}
    """

    cur.execute(
        sql,
        (
            int(pokemon["id"]),
            pokemon["name"],
            int(pokemon.get("generation", 1)),
            list(pokemon.get("types", [])),
            pokemon.get("tier"),
            json.dumps(pokemon.get("stats", {})),
            json.dumps({"source": "ingest"}),
            item["text"],
            _vector_literal(vector),
        ),
    )


def _save_eval_to_s3(event: dict[str, Any]) -> dict[str, Any]:
    bucket = os.getenv("S3_EVAL_BUCKET")
    if not bucket:
        return {"saved": False, "reason": "S3_EVAL_BUCKET not set"}
    key = event.get("key", "eval/results.json")
    boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=json.dumps(event).encode("utf-8"))
    return {"saved": True, "bucket": bucket, "key": key}


def handler(event: dict, context: Any) -> dict:
    del context
    event = event or {}

    try:
        if "aggregate" in event:
            return _save_eval_to_s3(event)

        strategy = event.get("strategy")
        embedded = event.get("embedded", [])
        with get_connection() as conn:
            with conn.cursor() as cur:
                for item in embedded:
                    _upsert_record(cur, item, strategy=strategy)

        return {"loaded": len(embedded), "strategy": strategy}
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("ingest_load_failed", extra={"error": str(exc)})
        raise
