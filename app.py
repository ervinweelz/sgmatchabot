#https://api.telegram.org/bot7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00/setWebhook?url=https://sgmatchabot.onrender.com/webhook/7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00
import os
import json
from flask import Flask, request, jsonify
import requests

# === Config ===
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

DATA_PATH = os.environ.get("DATA_PATH", "data.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# === Telegram helpers ===
def tg_post_json(method: str, payload: dict):
    url = f"{TELEGRAM_API}/{method}"
    try:
        requests.post(url, json=payload, timeout=10)
    except requests.RequestException:
        pass

def tg_post_multipart(method: str, data: dict, files: dict):
    url = f"{TELEGRAM_API}/{method}"
    try:
        requests.post(url, data=data, files=files, timeout=20)
    except requests.RequestException:
        pass

def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    tg_post_json("sendMessage", payload)

def send_quiz_poll(chat_id, question, options, correct_index=0, explanation=None):
    payload = {
        "chat_id": chat_id,
        "question": question,
        "options": options,             # list of strings
        "type": "quiz",
        "is_anonymous": True,
        "correct_option_id": int(correct_index),
    }
    if explanation:
        payload["explanation"] = explanation
    tg_post_json("sendPoll", payload)

def send_photo(chat_id, photo, caption=None, parse_mode=None):
    """
    photo: URL string OR local file path (within repo)
    Sends the image first; caption is supported but we won't use it for reviews (we send text separately).
    """
    if isinstance(photo, str) and photo.lower().startswith(("http://", "https://")):
        payload = {"chat_id": chat_id, "photo": photo}
        if caption:
            payload["caption"] = caption[:1000]
        if parse_mode:
            payload["parse_mode"] = parse_mode
        tg_post_json("sendPhoto", payload)
    else:
        if not photo or not os.path.exists(photo):
            return
        data = {"chat_id": str(chat_id)}
        if caption:
            data["caption"] = caption[:1000]
        if parse_mode:
            data["parse_mode"] = parse_mode
        with open(photo, "rb") as f:
            files = {"photo": f}
            tg_post_multipart("sendPhoto", data, files)

def inline_keyboard(rows):
    return {"inline_keyboard": rows}

def star_bar(rating):
    """Return a 5-star bar. We show full stars and empties; decimals are shown numerically."""
    try:
        r = max(0.0, min(5.0, float(rating)))
    except (TypeError, ValueError):
        return "N/A"
    full = int(r)                   # full stars
    empty = 5 - full                # we don't render half-star glyphs for reliability
    return "★" * full + "☆" * empty


# === Data access ===
CMD = DATA.get("commands", {})
RECIPES = DATA.get("recipes", {})
REVIEWS = DATA.get("reviews", {})
QUIZ = DATA.get("quiz", {})

# Map recipe buttons -> recipe keys (based on known keys order)
_recipe_buttons = RECIPES.get("buttons", [])
_known_recipe_keys = [k for k in ["usucha", "matcha_latte"] if k in RECIPES]
RECIPE_CB_TO_KEY = {
    btn["callback_data"]: _known_recipe_keys[i]
    for i, btn in enumerate(_recipe_buttons)
    if i < len(_known_recipe_keys)
}

# Map review brand callbacks -> brand objects
REVIEW_BRANDS = {b["callback_data"]: b for b in REVIEWS.get("brands", [])}

# === Command handlers (use JSON content) ===
def handle_start(chat_id):
    text = CMD.get("start", {}).get("response", "Welcome!")
    send_message(chat_id, text)

def handle_about(chat_id):
    block = CMD.get("about", {})
    send_message(chat_id, block.get("text", "About"), parse_mode=block.get("parse_mode"))

def handle_matcha101(chat_id):
    block = CMD.get("matcha101", {})
    send_message(chat_id, block.get("text", "Matcha 101"), parse_mode=block.get("parse_mode"))

def handle_tele_channel(chat_id):
    block = CMD.get("channel", {})
    send_message(chat_id, block.get("text", "Join the channel"), parse_mode=block.get("parse_mode"))

def handle_recipes(chat_id):
    buttons = RECIPES.get("buttons", [])
    rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in buttons]
    send_message(chat_id, "Choose a recipe:", reply_markup=inline_keyboard(rows))

