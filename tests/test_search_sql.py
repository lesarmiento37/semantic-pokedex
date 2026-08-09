import re

from pokedex.search.engine import build_search_sql


def test_build_search_sql_contains_vector_ordering_operator():
    sql, params = build_search_sql(
        strategy="v2",
        model="titan",
        filters={},
        top_k=10,
        ef_search=80,
    )
    assert "ORDER BY emb_v2_titan <=> %s::vector" in sql
    assert "SET LOCAL hnsw.ef_search = 80;" in sql
    assert len(params) == sql.count("%s")


def test_build_search_sql_adds_filter_clauses():
    sql, params = build_search_sql(
        strategy="v3",
        model="minilm",
        filters={"types": ["Water", "Ground"], "tier": ["OU", "UU"], "generation": [1, 2]},
        top_k=5,
        ef_search=40,
    )
    assert "types && %s::text[]" in sql
    assert "tier = ANY(%s)" in sql
    assert "generation = ANY(%s)" in sql
    assert "WHERE" in sql
    assert len(params) == sql.count("%s")


def test_placeholder_count_matches_parameter_count_when_filters_absent():
    sql, params = build_search_sql(
        strategy="v1",
        model="titan",
        filters={"types": [], "tier": [], "generation": []},
        top_k=7,
        ef_search=25,
    )
    placeholders = len(re.findall(r"%s", sql))
    assert placeholders == len(params)
