# Narrative Level Generator

A Python tool that takes a natural language story prompt and outputs a structured JSON room layout using Claude AI.

**Part of a larger Unity plugin** for narrative-aware level generation for indie game developers.

---

## Project Structure

```
narrative-level-gen/
├── main.py               # Entry point — run this
├── requirements.txt
├── .env.example          # Copy to .env and add your API key
├── src/
│   ├── generator.py      # Core: API calls, parsing, validation
│   └── prompt_builder.py # Prompt templates (edit these to tune output)
├── output/               # Generated JSON files saved here
└── tests/
    └── test_generator.py
```

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your API key
cp .env.example .env
# Open .env and replace with your real Anthropic API key

# 4. Run it!
python main.py

# Or with a custom prompt:
python main.py --prompt "haunted ship, 4 rooms, sea monster boss"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Week 2 Preview

Week 2 will add `src/visualizer.py` to render the JSON room graph as a 2D map using matplotlib.
