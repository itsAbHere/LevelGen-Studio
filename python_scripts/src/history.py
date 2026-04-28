"""
history.py

Manages a persistent log of all generated levels.
Saves to output/history.json
"""

import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("output/history.json")


def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_to_history(prompt: str, level_data: dict) -> dict:
    history = load_history()

    entry = {
        "id": len(history) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "prompt": prompt,
        "archetype": level_data.get("archetype", "UNKNOWN"),
        "level_title": level_data.get("level_title", "Untitled"),
        "room_count": len(level_data.get("rooms", [])),
        "level": level_data
    }

    history.insert(0, entry)
    history = history[:50]

    HISTORY_FILE.parent.mkdir(exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    return entry