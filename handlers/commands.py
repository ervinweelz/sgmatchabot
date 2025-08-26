from telegram_helpers import send_message, send_quiz_poll, inline_keyboard

def handle_message(msg, data):
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip().lower()

    CMD = data.get("commands", {})
    RECIPES = data.get("recipes", {})
    REVIEWS = data.get("reviews", {})
    QUIZ = data.get("quiz", {})

    def handle_start():
        send_message(chat_id, CMD.get("start", {}).get("response", "Welcome!"))

    def handle_about():
        block = CMD.get("about", {})
        send_message(chat_id, block.get("text", "About"), parse_mode=block.get("parse_mode"))

    def handle_matcha101():
        block = CMD.get("matcha101", {})
        send_message(chat_id, block.get("text", "Matcha 101"), parse_mode=block.get("parse_mode"))

    def handle_tele_channel():
        block = CMD.get("channel", {})
        send_message(chat_id, block.get("text", "Join the channel"), parse_mode=block.get("parse_mode"))

    def handle_recipes():
        buttons = RECIPES.get("buttons", [])
        rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in buttons]
        send_message(chat_id, "Choose a recipe:", reply_markup=inline_keyboard(rows))

    def handle_reviews():
        buttons = REVIEWS.get("buttons", [])
        rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in buttons]
        send_message(chat_id, "Reviews menu:", reply_markup=inline_keyboard(rows))

    def handle_quiz():
        opts = QUIZ.get("options", [])
        correct_idx = next((i for i, o in enumerate(opts) if o.get("correct")), 0)
        send_quiz_poll(chat_id, QUIZ.get("question", "Quiz time!"), [o["text"] for o in opts], correct_idx)

    def handle_cafes():
        cafes = REVIEWS.get("cafes", [])
        rows = [[{"text": c["text"], "callback_data": c["callback_data"]}] for c in cafes]
        send_message(chat_id, "Choose a cafe:", reply_markup=inline_keyboard(rows))

    command_map = {
        "/start": handle_start,
        "start": handle_start,
        "/about": handle_about,
        "about": handle_about,
        "/matcha101": handle_matcha101,
        "matcha101": handle_matcha101,
        "/channel": handle_tele_channel,
        "/tele_channel": handle_tele_channel,
        "channel": handle_tele_channel,
        "/recipes": handle_recipes,
        "recipes": handle_recipes,
        "/reviews": handle_reviews,
        "reviews": handle_reviews,
        "/quiz": handle_quiz,
        "quiz": handle_quiz,
        "/cafes": handle_cafes,
        "cafes": handle_cafes,
    }

    (command_map.get(text) or (lambda: send_message(chat_id, "Unknown command.")))()
