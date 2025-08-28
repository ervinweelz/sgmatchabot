from telegram_helpers import send_message, inline_keyboard
import time

# ---------- /tip ----------
def handle_tip(chat_id, data):
    tips = (data.get("content", {}) or {}).get("tips", [])
    if not tips:
        send_message(chat_id, "No tips available. Ask the admin to add some into data.json")
        return
    import random
    tip = random.choice(tips)
    send_message(chat_id, f"📝 *Tip*\n\n{tip}", parse_mode="Markdown")

# ---------- /glossary ----------
PAGE_SIZE = 6

def handle_glossary(chat_id, data, page: int = 0):
    gl = (data.get("content", {}) or {}).get("glossary", [])
    if not gl:
        send_message(chat_id, "No glossary terms yet.")
        return
    total_pages = (len(gl) + PAGE_SIZE - 1) // PAGE_SIZE
    page = max(0, min(total_pages - 1, page))

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = gl[start:end]

    lines = ["📗 *Matcha Glossary*"]
    for item in chunk:
        term = item.get("term", "")
        desc = item.get("definition", "")
        lines.append(f"\n*{term}*\n{desc}")

    nav = []
    if page > 0:
        nav.append({"text": "⬅️ Prev", "callback_data": f"glossary_page_{page-1}"})
    if page < total_pages - 1:
        nav.append({"text": "Next ➡️", "callback_data": f"glossary_page_{page+1}"})

    send_message(chat_id, "\n".join(lines), parse_mode="Markdown",
                 reply_markup=inline_keyboard([nav] if nav else []))

def handle_glossary_callback(cq, data):
    from telegram_helpers import edit_message_text, answer_callback
    cq_id = cq["id"]
    chat_id = cq["message"]["chat"]["id"]
    message_id = cq["message"]["message_id"]
    cb = cq.get("data", "")
    try:
        page = int(cb.split("_")[-1])
    except Exception:
        answer_callback(cq_id)
        return

    gl = (data.get("content", {}) or {}).get("glossary", [])
    total_pages = (len(gl) + PAGE_SIZE - 1) // PAGE_SIZE
    page = max(0, min(total_pages - 1, page))

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = gl[start:end]

    lines = ["📗 *Matcha Glossary*"]
    for item in chunk:
        term = item.get("term", "")
        desc = item.get("definition", "")
        lines.append(f"\n*{term}*\n{desc}")

    nav = []
    if page > 0:
        nav.append({"text": "⬅️ Prev", "callback_data": f"glossary_page_{page-1}"})
    if page < total_pages - 1:
        nav.append({"text": "Next ➡️", "callback_data": f"glossary_page_{page+1}"})

    try:
        edit_message_text(chat_id, message_id, "\n".join(lines),
                          reply_markup=inline_keyboard([nav] if nav else []),
                          parse_mode="Markdown")
    except Exception:
        send_message(chat_id, "\n".join(lines), parse_mode="Markdown",
                     reply_markup=inline_keyboard([nav] if nav else []))
    finally:
        answer_callback(cq_id)

# ---------- /grades ----------
def handle_grades(chat_id, data):
    grades = (data.get("content", {}) or {}).get("grades", [])
    if not grades:
        send_message(chat_id, "No grades info yet.")
        return
    lines = ["🏷️ *Matcha Grades*\n"]
    for g in grades:
        name = g.get("name", "")
        desc = g.get("description", "")
        lines.append(f"*{name}*\n{desc}\n")
    send_message(chat_id, "\n".join(lines), parse_mode="Markdown")

# ---------- /tools ----------
def handle_tools(chat_id, data):
    tools = (data.get("content", {}) or {}).get("tools", [])
    if not tools:
        send_message(chat_id, "No tools info yet.")
        return
    from telegram_helpers import send_photo
    for tool in tools:
        name = tool.get("name")
        desc = tool.get("description")
        image = tool.get("image")
        caption = f"🔧 *{name}*\n{desc}"
        if image:
            send_photo(chat_id, image, caption=caption, parse_mode="Markdown")
        else:
            send_message(chat_id, caption, parse_mode="Markdown")

# ---------- /timer ----------
# def handle_timer(chat_id):
#     send_message(chat_id, "⏱️ Timer started: 2 minutes")
#     time.sleep(60)
#     send_message(chat_id, "1 minute left...")
#     time.sleep(60)
#     send_message(chat_id, "✅ Done! Enjoy your matcha.")
