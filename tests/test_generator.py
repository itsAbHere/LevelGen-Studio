"""
tests/test_generator.py

Unit tests for the generator — these test logic without hitting the real API.
Run with: python -m pytest tests/
"""

import json
import pytest

from src.generator import validate_level
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
    """Returns a minimal valid level dict for testing."""
    return {
        "level_title": "Test Level",
        "theme": "dungeon",
        "narrative_summary": "A test.",
        "rooms": [
            {
                "id": "room_1",
                "name": "Start",
                "type": "start",
                "description": "You begin here.",
                "enemies": [],
                "items": [],
                "is_boss_room": False,
                "connections": ["room_2"]
            },
            {
                "id": "room_2",
                "name": "Boss Lair",
                "type": "boss",
                "description": "The boss awaits.",
                "enemies": ["Dragon"],
                "items": ["Key"],
                "is_boss_room": True,
                "connections": []
            }
        ]
    }

def test_valid_level_has_no_warnings():
    level = make_valid_level()
    warnings = validate_level(level)
    assert warnings == []

def test_missing_boss_room_raises_warning():
    level = make_valid_level()
    for room in level["rooms"]:
        room["is_boss_room"] = False
    warnings = validate_level(level)
    assert any("boss" in w.lower() for w in warnings)

def test_bad_connection_raises_warning():
    level = make_valid_level()
    level["rooms"][0]["connections"] = ["room_999"]  # doesn't exist
    warnings = validate_level(level)
    assert any("room_999" in w for w in warnings)

def test_empty_rooms_raises_warning():
    level = {"rooms": []}
    warnings = validate_level(level)
    assert warnings
