from __future__ import annotations

from .base import RepresentationStrategy


class V2StructuredNL(RepresentationStrategy):
    name = "v2_structured_nl"

    @staticmethod
    def _band(value: int) -> str:
        if value < 55:
            return "low"
        if value < 85:
            return "moderate"
        return "high"

    def render(self, pokemon: dict) -> str:
        stats = pokemon.get("stats", {})
        hp = int(stats.get("hp", 0))
        atk = int(stats.get("atk", 0))
        defense = int(stats.get("def", 0))
        spa = int(stats.get("spa", 0))
        spd = int(stats.get("spd", 0))
        spe = int(stats.get("spe", 0))

        types = pokemon.get("types", [])
        generation = pokemon.get("generation", "unknown")
        tier = pokemon.get("tier", "unranked")

        return (
            f"{pokemon.get('name', 'Unknown')} is a generation {generation} Pokémon with "
            f"types {', '.join(types) if types else 'unknown'}. "
            f"Its durability is {self._band(hp)} HP and {self._band(defense)} physical defense, "
            f"with {self._band(spd)} special defense. "
            f"Its offensive profile is {self._band(atk)} physical attack and {self._band(spa)} special attack. "
            f"Its speed is {self._band(spe)}. "
            f"Competitive tier is {tier}."
        )
