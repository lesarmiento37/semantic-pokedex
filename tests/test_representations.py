import pytest

from pokedex.representations.v1_raw_stats import V1RawStats
from pokedex.representations.v2_structured_nl import V2StructuredNL
from pokedex.representations.v3_role_oriented import V3RoleOriented
from pokedex.representations.v4_llm_generated import V4LLMGenerated


@pytest.fixture
def pikachu_dict():
    return {
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
    }


def test_v1_returns_non_empty_string(pikachu_dict):
    result = V1RawStats().render(pikachu_dict)
    assert isinstance(result, str)
    assert result.strip()


def test_v2_returns_non_empty_string_and_qualitative_words(pikachu_dict):
    result = V2StructuredNL().render(pikachu_dict)
    assert isinstance(result, str)
    assert result.strip()
    assert any(word in result.lower() for word in ["low", "moderate", "high"])


def test_v3_returns_non_empty_string_and_role_keywords(pikachu_dict):
    result = V3RoleOriented().render(pikachu_dict)
    assert isinstance(result, str)
    assert result.strip()
    keywords = ["wall", "sweeper", "setter", "pivot", "hazard"]
    assert any(keyword in result.lower() for keyword in keywords)


@pytest.mark.skip(reason="Requires Bedrock")
def test_v4_returns_non_empty_string(pikachu_dict):
    result = V4LLMGenerated().render(pikachu_dict)
    assert isinstance(result, str)
    assert result.strip()
