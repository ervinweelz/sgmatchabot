# === Standard Imports ===
import os
import json
import logging
import requests
from flask import Flask, request, jsonify

# === Local Imports ===
from handlers import commands, callbacks  # Import your custom command and callback handlers

# === Bot Configuration ===

# Get the bot token from environment variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

# Load data.json from path (defaults to "data.json" in root)
DATA_PATH = os.environ.get("DATA_PATH", "data.json")
try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    raise RuntimeError(f"Failed to load data.json: {e}")

# Telegram API base URL
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# === Flask App Setup ===
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Telegram Helper (optional direct API POST) ===
def tg_post(method: str, payload=None, files=None):
    """
    Utility function to send POST requests to Telegram API.
    Supports both JSON and multipart/form-data.
    """
    url = f"{TELEGRAM_API}/{method}"
    try:
        response = requests.post(
            url,
            json=payload if not files else None,
            data=payload if files else None,
            files=files,
            timeout=15
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Telegram API error: {e}")

# === Health Check Route ===
@app.route("/", methods=["GET"])
def health():
    """Simple GET route to confirm the app is running."""
    return jsonify(status="ok"), 200

# === Webhook Receiver ===
@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    """
    Telegram webhook handler.
    Called when Telegram sends a message or button callback to your bot.
    """
    update = request.get_json(force=True)

    if "callback_query" in update:
        # Inline button interaction
        callbacks.handle_callback_query(update["callback_query"], DATA)

    elif "message" in update:
        # Standard text message or command
        commands.handle_message(update["message"], DATA)

    return "ok", 200

# === App Entrypoint ===
if __name__ == "__main__":
    # Run the Flask app on all interfaces (required by most platforms like Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
