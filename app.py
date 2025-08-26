import os
import json
import logging
from flask import Flask, request, jsonify
import requests

from handlers import commands, callbacks

# === Config ===
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

DATA_PATH = os.environ.get("DATA_PATH", "data.json")
try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    raise RuntimeError(f"Failed to load data.json: {e}")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Telegram Helpers ===
def tg_post(method: str, payload=None, files=None):
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

# === Routes ===
@app.route("/", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)

    if "callback_query" in update:
        callbacks.handle_callback_query(update["callback_query"], DATA)

    elif "message" in update:
        commands.handle_message(update["message"], DATA)

    return "ok", 200

# === Entrypoint ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
