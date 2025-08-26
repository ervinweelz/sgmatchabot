import os
import json
import logging
from flask import Flask, request, jsonify
import requests

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
        response = requests.post(url, json=payload if not files else None, data=payload if files else None, files=files, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Telegram API error: {e}")


def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text[:4096]}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    tg_post("sendMessage", payload)


def send_quiz_poll(chat_id, question, options, correct_index=0, explanation=None):
    payload = {
        "chat_id": chat_id,
        "question": question,
        "options": options,
        "type": "quiz",
        "is_anonymous": True,
        "correct_option_id": int(correct_index),
    }
    if explanation:
        payload["explanation"] = explanation
    tg_post("sendPoll", payload)


def send_photo(chat_id, photo, caption=None, parse_mode=None):
    if isinstance(photo, str) and photo.startswith("http"):
        payload = {"chat_id": chat_id, "photo": photo, "caption": caption[:1000] if caption else None}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        tg_post("sendPhoto", payload)
    elif os.path.exists(photo):
        with open(photo, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id, "caption": caption[:1000] if caption else None}
            if parse_mode:
                data["parse_mode"] = parse_mode
            tg_post("sendPhoto", data, files)


def inline_keyboard(rows):
    return {"inline_keyboard": rows}


def star_bar(rating):
    try:
        r = max(0.0, min(5.0, float(rating)))
    except (TypeError, ValueError):
        return "N/A"
    return "★" * int(r) + "☆" * (5 - int(r))

# === Data ===
CMD = DATA.get("commands", {})
RECIPES = DATA.get("recipes", {})
REVIEWS = DATA.get("reviews", {})
QUIZ = DATA.get("quiz", {})

RECIPE_CB_TO_KEY = {btn["callback_data"]: key for btn, key in zip(RECIPES.get("buttons", []), [k for k in ["usucha", "matcha_latte"] if k in RECIPES])}
REVIEW_BRANDS = {b["callback_data"]: b for b in REVIEWS.get("brands", [])}
REVIEW_CAFES = {c["callback_data"]: c for c in REVIEWS.get("cafes", [])}

# === Command Handlers ===
def handle_start(chat_id): send_message(chat_id, CMD.get("start", {}).get("response", "Welcome!"))
def handle_about(chat_id): send_message(chat_id, CMD.get("about", {}).get("text", "About"), parse_mode=CMD.get("about", {}).get("parse_mode"))
def handle_matcha101(chat_id): send_message(chat_id, CMD.get("matcha101", {}).get("text", "Matcha 101"), parse_mode=CMD.get("matcha101", {}).get("parse_mode"))
def handle_tele_channel(chat_id): send_message(chat_id, CMD.get("channel", {}).get("text", "Join the channel"), parse_mode=CMD.get("channel", {}).get("parse_mode"))

def handle_recipes(chat_id):
    buttons = RECIPES.get("buttons", [])
    rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in buttons]
    send_message(chat_id, "Choose a recipe:", reply_markup=inline_keyboard(rows))

def handle_reviews(chat_id):
    buttons = REVIEWS.get("buttons", [])
    rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in buttons]
    send_message(chat_id, "Reviews menu:", reply_markup=inline_keyboard(rows))

def handle_quiz(chat_id):
    opts = QUIZ.get("options", [])
    correct_idx = next((i for i, o in enumerate(opts) if o.get("correct")), 0)
    send_quiz_poll(chat_id, QUIZ.get("question", "Quiz time!"), [o["text"] for o in opts], correct_idx)

def build_review_text(item):
    lines = [item.get("text", "")]
    ratings = item.get("ratings", {})
    for key in ["usucha", "matcha_latte"]:
        if key in ratings:
            lines.append(f"{key.replace('_', ' ').title()}: {star_bar(ratings[key])} ({ratings[key]}/5)")
    if item.get("notes"):
        lines.extend(["", item["notes"]])
    return "\n".join(lines).strip()

# === Routes ===
@app.route("/", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)

    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq.get("data", "")

        if data in RECIPE_CB_TO_KEY:
            recipe = RECIPES.get(RECIPE_CB_TO_KEY[data], {})
            ingredients = recipe.get("ingredients", [])
            directions = recipe.get("directions", [])
            send_message(chat_id, f"Ingredients:\n- {'\n- '.join(ingredients)}\n\nDirections:\n- {'\n- '.join(directions)}")
        elif data == "review_matcha_brands":
            brand_rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in REVIEWS.get("brands", [])]
            send_message(chat_id, "Choose a brand:", reply_markup=inline_keyboard(brand_rows))
        elif data == "review_cafes":
            cafe_rows = [[{"text": c["text"], "callback_data": c["callback_data"]}] for c in REVIEWS.get("cafes", [])]
            send_message(chat_id, "Choose a cafe:", reply_markup=inline_keyboard(cafe_rows))
        elif data == "review_service":
            send_message(chat_id, "Service review coming soon.")
        elif data in REVIEW_BRANDS:
            item = REVIEW_BRANDS[data]
            send_photo(chat_id, item.get("image_url") or item.get("image_path"))
            send_message(chat_id, build_review_text(item))
        elif data in REVIEW_CAFES:
            item = REVIEW_CAFES[data]
            send_photo(chat_id, item.get("image_url") or item.get("image_path"))
            send_message(chat_id, build_review_text(item))
        else:
            send_message(chat_id, "Unknown action.")

    elif "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = (msg.get("text") or "").strip().lower()

        command_map = {
            "/start": handle_start,
            "/about": handle_about,
            "/matcha101": handle_matcha101,
            "/channel": handle_tele_channel,
            "/tele_channel": handle_tele_channel,
            "/recipes": handle_recipes,
            "/reviews": handle_reviews,
            "/quiz": handle_quiz,
            "/cafes": lambda cid: send_message(cid, "Choose a cafe:", reply_markup=inline_keyboard([[{"text": c["text"], "callback_data": c["callback_data"]}] for c in REVIEWS.get("cafes", [])]))
        }
        (command_map.get(text) or (lambda cid: send_message(cid, "Unknown command.")))(chat_id)

    return "ok", 200

# === Entrypoint ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