def handle_reviews(chat_id):
    buttons = REVIEWS.get("buttons", [])
    rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in buttons]
    send_message(chat_id, "Reviews menu:", reply_markup=inline_keyboard(rows))

def handle_quiz(chat_id):
    question = QUIZ.get("question", "Quiz time!")
    opts = QUIZ.get("options", [])
    option_texts = [o["text"] for o in opts]
    correct_idx = next((i for i, o in enumerate(opts) if o.get("correct")), 0)
    send_quiz_poll(chat_id, question, option_texts, correct_index=correct_idx)

# === Routes ===
@app.route("/", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}

    # --- Inline button presses ---
    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq.get("data", "")

        # Recipes: details
        if data in RECIPE_CB_TO_KEY:
            key = RECIPE_CB_TO_KEY[data]
            recipe = RECIPES.get(key, {})
            ingredients = recipe.get("ingredients", [])
            directions = recipe.get("directions", [])
            text = "Ingredients:\n- " + "\n- ".join(ingredients) + "\n\nDirections:\n- " + "\n- ".join(directions)
            send_message(chat_id, text)
            return "ok", 200

        # Reviews: show brand list
        if data == "review_matcha_brands":
            brand_rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in REVIEWS.get("brands", [])]
            send_message(chat_id, "Choose a brand:", reply_markup=inline_keyboard(brand_rows))
            return "ok", 200

        # Reviews: service review placeholder
        if data == "review_service":
            send_message(chat_id, "Service review coming soon.")
            return "ok", 200

        # Reviews: specific brand -> send image first, then text (with star ratings)
        if data in REVIEW_BRANDS:
            brand = REVIEW_BRANDS[data]
            img_url = brand.get("image_url")
            img_path = brand.get("image_path")

            # Build the text from ratings
            ratings = brand.get("ratings", {})
            u = ratings.get("usucha")
            l = ratings.get("matcha_latte")

            lines = [brand.get("text", "")]
            if u is not None:
                lines.append(f"Usucha: {star_bar(u)} ({u}/5)")
            if l is not None:
                lines.append(f"Matcha Latte: {star_bar(l)} ({l}/5)")
            if brand.get("notes"):
                lines.append("")
                lines.append(brand["notes"])

            review_text = "\n".join(lines).strip() or "No review yet."

            # 1) image, 2) text
            if img_url:
                send_photo(chat_id, img_url)
                send_message(chat_id, review_text)
            elif img_path:
                send_photo(chat_id, img_path)
                send_message(chat_id, review_text)
            else:
                send_message(chat_id, review_text)

            return "ok", 200


        # Fallback
        send_message(chat_id, "Unknown action.")
        return "ok", 200

    # --- Text messages / commands ---
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = (msg.get("text") or "").strip().lower()

        if text in ("/start", "start"):
            handle_start(chat_id)
        elif text in ("/about", "about"):
            handle_about(chat_id)
        elif text in ("/matcha101", "matcha101"):
            handle_matcha101(chat_id)
        elif text in ("/tele_channel", "tele_channel", "/channel", "channel"):
            handle_tele_channel(chat_id)
        elif text in ("/recipes", "recipes"):
            handle_recipes(chat_id)
        elif text in ("/reviews", "reviews"):
            handle_reviews(chat_id)
        elif text in ("/quiz", "quiz"):
            handle_quiz(chat_id)
        else:
            send_message(chat_id, "Unknown command. Try: /about /matcha101 /tele_channel /recipes /reviews /quiz")

    return "ok", 200

# === Entrypoint ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
