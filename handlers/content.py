from telegram_helpers import send_message, inline_keyboard, edit_message_text, answer_callback, send_photo
import time
import random

# ---------- /tip ----------
# Sends a random tip from the data.json file
def handle_tip(chat_id, data):
    tips = (data.get("content", {}) or {}).get("tips", [])
    if not tips:
        send_message(chat_id, "No tips available. Ask the admin to add some into data.json")
        return
    tip = random.choice(tips)
    send_message(chat_id, f"📝 *Tip*\n\n{tip}", parse_mode="Markdown")

# ---------- /glossary ----------
PAGE_SIZE = 6  # Number of glossary terms per page

# Handles the /glossary command (shows first page)
def handle_glossary(chat_id, data, page: int = 0):
    gl = (data.get("content", {}) or {}).get("glossary", [])
    if not gl:
        send_message(chat_id, "No glossary terms yet.")
        return

    total_pages = (len(gl) + PAGE_SIZE - 1) // PAGE_SIZE
    page = max(0, min(total_pages - 1, page))  # Ensure valid page range

    start = page * PAGE_SIZE
    chunk = gl[start:start + PAGE_SIZE]

    # Build the glossary message
    lines = ["📗 *Matcha Glossary*"]
    for item in chunk:
        lines.append(f"\n*{item.get('term', '')}*\n{item.get('definition', '')}")

    # Navigation buttons
    nav = []
    if page > 0:
        nav.append({"text": "⬅️ Prev", "callback_data": f"glossary_page_{page-1}"})
    if page < total_pages - 1:
        nav.append({"text": "Next ➡️", "callback_data": f"glossary_page_{page+1}"})

    send_message(chat_id, "\n".join(lines), parse_mode="Markdown",
                 reply_markup=inline_keyboard([nav] if nav else []))

# Callback handler for inline glossary navigation
def handle_glossary_callback(cq, data):
    cq_id = cq["id"]
    chat_id = cq["message"]["chat"]["id"]
    message_id = cq["message"]["message_id"]
    cb = cq.get("data", "")

    try:
        page = int(cb.split("_")[-1])  # Extract page number from callback
    except Exception:
        answer_callback(cq_id)
        return

    gl = (data.get("content", {}) or {}).get("glossary", [])
    total_pages = (len(gl) + PAGE_SIZE - 1) // PAGE_SIZE
    page = max(0, min(total_pages - 1, page))

    start = page * PAGE_SIZE
    chunk = gl[start:start + PAGE_SIZE]

    # Build glossary page message
    lines = ["📗 *Matcha Glossary*"]
    for item in chunk:
        lines.append(f"\n*{item.get('term', '')}*\n{item.get('definition', '')}")

    nav = []
    if page > 0:
        nav.append({"text": "⬅️ Prev", "callback_data": f"glossary_page_{page-1}"})
    if page < total_pages - 1:
        nav.append({"text": "Next ➡️", "callback_data": f"glossary_page_{page+1}"})

    # Try editing the previous message, else send a new one
    try:
        edit_message_text(chat_id, message_id, "\n".join(lines),
                          reply_markup=inline_keyboard([nav] if nav else []),
                          parse_mode="Markdown")
    except Exception:
        send_message(chat_id, "\n".join(lines), parse_mode="Markdown",
                     reply_markup=inline_keyboard([nav] if nav else []))
    finally:
        answer_callback(cq_id)  # Notify Telegram the callback was handled

# ---------- /grades ----------
# Displays matcha grade levels with descriptions
def handle_grades(chat_id, data):
    grades = (data.get("content", {}) or {}).get("grades", [])
    if not grades:
        send_message(chat_id, "No grades info yet.")
        return
    lines = ["🏷️ *Matcha Grades*\n"]
    for g in grades:
        lines.append(f"*{g.get('name', '')}*\n{g.get('description', '')}\n")
    send_message(chat_id, "\n".join(lines), parse_mode="Markdown")

# ---------- /tools ----------
# Sends info (and images) about matcha preparation tools
# def handle_tools(chat_id, data):
#     tools = (data.get("content", {}) or {}).get("tools", [])
#     if not tools:
#         send_message(chat_id, "No tools info yet.")
#         return

#     for tool in tools:
#         name = tool.get("name")
#         desc = tool.get("description")
#         image = tool.get("image")
#         caption = f"🔧 *{name}*\n{desc}"
#         if image:
#             send_photo(chat_id, image, caption=caption, parse_mode="Markdown")
#         else:
#             send_message(chat_id, caption, parse_mode="Markdown")

# ---------- /timer ----------
# Starts a 2-minute timer with progress messages
# def handle_timer(chat_id):
#     send_message(chat_id, "⏱️ Timer started: 2 minutes")
#     time.sleep(60)
#     send_message(chat_id, "1 minute left...")
#     time.sleep(60)
#     send_message(chat_id, "✅ Done! Enjoy your matcha.")
