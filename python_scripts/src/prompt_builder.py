"""
prompt_builder.py

Builds the system and user prompts sent to the LLM.
Keeping prompt logic separate from API logic makes it
easy to iterate on prompts without touching other code.
"""

SYSTEM_PROMPT = """You are a game level designer AI. Your job is to take a natural language story prompt and generate a structured JSON room layout for a 2D game level.

Rules:
- The "rooms" array is ordered — index 0 is always the entrance/start room
- Exactly one room must have type "boss"
- The first room must have type "entrance"
- Room types must be ONLY one of: "entrance", "standard", "corridor", "treasure", "boss"
- Room moods must be ONLY one of: "tense", "dark", "dramatic", "calm", "eerie"
- "enemies" must be a single string, one of: "none", "patrol", "guard", "swarm", "boss"
- "exits" is an integer (how many doors/exits the room has)
- "connections" is a list of integer index PAIRS — e.g. [[0,1],[1,2]] means room 0 connects to room 1, room 1 connects to room 2
- Every room must be reachable (no isolated rooms)

Return ONLY valid JSON. No explanation, no markdown fences, no extra text.

JSON schema:
{
  "level_title": "string",
  "theme": "string",
  "narrative_summary": "string",
  "rooms": [
    {
      "type": "entrance | standard | corridor | treasure | boss",
      "mood": "tense | dark | dramatic | calm | eerie",
      "enemies": "none | patrol | guard | swarm | boss",
      "exits": 2
    }
  ],
  "connections": [[0, 1], [1, 2]]
}
"""


def build_user_prompt(story_prompt: str) -> str:
    """Wrap the raw user story prompt in a clear instruction."""
    return f"""Generate a level layout for this story prompt:

\"{story_prompt}\"

Remember: return ONLY the JSON object, nothing else."""