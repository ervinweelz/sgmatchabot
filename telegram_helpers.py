import os
import requests
import logging

# Get your Telegram bot token from environment variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Base API URL for sending Telegram bot requests
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# Setup logging to track errors and actions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Helper: Send POST request to Telegram API
# -------------------------------
def tg_post(method: str, payload=None, files=None):
    url = f"{TELEGRAM_API}/{method}"
    try:
        response = requests.post(
            url,
            json=payload if not files else None,  # Use JSON when not sending files
            data=payload if files else None,      # Use form data when sending files
            files=files,
            timeout=15
        )
        response.raise_for_status()  # Raise error on HTTP failure
    except requests.RequestException as e:
        logger.error(f"Telegram API error: {e}")

# -------------------------------
# Send a basic text message
# -------------------------------
def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text[:4096]}  # Telegram limit = 4096 chars
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    tg_post("sendMessage", payload)

# -------------------------------
# Send a quiz-style poll
# -------------------------------
def send_quiz_poll(chat_id, question, options, correct_index=0, explanation=None):
    payload = {
        "chat_id": chat_id,
        "question": question,
        "options": options,  # List of strings
        "type": "quiz",      # Must be "quiz" for correct answer support
        "is_anonymous": True,
        "correct_option_id": int(correct_index),
    }
    if explanation:
        payload["explanation"] = explanation
    tg_post("sendPoll", payload)

# -------------------------------
# Send a photo (URL or local file)
# -------------------------------
def send_photo(chat_id, photo, caption=None, parse_mode=None):
    # Handle remote images via URL
    if isinstance(photo, str) and photo.startswith("http"):
        payload = {"chat_id": chat_id, "photo": photo}
        if caption:
            payload["caption"] = caption[:1000]  # Caption limit
        if parse_mode:
            payload["parse_mode"] = parse_mode
        tg_post("sendPhoto", payload)

    # Handle local file paths
    elif os.path.exists(photo):
        with open(photo, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption[:1000]
            if parse_mode:
                data["parse_mode"] = parse_mode
            tg_post("sendPhoto", data, files)

# -------------------------------
# Build an inline keyboard layout
# -------------------------------
def inline_keyboard(rows):
    return {"inline_keyboard": rows}  # rows = list of button row lists
