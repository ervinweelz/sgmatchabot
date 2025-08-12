import os
from flask import Flask, request, jsonify
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN environment variable")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# === Helper to send Telegram messages ===
def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def send_quiz_poll(chat_id, question, options, correct_index=0, explanation=None):
    url = f"{TELEGRAM_API}/sendPoll"
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
    requests.post(url, json=payload)

# === Command Handlers ===
def handle_start(chat_id):
    send_message(chat_id, "👋 Hello! I’m SG Matcha Bot — your pocket guide to matcha in Singapore.\nType /help to see what I can do.")

def handle_help(chat_id):
    send_message(chat_id,
        "Here are my commands:\n"
        "/about – What this bot is about\n"
        "/tele_channel – Our Telegram channel\n"
        "/matcha101 – Matcha basics and tips\n"
        "/quiz – Quick matcha quiz\n"
        "/recipes – Simple matcha recipes\n"
        "/reviews – Community reviews"
    )

def handle_about(chat_id):
    send_message(chat_id, "🍵 SG Matcha Bot\nDiscover matcha spots, learn the basics, try recipes, and read bite-sized reviews.")

def handle_tele_channel(chat_id):
    send_message(chat_id, "Join our Telegram channel: https://t.me/your_matcha_channel")

def handle_matcha101(chat_id):
    send_message(chat_id,
        "🌱 Matcha 101\n"
        "• Ceremonial grade (sipping) / Culinary grade (lattes/bakes)\n"
        "• Water ~70–80°C\n"
        "• Ratio ~2g matcha : 60–70 ml water\n"
        "• Whisk zig-zag for froth"
    )

def handle_quiz(chat_id):
    question = "Which water temperature is best for preparing matcha?"
    options = ["Boiling 100°C", "85–95°C", "70–80°C", "Room temp"]
    send_quiz_poll(chat_id, question, options, correct_index=2, explanation="Hot—but not boiling—keeps it smooth.")

def handle_recipes(chat_id):
    send_message(chat_id,
        "📗 Simple Recipes\n"
        "• Iced Matcha Latte: 2g matcha, 60 ml water (75°C), whisk → ice → 180 ml milk\n"
        "• Matcha Lemonade: 2g matcha, 80 ml water, whisk → 200 ml lemonade over ice\n"
        "• Matcha Banana Smoothie: 2g matcha, 1 banana, 200 ml milk, blend"
    )

def handle_reviews(chat_id):
    send_message(chat_id,
        "⭐ Reviews\n"
        "• Cafe A: Smooth, grassy, low bitterness\n"
        "• Cafe B: Robust, slightly toasty\n"
        "• Cafe C: Creamy latte, light sweetness"
    )

COMMANDS = {
    "/start": handle_start,
    "/help": handle_help,
    "/about": handle_about,
    "/tele_channel": handle_tele_channel,
    "/matcha101": handle_matcha101,
    "/quiz": handle_quiz,
    "/recipes": handle_recipes,
    "/reviews": handle_reviews,
}

# === Routes ===
@app.route("/", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = (data["message"].get("text") or "").strip().lower()
        if not text.startswith("/"):
            text = f"/{text}"
        handler = COMMANDS.get(text)
        if handler:
            handler(chat_id)
        else:
            send_message(chat_id, "Unknown command. Type /help for a list of commands.")
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
