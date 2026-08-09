from __future__ import annotations

from .base import RepresentationStrategy


class V3RoleOriented(RepresentationStrategy):
    name = "v3_role_oriented"

    def render(self, pokemon: dict) -> str:
        name = pokemon.get("name", "Unknown")
        tier = pokemon.get("tier", "unranked")

        role_value = pokemon.get("role", "pivot")
        if isinstance(role_value, list):
            role_text = ", ".join(role_value)
        else:
            role_text = str(role_value)

        hazards = pokemon.get("hazards", [])
        if isinstance(hazards, str):
            hazards = [hazards]

        resistances = pokemon.get("resistances", [])
        weaknesses = pokemon.get("weaknesses", [])

        hazard_clause = (
            f"It can provide hazard support with {', '.join(hazards)} as a hazard setter."
            if hazards
            else "It is not known as a dedicated hazard setter."
        )

        role_keywords = "wall sweeper setter pivot hazard"

        return (
            f"{name} is typically used in tier {tier} as a {role_text}. "
            f"This role profile highlights whether it behaves like a wall, sweeper, setter, or pivot. "
            f"{hazard_clause} "
            f"It resists {', '.join(resistances) if resistances else 'few key matchups'} "
            f"and is weak to {', '.join(weaknesses) if weaknesses else 'specific counters'}. "
            f"Role keywords: {role_keywords}."
        )
