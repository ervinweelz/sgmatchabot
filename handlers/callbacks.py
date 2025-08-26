from telegram_helpers import send_message, send_photo, inline_keyboard

def handle_callback_query(cq, data):
    chat_id = cq["message"]["chat"]["id"]
    cb_data = cq.get("data", "")

    RECIPES = data.get("recipes", {})
    REVIEWS = data.get("reviews", {})

    RECIPE_CB_TO_KEY = {
        btn["callback_data"]: key
        for btn, key in zip(RECIPES.get("buttons", []), [k for k in ["usucha", "matcha_latte"] if k in RECIPES])
    }
    REVIEW_BRANDS = {b["callback_data"]: b for b in REVIEWS.get("brands", [])}
    REVIEW_CAFES = {c["callback_data"]: c for c in REVIEWS.get("cafes", [])}

    def build_review_text(item):
        lines = [item.get("text", "")]
        ratings = item.get("ratings", {})
        for key in ["usucha", "matcha_latte"]:
            if key in ratings:
                val = ratings[key]
                stars = "★" * int(val) + "☆" * (5 - int(val))
                lines.append(f"{key.replace('_', ' ').title()}: {stars} ({val}/5)")
        if item.get("notes"):
            lines.extend(["", item["notes"]])
        return "\n".join(lines).strip()

    if cb_data in RECIPE_CB_TO_KEY:
        recipe = RECIPES.get(RECIPE_CB_TO_KEY[cb_data], {})
        ingredients = recipe.get("ingredients", [])
        directions = recipe.get("directions", [])
        send_message(chat_id, f"Ingredients:\n- {'\n- '.join(ingredients)}\n\nDirections:\n- {'\n- '.join(directions)}")

    elif cb_data == "review_matcha_brands":
        brand_rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in REVIEWS.get("brands", [])]
        send_message(chat_id, "Choose a brand:", reply_markup=inline_keyboard(brand_rows))

    elif cb_data == "review_cafes":
        cafe_rows = [[{"text": c["text"], "callback_data": c["callback_data"]}] for c in REVIEWS.get("cafes", [])]
        send_message(chat_id, "Choose a cafe:", reply_markup=inline_keyboard(cafe_rows))

    elif cb_data == "review_service":
        send_message(chat_id, "Service review coming soon.")

    elif cb_data in REVIEW_BRANDS:
        item = REVIEW_BRANDS[cb_data]
        send_photo(chat_id, item.get("image_url") or item.get("image_path"))
        send_message(chat_id, build_review_text(item))

    elif cb_data in REVIEW_CAFES:
        item = REVIEW_CAFES[cb_data]
        send_photo(chat_id, item.get("image_url") or item.get("image_path"))
        send_message(chat_id, build_review_text(item))

    else:
        send_message(chat_id, "Unknown action.")
