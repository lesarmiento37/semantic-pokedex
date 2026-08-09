from __future__ import annotations

import logging
import os
from typing import Any

from pokedex.embeddings.titan import embed_batch

LOGGER = logging.getLogger()
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def handler(event: dict, context: Any) -> dict:
    del context
    event = event or {}

    try:
        represented = event.get("represented", [])
        texts = [entry["text"] for entry in represented]
        vectors = embed_batch(texts)

        enriched = []
        for entry, vector in zip(represented, vectors, strict=True):
            enriched.append({**entry, "embedding_titan": vector})

        return {"strategy": event.get("strategy"), "embedded": enriched}
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("ingest_embed_failed", extra={"error": str(exc)})
        raise
