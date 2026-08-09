from __future__ import annotations

import re
from typing import Any

_ALLOWED_STRATEGIES = {"v1", "v2", "v3", "v4"}
_ALLOWED_MODELS = {"titan", "minilm"}
_IDENTIFIER_RE = re.compile(r"^[a-z0-9_]+$")
QUERY_VECTOR_SENTINEL = "__QUERY_VECTOR__"


def _validate_strategy_model(strategy: str, model: str) -> str:
    if strategy not in _ALLOWED_STRATEGIES:
        raise ValueError(f"Unsupported strategy: {strategy}")
    if model not in _ALLOWED_MODELS:
        raise ValueError(f"Unsupported model: {model}")
    column = f"emb_{strategy}_{model}"
    if not _IDENTIFIER_RE.match(column):
        raise ValueError("Computed embedding column is invalid")
    return column


def build_search_sql(
    strategy: str,
    model: str,
    filters: dict,
    top_k: int,
    ef_search: int,
) -> tuple[str, list[Any]]:
    if top_k < 1 or top_k > 100:
        raise ValueError("top_k must be between 1 and 100")
    if ef_search < 1 or ef_search > 10000:
        raise ValueError("ef_search must be between 1 and 10000")

    embedding_col = _validate_strategy_model(strategy, model)

    clauses: list[str] = []
    params: list[Any] = []

    type_filters = filters.get("types") or []
    tier_filters = filters.get("tier") or []
    generation_filters = filters.get("generation") or []

    if type_filters:
        clauses.append("types && %s::text[]")
        params.append(list(type_filters))

    if tier_filters:
        clauses.append("tier = ANY(%s)")
        params.append(list(tier_filters))

    if generation_filters:
        clauses.append("generation = ANY(%s)")
        params.append(list(generation_filters))

    where_sql = ""
    if clauses:
        where_sql = "WHERE " + " AND ".join(clauses)

    sql = (
        f"SET LOCAL hnsw.ef_search = {int(ef_search)};\n"
        f"SELECT id, name, generation, types, tier, 1 - ({embedding_col} <=> %s::vector) AS similarity\n"
        f"FROM pokemon\n"
        f"{where_sql}\n"
        f"ORDER BY {embedding_col} <=> %s::vector\n"
        f"LIMIT %s"
    )

    params.extend([QUERY_VECTOR_SENTINEL, QUERY_VECTOR_SENTINEL, int(top_k)])
    return sql, params
