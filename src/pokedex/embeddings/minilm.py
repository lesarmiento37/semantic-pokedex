# NOTE: Do not import this module inside AWS Lambda handlers.
from __future__ import annotations

from typing import Any

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_MINILM_MODEL: Any = None


def _model():
    global _MINILM_MODEL  # noqa: PLW0603
    if _MINILM_MODEL is None:
        from sentence_transformers import SentenceTransformer  # pylint: disable=import-outside-toplevel

        _MINILM_MODEL = SentenceTransformer(MODEL_NAME)
    return _MINILM_MODEL


def embed(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Text for embedding must be non-empty")
    vector = _model().encode(text, normalize_embeddings=True)
    vector_list = vector.tolist() if hasattr(vector, "tolist") else list(vector)
    if len(vector_list) != 384:
        raise ValueError("MiniLM embedding response does not contain a 384-d vector")
    return [float(v) for v in vector_list]
