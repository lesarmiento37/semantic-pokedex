from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any

import boto3
import requests

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def _generation_from_id(pokemon_id: int) -> int:
    if pokemon_id <= 151:
        return 1
    if pokemon_id <= 251:
        return 2
    if pokemon_id <= 386:
        return 3
    if pokemon_id <= 493:
        return 4
    if pokemon_id <= 649:
        return 5
    if pokemon_id <= 721:
        return 6
    if pokemon_id <= 809:
        return 7
    if pokemon_id <= 905:
        return 8
    return 9


def _fetch_pokeapi_records(limit: int = 251) -> list[dict[str, Any]]:
    def _fetch_one(pokemon_id: int) -> dict[str, Any]:
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}", timeout=10)
        response.raise_for_status()
        payload = response.json()
        stats = {entry["stat"]["name"]: entry["base_stat"] for entry in payload.get("stats", [])}
        return {
            "id": payload["id"],
            "name": payload["name"].title(),
            "generation": _generation_from_id(payload["id"]),
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

    records: list[dict[str, Any]] = []
    errors: list[tuple[int, str]] = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        future_by_id = {executor.submit(_fetch_one, pokemon_id): pokemon_id for pokemon_id in range(1, limit + 1)}
        for future in as_completed(future_by_id):
            pokemon_id = future_by_id[future]
            try:
                records.append(future.result())
            except Exception as exc:  # noqa: BLE001
                errors.append((pokemon_id, str(exc)))
                LOGGER.warning("pokemon_fetch_failed", extra={"pokemon_id": pokemon_id, "error": str(exc)})

    if errors:
        LOGGER.warning("partial_fetch_with_errors", extra={"failed_records": len(errors), "total": limit})
    if not records:
        raise RuntimeError("Failed to fetch all Pokémon records")

    records.sort(key=lambda item: item["id"])
    return records


def handler(event: dict, context: Any) -> dict:
    del context
    event = event or {}

    try:
        limit = int(event.get("limit", 251))
        records = _fetch_pokeapi_records(limit=limit)

        bucket = os.getenv("S3_RAW_BUCKET")
        key = f"pokemon/raw/{datetime.now(tz=timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        persisted = False
        if bucket:
            boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=json.dumps(records).encode("utf-8"))
            persisted = True

        return {
            "records": records,
            "strategies": ["v1", "v2", "v3", "v4"],
            "raw_s3_key": key if persisted else None,
            "raw_s3_persisted": persisted,
        }
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("ingest_fetch_failed", extra={"error": str(exc)})
        raise
