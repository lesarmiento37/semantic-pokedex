# Representation Strategies

This project intentionally compares four text representation strategies over the same Pokémon entities.

The objective is to study retrieval behavior differences attributable to representation shape, not only embedding model choice.

## Why representation matters

Vector retrieval quality is strongly affected by what we ask the model to encode.

Even with the same embedding model:

- terse numeric text can preserve precision but lose semantic nuance,
- natural-language templates improve matchability for user phrasing,
- role-focused descriptions help competitive search intents,
- LLM-generated context may capture richer trade-offs but can introduce variance.

## Strategy V1 — Raw stats string

**Module:** `v1_raw_stats.py`

### Idea

Create a compact deterministic line including:

- species name,
- base stats,
- types,
- generation,
- optional tier.

### Strengths

- deterministic and cheap,
- easy to debug,
- useful baseline.

### Weaknesses

- sparse semantics,
- weak alignment with natural-language intents,
- no explicit role context.

### Expected behavior

Likely good for exact-ish stat-driven queries, weaker for abstract role queries like “bulky pivot with hazard utility”.

## Strategy V2 — Structured natural language

**Module:** `v2_structured_nl.py`

### Idea

Use a template sentence with qualitative descriptors (`low`, `moderate`, `high`) inferred from numeric stats.

### Strengths

- still deterministic,
- better lexical overlap with user language,
- introduces interpretable stat bands.

### Weaknesses

- rule thresholds can be coarse,
- may lose raw numeric granularity.

### Expected behavior

Likely stronger than V1 for descriptive prompts and mixed stat-role queries.

## Strategy V3 — Role-oriented competitive prose

**Module:** `v3_role_oriented.py`

### Idea

Encode competitive metadata explicitly:

- role (wall, sweeper, pivot, hazard setter),
- hazards,
- resistances,
- weaknesses,
- tier.

### Strengths

- aligns directly with competitive query language,
- strongly expresses tactical identity.

### Weaknesses

- depends on metadata quality,
- can underperform if role labels are noisy.

### Expected behavior

Should perform best on intent-style competitive queries such as:

- “water tank that resists fairies and can set hazards”
- “fast cleaner that can pivot out”
- “defensive wall weak to electric but good into water”

## Strategy V4 — LLM-generated analysis

**Module:** `v4_llm_generated.py`

### Idea

Prompt Claude Haiku to produce concise competitive analysis from structured attributes.

### Strengths

- can synthesize implicit relations,
- can produce richer semantic descriptors,
- may improve recall for nuanced prompts.

### Weaknesses

- non-deterministic outputs,
- higher latency/cost,
- depends on prompt quality,
- fallback behavior required when model access is unavailable.

### Expected behavior

Potentially strongest on nuanced, compositional queries if prompts are stable and generation quality is consistent. However, variance can reduce reproducibility.

## Hypothesis summary

If metadata quality is sufficient:

1. **V3** should be strongest for competitive-role prompts.
2. **V4** may tie or beat V3 on nuanced phrasing but with higher cost/variance.
3. **V2** should outperform V1 for most natural-language search intents.
4. **V1** remains a useful deterministic baseline.

## How to evaluate fairly

To compare strategies rigorously:

- use the same query set,
- keep ANN/search settings controlled,
- compare both Titan and MiniLM where applicable,
- collect recall@10 and MRR@10,
- record p50/p95 latency and cost signals.

## Practical recommendation for early iterations

Start with V2 and V3 for low-variance wins, then add V4 when budget and latency headroom allow deeper experimentation.
