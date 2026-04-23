"""
generator.py

Core module: sends prompts to GitHub Models (GPT-4o) and parses the JSON response.
Uses OpenAI-compatible SDK pointed at GitHub's endpoint.
"""

import json
import os
from pathlib import Path
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

from src.prompt_builder import SYSTEM_PROMPT, build_user_prompt

load_dotenv()

VALID_ROOM_TYPES = {"entrance", "standard", "corridor", "treasure", "boss"}
VALID_MOODS = {"tense", "dark", "dramatic", "calm", "eerie"}
VALID_ENEMIES = {"none", "patrol", "guard", "swarm", "boss"}


def generate_level(story_prompt: str) -> dict:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=os.getenv("GITHUB_TOKEN")
    )

    print("  Sending prompt to GitHub Models (gpt-4o)...")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(story_prompt)}
        ]
    )

    raw_text = response.choices[0].message.content.strip()

    # Defensive: strip accidental markdown fences
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        raw_text = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

    try:
        level_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM returned invalid JSON.\nError: {e}\nRaw output:\n{raw_text}"
        ) from e

    return level_data


def save_level(level_data: dict, output_dir: str = "output", filename: Optional[str] = None) -> Path:
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    if filename is None:
        title = level_data.get("level_title", "level").lower()
        safe_title = "".join(c if c.isalnum() else "_" for c in title)[:40]
        filename = f"{safe_title}.json"

    file_path = out_path / filename
    with open(file_path, "w") as f:
        json.dump(level_data, f, indent=2)

    return file_path


def validate_level(level_data: dict) -> list[str]:
    warnings = []
    rooms = level_data.get("rooms", [])
    connections = level_data.get("connections", [])

    if not rooms:
        warnings.append("No rooms found in level data.")
        return warnings

    room_count = len(rooms)

    for i, room in enumerate(rooms):
        rtype = room.get("type")
        mood = room.get("mood")
        enemies = room.get("enemies")

        if rtype not in VALID_ROOM_TYPES:
            warnings.append(f"Room {i} has invalid type: '{rtype}'. Must be one of {VALID_ROOM_TYPES}")
        if mood not in VALID_MOODS:
            warnings.append(f"Room {i} has invalid mood: '{mood}'. Must be one of {VALID_MOODS}")
        if enemies not in VALID_ENEMIES:
            warnings.append(f"Room {i} has invalid enemies value: '{enemies}'. Must be one of {VALID_ENEMIES}")

    if rooms[0].get("type") != "entrance":
        warnings.append(f"Room 0 should be type 'entrance', got '{rooms[0].get('type')}'")

    boss_rooms = [i for i, r in enumerate(rooms) if r.get("type") == "boss"]
    if len(boss_rooms) == 0:
        warnings.append("No boss room found.")
    elif len(boss_rooms) > 1:
        warnings.append(f"Multiple boss rooms found at indices: {boss_rooms}")

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