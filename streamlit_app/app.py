from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

st.set_page_config(page_title="Semantic Pokédex", layout="wide")
st.title("Semantic Pokédex")
st.caption("Semantic search over Pokémon with strategy and ANN controls")

search_api_url = os.getenv("SEARCH_API_URL", "").strip()

with st.sidebar:
    st.header("Filters")
    types_filter = st.multiselect(
        "Types",
        options=[
            "Normal",
            "Fire",
            "Water",
            "Electric",
            "Grass",
            "Ice",
            "Fighting",
            "Poison",
            "Ground",
            "Flying",
            "Psychic",
            "Bug",
            "Rock",
            "Ghost",
            "Dragon",
            "Dark",
            "Steel",
            "Fairy",
        ],
    )
    generation_filter = st.multiselect("Generation", options=[1, 2], default=[1, 2])
    tier_filter = st.multiselect("Tier", options=["OU", "UU", "RU", "NU", "Ubers", "LC"], default=[])

    strategy = st.selectbox("Representation strategy", options=["v1", "v2", "v3", "v4"], index=2)
    model = st.selectbox("Embedding model", options=["titan", "minilm"], index=0)
    ef_search = st.slider("HNSW ef_search", min_value=10, max_value=200, value=40, step=5)
    top_k = st.slider("Top K", min_value=1, max_value=30, value=10, step=1)

query = st.text_input("Query", placeholder="water tank that resists fairies and can set hazards")
run = st.button("Search", type="primary")


def _mock_response(payload: dict[str, Any]) -> dict[str, Any]:
    q = payload.get("query", "")
    return {
        "results": [
            {
                "name": "Swampert",
                "types": ["Water", "Ground"],
                "similarity": 0.92,
                "summary": f"Mock result for query: {q}",
            },
            {
                "name": "Empoleon",
                "types": ["Water", "Steel"],
                "similarity": 0.88,
                "summary": "Mock fallback when SEARCH_API_URL is not configured.",
            },
        ]
    }


if run:
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        payload = {
            "query": query,
            "strategy": strategy,
            "model": model,
            "ef_search": ef_search,
            "top_k": top_k,
            "filters": {
                "types": types_filter,
                "generation": generation_filter,
                "tier": tier_filter,
            },
        }

        with st.spinner("Running semantic search..."):
            if search_api_url:
                try:
                    response = requests.post(search_api_url, json=payload, timeout=15)
                    response.raise_for_status()
                    data = response.json()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Search API request failed: {exc}")
                    data = {"results": []}
            else:
                data = _mock_response(payload)

        results = data.get("results", [])
        st.subheader(f"Results ({len(results)})")

        if not results:
            st.info("No results returned.")

        for idx, result in enumerate(results, start=1):
            with st.container(border=True):
                st.markdown(f"### {idx}. {result.get('name', 'Unknown')}")
                st.write(f"Types: {', '.join(result.get('types', []))}")
                st.write(f"Similarity: {result.get('similarity', 0):.4f}")
                if result.get("summary"):
                    st.caption(result["summary"])
