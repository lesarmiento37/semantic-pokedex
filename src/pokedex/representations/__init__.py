"""Text representation strategies for semantic retrieval."""

from .base import RepresentationStrategy
from .v1_raw_stats import V1RawStats
from .v2_structured_nl import V2StructuredNL
from .v3_role_oriented import V3RoleOriented
from .v4_llm_generated import V4LLMGenerated

STRATEGY_REGISTRY = {
    "v1": V1RawStats,
    "v2": V2StructuredNL,
    "v3": V3RoleOriented,
    "v4": V4LLMGenerated,
}

__all__ = [
    "RepresentationStrategy",
    "V1RawStats",
    "V2StructuredNL",
    "V3RoleOriented",
    "V4LLMGenerated",
    "STRATEGY_REGISTRY",
]
