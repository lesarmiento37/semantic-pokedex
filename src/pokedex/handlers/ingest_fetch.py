from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import boto3
import requests

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def _fetch_pokeapi_records(limit: int = 251) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for pokemon_id in range(1, limit + 1):
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}", timeout=10)
        response.raise_for_status()
        payload = response.json()
        stats = {entry["stat"]["name"]: entry["base_stat"] for entry in payload.get("stats", [])}
        records.append(
            {
                "id": payload["id"],
                "name": payload["name"].title(),
                "generation": 1 if payload["id"] <= 151 else 2,
                "types": [t["type"]["name"].title() for t in payload.get("types", [])],
                "stats": {
                    "hp": stats.get("hp", 0),
                    "atk": stats.get("attack", 0),
                    "def": stats.get("defense", 0),
                    "spa": stats.get("special-attack", 0),
                    "spd": stats.get("special-defense", 0),
                    "spe": stats.get("speed", 0),
                },
            }
        )
    return records


def handler(event: dict, context: Any) -> dict:
    del context
    event = event or {}

    try:
        limit = int(event.get("limit", 251))
        records = _fetch_pokeapi_records(limit=limit)

        bucket = os.getenv("S3_RAW_BUCKET")
        key = f"pokemon/raw/{datetime.now(tz=timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        if bucket:
            boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=json.dumps(records).encode("utf-8"))

        return {"records": records, "strategies": ["v1", "v2", "v3", "v4"], "raw_s3_key": key}
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("ingest_fetch_failed", extra={"error": str(exc)})
        raise
