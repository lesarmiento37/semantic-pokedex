from __future__ import annotations

import json
from typing import Any

MODEL_ID = "amazon.titan-embed-text-v2:0"
TITAN_DIMENSIONS = 1024

_CLIENT = None


def _client():
    global _CLIENT  # noqa: PLW0603
    if _CLIENT is None:
        import boto3  # pylint: disable=import-outside-toplevel

        _CLIENT = boto3.client("bedrock-runtime")
    return _CLIENT


def _invoke(text: str) -> list[float]:
    payload: dict[str, Any] = {
        "inputText": text,
        "dimensions": TITAN_DIMENSIONS,
        "normalize": True,
    }
    response = _client().invoke_model(modelId=MODEL_ID, body=json.dumps(payload))
    body = json.loads(response["body"].read())
    vector = body.get("embedding")
    if not isinstance(vector, list) or len(vector) != TITAN_DIMENSIONS:
        raise ValueError("Titan embedding response does not contain a 1024-d vector")
    return [float(v) for v in vector]


def embed(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Text for embedding must be non-empty")
    return _invoke(text)


def embed_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return [embed(text) for text in texts]
