"""
app.py

Flask server for the Level Visualizer.
Exposes one API endpoint: POST /generate
"""

from flask import Flask, request, jsonify, render_template
from src.generator import generate_level, validate_level
from src.history import save_to_history, load_history

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty"}), 400

    try:
        level_data = generate_level(prompt)
        entry = save_to_history(prompt, level_data)
        warnings = validate_level(level_data)
        return jsonify({"level": level_data, "warnings": warnings})
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500

@app.route("/history", methods=["GET"])
def history():
    return jsonify(load_history())


if __name__ == "__main__":
    app.run(debug=True)