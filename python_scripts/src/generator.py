"""
generator.py

Core module: sends prompts to Claude and parses the JSON response.
"""

import json
import os
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv

from src.prompt_builder import SYSTEM_PROMPT, build_user_prompt

# Load .env file if it exists (useful during local development)
load_dotenv()


def generate_level(story_prompt: str, model: str = "claude-opus-4-5") -> dict:
    """
    Takes a natural language story prompt and returns a structured
    room layout as a Python dict.

    Args:
        story_prompt: e.g. "abandoned castle, player is being hunted, 3 rooms"
        model: Claude model to use

    Returns:
        Parsed JSON dict representing the level layout

    Raises:
        ValueError: if the LLM returns invalid JSON
        anthropic.APIError: if the API call fails
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print(f"  Sending prompt to {model}...")

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": build_user_prompt(story_prompt)}
        ]
    )

    raw_text = message.content[0].text.strip()

    # Defensive: strip accidental markdown fences if the model adds them
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        # Remove first and last fence lines
        raw_text = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    try:
        level_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM returned invalid JSON.\nError: {e}\nRaw output:\n{raw_text}"
        ) from e

    return level_data


def save_level(level_data: dict, output_dir: str = "output", filename: Optional[str] = None) -> Path:
    """
    Saves a level dict to a JSON file in the output directory.

    Args:
        level_data: the parsed level dict
        output_dir: folder to save into
        filename: optional custom filename (auto-generated if None)

    Returns:
        Path to the saved file
    """
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    if filename is None:
        # Sanitize level title to create a safe filename
        title = level_data.get("level_title", "level").lower()
        safe_title = "".join(c if c.isalnum() else "_" for c in title)[:40]
        filename = f"{safe_title}.json"

    file_path = out_path / filename
    with open(file_path, "w") as f:
        json.dump(level_data, f, indent=2)

    return file_path


VALID_ROOM_TYPES = {"entrance", "standard", "corridor", "treasure", "boss"}
VALID_MOODS = {"tense", "dark", "dramatic", "calm", "eerie"}
VALID_ENEMIES = {"none", "patrol", "guard", "swarm", "boss"}


def validate_level(level_data: dict) -> list[str]:
    """
    Sanity checks on the generated level against the agreed contract with Unity side.
    Returns a list of warning strings (empty = all good).
    """
    warnings = []
    rooms = level_data.get("rooms", [])
    connections = level_data.get("connections", [])

    if not rooms:
        warnings.append("No rooms found in level data.")
        return warnings

    room_count = len(rooms)

    # Check room types and moods
    types_found = set()
    for i, room in enumerate(rooms):
        rtype = room.get("type")
        mood = room.get("mood")
        enemies = room.get("enemies")

        if rtype not in VALID_ROOM_TYPES:
            warnings.append(f"Room {i} has invalid type: '{rtype}'. Must be one of {VALID_ROOM_TYPES}")
        else:
            types_found.add(rtype)

        if mood not in VALID_MOODS:
            warnings.append(f"Room {i} has invalid mood: '{mood}'. Must be one of {VALID_MOODS}")

        if enemies not in VALID_ENEMIES:
            warnings.append(f"Room {i} has invalid enemies value: '{enemies}'. Must be one of {VALID_ENEMIES}")

    # First room must be entrance
    if rooms and rooms[0].get("type") != "entrance":
        warnings.append(f"Room 0 should be type 'entrance', got '{rooms[0].get('type')}'")

    # Exactly one boss room
    boss_rooms = [i for i, r in enumerate(rooms) if r.get("type") == "boss"]
    if len(boss_rooms) == 0:
        warnings.append("No boss room found.")
    elif len(boss_rooms) > 1:
        warnings.append(f"Multiple boss rooms found at indices: {boss_rooms}")

    # Validate connections are valid index pairs
    for conn in connections:
        if not (isinstance(conn, list) and len(conn) == 2):
            warnings.append(f"Invalid connection format: {conn}. Must be a pair like [0, 1]")
            continue
        a, b = conn
        if not (0 <= a < room_count):
            warnings.append(f"Connection references out-of-range room index: {a}")
        if not (0 <= b < room_count):
            warnings.append(f"Connection references out-of-range room index: {b}")

    return warnings