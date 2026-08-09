# Evaluation Methodology

This folder contains query templates and guidance for measuring semantic retrieval quality.

## Ground-truth labeling

Use manual relevance judgments for each query:

1. Write realistic natural-language intent queries.
2. For each query, define expected relevant Pokémon candidates.
3. Keep labels consistent across runs to compare strategy/model settings fairly.

### Recommended labeling process

- Start with 30 total queries.
- Ensure diversity:
  - offense,
  - defense,
  - utility,
  - hazard interactions,
  - type synergy,
  - speed control,
  - role flexibility.
- For each query, store expected top candidates in `expected_top_k`.

## Metrics

### Recall@10

Recall@10 answers: “Did the top-10 contain relevant choices?”

A practical implementation can use either:

- binary hit if any expected label appears in top-10, or
- strict fraction of expected labels recovered in top-10.

Be explicit about which definition is used.

### MRR@10

Mean Reciprocal Rank focuses on how early the first relevant answer appears.

For each query:

- reciprocal rank = `1 / rank_of_first_relevant`,
- if no relevant item in top-10, value = 0.

Aggregate by averaging across all queries.

## Latency reporting

For each experimental configuration, collect:

- p50 latency,
- p95 latency,
- optional p99 if needed.

Capture latency in milliseconds and track alongside quality metrics.

## Experiment matrix suggestions

Run combinations over:

- representation strategy (`v1`, `v2`, `v3`, `v4`),
- embedding model (`titan`, `minilm` where supported),
- HNSW `ef_search` settings,
- retrieval `top_k` values.

Keep one variable controlled when testing another to isolate effects.
