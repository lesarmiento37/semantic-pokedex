from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import boto3

from pokedex.representations import STRATEGY_REGISTRY

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))


ROLE_DEFAULTS = {
    "hazards": ["Stealth Rock"],
    "resistances": ["Water", "Electric"],
    "weaknesses": ["Ground"],
    "role": "pivot",
    "tier": "OU",
}


def _enrich(record: dict[str, Any]) -> dict[str, Any]:
    merged = dict(record)
    for key, value in ROLE_DEFAULTS.items():
        merged.setdefault(key, value)
    return merged


def handler(event: dict, context: Any) -> dict:
    del context
    event = event or {}

    try:
        strategy_name = event.get("strategy", "v1")
        records = event.get("records", [])

        if strategy_name not in STRATEGY_REGISTRY:
            raise ValueError(f"Unsupported strategy '{strategy_name}'. Expected one of: v1, v2, v3, v4")

        strategy_class = STRATEGY_REGISTRY[strategy_name]
        strategy = strategy_class()

        represented: list[dict[str, Any]] = []
        for record in records:
            enriched = _enrich(record)
            represented.append(
                {
                    "id": enriched["id"],
                    "strategy": strategy_name,
                    "pokemon": enriched,
                    "text": strategy.render(enriched),
                }
            )

        bucket = os.getenv("S3_CURATED_BUCKET")
        if bucket:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            key = f"pokemon/curated/{strategy_name}/{timestamp}.json"
            boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=json.dumps(represented).encode("utf-8"))

        return {"strategy": strategy_name, "represented": represented}
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("ingest_represent_failed", extra={"error": str(exc)})
        raise
