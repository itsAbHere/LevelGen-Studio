"""
main.py

Entry point. Run this to generate a level from a prompt.

Usage:
    python main.py
    python main.py --prompt "dark forest, 4 rooms, wolf boss"
"""

import argparse
import json
import sys

from src.generator import generate_level, save_level, validate_level

DEFAULT_PROMPT = "abandoned castle, player is being hunted, 3 rooms, final room has a boss"


def main():
    parser = argparse.ArgumentParser(description="Narrative Level Generator")
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Story prompt to generate a level from"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Directory to save the JSON output (default: output/)"
    )
    args = parser.parse_args()

    # If no --prompt flag, use default or ask interactively
    if args.prompt:
        prompt = args.prompt
    else:
        print("Narrative Level Generator")
        print("=" * 40)
        print(f"Default prompt: {DEFAULT_PROMPT}")
        user_input = input("\nEnter your own prompt (or press Enter to use default): ").strip()
        prompt = user_input if user_input else DEFAULT_PROMPT

    print(f"\nGenerating level for: \"{prompt}\"")
    print("-" * 40)

    try:
        level_data = generate_level(prompt)
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    # Validate
    warnings = validate_level(level_data)
    if warnings:
        print("\n[WARNINGS]")
        for w in warnings:
            print(f"  ⚠  {w}")

    # Save to file
    saved_path = save_level(level_data, output_dir=args.output)
    print(f"\n[SAVED] Level written to: {saved_path}")

    # Pretty-print a summary to the terminal
    print("\n[LEVEL SUMMARY]")
    print(f"  Title   : {level_data.get('level_title', 'N/A')}")
    print(f"  Theme   : {level_data.get('theme', 'N/A')}")
    print(f"  Summary : {level_data.get('narrative_summary', 'N/A')}")
    print(f"  Rooms   : {len(level_data.get('rooms', []))}")
    print()

    for room in level_data.get("rooms", []):
        boss_tag = " 👹 [BOSS]" if room.get("is_boss_room") else ""
        print(f"  [{room['id']}] {room['name']} ({room['type']}){boss_tag}")
        print(f"       {room['description']}")
        if room.get("connections"):
            print(f"       → connects to: {', '.join(room['connections'])}")
        print()

    print("\nFull JSON:")
    print(json.dumps(level_data, indent=2))


if __name__ == "__main__":
    main()
