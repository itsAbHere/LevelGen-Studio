"""
tests/test_generator.py

Unit tests for the generator — these test logic without hitting the real API.
Run with: python -m pytest tests/
"""

import json
import pytest

from src.generator import validate_level, VALID_ROOM_TYPES, VALID_MOODS, VALID_ENEMIES
from src.prompt_builder import build_user_prompt, SYSTEM_PROMPT


# --- Test: prompt builder ---

def test_system_prompt_not_empty():
    assert len(SYSTEM_PROMPT) > 100

def test_user_prompt_includes_story():
    prompt = "dark forest, 3 rooms, wolf boss"
    result = build_user_prompt(prompt)
    assert prompt in result


# --- Test: validate_level ---

def make_valid_level():
    """Returns a minimal valid level dict matching the agreed contract."""
    return {
        "level_title": "Test Level",
        "theme": "dungeon",
        "narrative_summary": "A test.",
        "rooms": [
            {"type": "entrance", "mood": "tense",    "enemies": "none",  "exits": 2},
            {"type": "corridor", "mood": "dark",     "enemies": "patrol","exits": 2},
            {"type": "boss",     "mood": "dramatic", "enemies": "boss",  "exits": 1},
        ],
        "connections": [[0, 1], [1, 2]]
    }

def test_valid_level_has_no_warnings():
    assert validate_level(make_valid_level()) == []

def test_missing_boss_room_raises_warning():
    level = make_valid_level()
    for room in level["rooms"]:
        room["type"] = "standard"
    level["rooms"][0]["type"] = "entrance"
    warnings = validate_level(level)
    assert any("boss" in w.lower() for w in warnings)

def test_invalid_room_type_raises_warning():
    level = make_valid_level()
    level["rooms"][1]["type"] = "combat"  # not in agreed list
    warnings = validate_level(level)
    assert any("invalid type" in w for w in warnings)

def test_invalid_mood_raises_warning():
    level = make_valid_level()
    level["rooms"][0]["mood"] = "spooky"  # not in agreed list
    warnings = validate_level(level)
    assert any("invalid mood" in w for w in warnings)

def test_bad_connection_index_raises_warning():
    level = make_valid_level()
    level["connections"] = [[0, 99]]  # room 99 doesn't exist
    warnings = validate_level(level)
    assert any("99" in w for w in warnings)

def test_first_room_must_be_entrance():
    level = make_valid_level()
    level["rooms"][0]["type"] = "standard"
    warnings = validate_level(level)
    assert any("entrance" in w for w in warnings)

def test_empty_rooms_raises_warning():
    assert validate_level({"rooms": []})