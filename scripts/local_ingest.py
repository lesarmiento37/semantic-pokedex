from __future__ import annotations

import argparse
import json
from pathlib import Path

from pokedex.representations.v1_raw_stats import V1RawStats
from pokedex.representations.v2_structured_nl import V2StructuredNL
from pokedex.representations.v3_role_oriented import V3RoleOriented
from pokedex.representations.v4_llm_generated import V4LLMGenerated


SAMPLE_DATA = [
    {
        "id": 25,
        "name": "Pikachu",
        "generation": 1,
        "types": ["Electric"],
        "tier": "NU",
        "role": "pivot",
        "hazards": ["None"],
        "resistances": ["Electric", "Flying", "Steel"],
        "weaknesses": ["Ground"],
        "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
    },
    {
        "id": 245,
        "name": "Suicune",
        "generation": 2,
        "types": ["Water"],
        "tier": "OU",
        "role": "wall",
        "hazards": ["None"],
        "resistances": ["Fire", "Water", "Ice", "Steel"],
        "weaknesses": ["Electric", "Grass"],
        "stats": {"hp": 100, "atk": 75, "def": 115, "spa": 90, "spd": 115, "spe": 85},
    },
]


def _load_records(path: Path | None) -> list[dict]:
    if path is None:
        return SAMPLE_DATA
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Input JSON must be a list of Pokémon dicts")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Render representation strategy samples locally")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional path to local Pokémon JSON list",
    )
    args = parser.parse_args()

    records = _load_records(args.input)
    strategies = [V1RawStats(), V2StructuredNL(), V3RoleOriented(), V4LLMGenerated()]

    for record in records:
        print(f"\n=== {record.get('name', 'Unknown')} ===")
        for strategy in strategies:
            print(f"[{strategy.name}] {strategy.render(record)}")


if __name__ == "__main__":
    main()
