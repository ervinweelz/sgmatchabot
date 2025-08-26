import os
import requests
import logging

TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        payload = {"chat_id": chat_id, "photo": photo}
        if caption:
            payload["caption"] = caption[:1000]
        if parse_mode:
            payload["parse_mode"] = parse_mode
        tg_post("sendPhoto", payload)
    elif os.path.exists(photo):
        with open(photo, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": chat_id}
            if caption:
                data["caption"] = caption[:1000]
            if parse_mode:
                data["parse_mode"] = parse_mode
            tg_post("sendPhoto", data, files)

def inline_keyboard(rows):
    return {"inline_keyboard": rows}
