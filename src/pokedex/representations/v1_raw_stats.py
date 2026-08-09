from __future__ import annotations

from .base import RepresentationStrategy


class V1RawStats(RepresentationStrategy):
    name = "v1_raw_stats"

    def render(self, pokemon: dict) -> str:
        stats = pokemon.get("stats", {})
        types = "/".join(pokemon.get("types", [])) or "Unknown"
        return (
            f"{pokemon.get('name', 'Unknown')} "
            f"HP:{stats.get('hp', 0)} "
            f"ATK:{stats.get('atk', 0)} "
            f"DEF:{stats.get('def', 0)} "
            f"SPA:{stats.get('spa', 0)} "
            f"SPD:{stats.get('spd', 0)} "
            f"SPE:{stats.get('spe', 0)} "
            f"Types:{types}"
        )
