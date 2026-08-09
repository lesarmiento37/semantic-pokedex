from __future__ import annotations

import json
import logging
from typing import Any

from .base import RepresentationStrategy

LOGGER = logging.getLogger(__name__)
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

PROMPT_TEMPLATE = """You are a competitive Pokémon analyst.
Write a concise retrieval-oriented description in English.
Focus on battle role, typing interactions, hazards, and practical fit.
Do not include markdown.

Pokemon payload:
{payload}
"""


class V4LLMGenerated(RepresentationStrategy):
    name = "v4_llm_generated"

    def __init__(self) -> None:
        self._client = None

    def _client_or_none(self):
        if self._client is not None:
            return self._client
        try:
            import boto3  # pylint: disable=import-outside-toplevel

            self._client = boto3.client("bedrock-runtime")
            return self._client
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Bedrock client unavailable: %s", exc)
            return None

    def _build_request(self, pokemon: dict[str, Any]) -> dict[str, Any]:
        prompt = PROMPT_TEMPLATE.format(payload=json.dumps(pokemon, ensure_ascii=False, sort_keys=True))
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 220,
            "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}],
        }

    def render(self, pokemon: dict) -> str:
        client = self._client_or_none()
        fallback = (
            f"{pokemon.get('name', 'Unknown')} competitive summary unavailable from Bedrock; "
            "using local placeholder for v4_llm_generated strategy."
        )
        if client is None:
            return fallback

        try:
            body = json.dumps(self._build_request(pokemon))
            response = client.invoke_model(modelId=MODEL_ID, body=body)
            payload = json.loads(response["body"].read())
            content = payload.get("content", [])
            if not content:
                return fallback
            text = content[0].get("text", "").strip()
            return text or fallback
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("Bedrock generation failed; using fallback placeholder: %s", exc)
            return fallback
