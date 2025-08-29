# Import helper functions for sending messages, polls, and keyboards
from telegram_helpers import send_message, send_quiz_poll, inline_keyboard

# Import content handlers (for tip, glossary, grades, tools, etc.)
from . import content


# Main message handler function
def handle_message(msg, data):
    # Extract chat ID from message
    chat_id = msg["chat"]["id"]

    # Get and normalize message text
    full_text = (msg.get("text") or "").strip()
    text = full_text.lower()

    # Load each content section from data.json
    CMD = data.get("commands", {})
    RECIPES = data.get("recipes", {})
    REVIEWS = data.get("reviews", {})
    QUIZ = data.get("quiz", {})

    # --- Standard commands ---

    # /start - welcome message
    def handle_start():
        send_message(chat_id, CMD.get("start", {}).get("response", "Welcome!"))

    # /about - description of the bot
    def handle_about():
        block = CMD.get("about", {})
        send_message(chat_id, block.get("text", "About"), parse_mode=block.get("parse_mode"))

    # /matcha101 - intro to matcha
    def handle_matcha101():
        block = CMD.get("matcha101", {})
        send_message(chat_id, block.get("text", "Matcha 101"), parse_mode=block.get("parse_mode"))

    # /channel - matcha diary / Telegram channel
    def handle_tele_channel():
        block = CMD.get("channel", {})
        send_message(chat_id, block.get("text", "Join the channel"), parse_mode=block.get("parse_mode"))

    # /recipes - show list of recipe buttons
    def handle_recipes():
        buttons = RECIPES.get("buttons", [])
        rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in buttons]
        send_message(chat_id, "🍽️ Choose a recipe:", reply_markup=inline_keyboard(rows))

    # /reviews - show brand/cafe review menu
    def handle_reviews():
        buttons = REVIEWS.get("buttons", [])
        rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in buttons]
        send_message(chat_id, "📝 Reviews menu:", reply_markup=inline_keyboard(rows))

    # /quiz - send quiz poll from data.json
    def handle_quiz():
        opts = QUIZ.get("options", [])
        correct_idx = next((i for i, o in enumerate(opts) if o.get("correct")), 0)
        send_quiz_poll(chat_id, QUIZ.get("question", "Quiz time!"), [o["text"] for o in opts], correct_idx)

    # /cafes - shortcut to cafe review list
    def handle_cafes():
        cafes = REVIEWS.get("cafes", [])
        rows = [[{"text": c["text"], "callback_data": c["callback_data"]}] for c in cafes]
        send_message(chat_id, "Choose a cafe:", reply_markup=inline_keyboard(rows))

    # --- Content commands (from content.py) ---

    # /tip - show a random tip
    def handle_tip():
        content.handle_tip(chat_id, data)

    # /glossary - paginated glossary terms
    def handle_glossary():
        content.handle_glossary(chat_id, data)

    # /grades - show matcha grade types
    def handle_grades():
        content.handle_grades(chat_id, data)

    # /tools - matcha tools with images
    def handle_tools():
        content.handle_tools(chat_id, data)

    # /timer - optional timer feature (currently disabled)
    # def handle_timer():
    #     content.handle_timer(chat_id)

    # --- Command Router ---
    # Maps commands to the corresponding handler functions
    command_map = {
        "/start": handle_start, "start": handle_start,
        "/about": handle_about, "about": handle_about,
        "/matcha101": handle_matcha101, "matcha101": handle_matcha101,
        "/channel": handle_tele_channel, "/tele_channel": handle_tele_channel, "channel": handle_tele_channel,
        "/recipes": handle_recipes, "recipes": handle_recipes,
        "/reviews": handle_reviews, "reviews": handle_reviews,
        "/quiz": handle_quiz, "quiz": handle_quiz,
        "/cafes": handle_cafes, "cafes": handle_cafes,

        "/tip": handle_tip, "tip": handle_tip,
        "/glossary": handle_glossary, "glossary": handle_glossary,
        "/grades": handle_grades, "grades": handle_grades,
        "/tools": handle_tools, "tools": handle_tools,
        # "/timer": handle_timer, "timer": handle_timer
    }

    # Look up and run the command handler, or show fallback message
    (command_map.get(text.split()[0]) or (lambda: send_message(chat_id, "Unknown command.")))()
