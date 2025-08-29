# Import helper functions for sending messages, images, and inline keyboards
from telegram_helpers import send_message, send_photo, inline_keyboard

# Main function to handle inline button callbacks
def handle_callback_query(cq, data):
    # Extract the chat ID and callback data from the query
    chat_id = cq["message"]["chat"]["id"]
    cb_data = cq.get("data", "")

    # Load recipes and reviews sections from the data
    RECIPES = data.get("recipes", {})
    REVIEWS = data.get("reviews", {})

    # Map recipe button callback_data to their recipe keys (e.g., 'usucha')
    RECIPE_CB_TO_KEY = {
        btn["callback_data"]: key
        for btn, key in zip(RECIPES.get("buttons", []), [k for k in ["usucha", "matcha_latte"] if k in RECIPES])
    }

    # Map review brand and cafe callback_data to their full data blocks
    REVIEW_BRANDS = {b["callback_data"]: b for b in REVIEWS.get("brands", [])}
    REVIEW_CAFES = {c["callback_data"]: c for c in REVIEWS.get("cafes", [])}

    # Helper: Format review text and ratings
    def build_review_text(item):
        lines = [item.get("text", "")]
        ratings = item.get("ratings", {})
        for key in ["usucha", "matcha_latte"]:
            if key in ratings:
                val = ratings[key]
                stars = "★" * int(val) + "☆" * (5 - int(val))  # Star bar
                lines.append(f"{key.replace('_', ' ').title()}: {stars} ({val}/5)")
        if item.get("notes"):
            lines.extend(["", item["notes"]])
        return "\n".join(lines).strip()

    # --- Recipes ---

    # If a recipe button was clicked, show the recipe
    if cb_data in RECIPE_CB_TO_KEY:
        recipe = RECIPES.get(RECIPE_CB_TO_KEY[cb_data], {})
        ingredients = recipe.get("ingredients", [])
        directions = recipe.get("directions", [])

        # Format and send the recipe text
        ingredients_text = "\n- ".join(ingredients)
        directions_text = "\n- ".join(directions)
        send_message(chat_id, f"Ingredients:\n- {ingredients_text}\n\nDirections:\n- {directions_text}")

    # --- Reviews Navigation ---

    # If 'brands' button clicked, show list of brands
    elif cb_data == "review_matcha_brands":
        brand_rows = [[{"text": b["text"], "callback_data": b["callback_data"]}] for b in REVIEWS.get("brands", [])]
        send_message(chat_id, "Choose a brand:", reply_markup=inline_keyboard(brand_rows))

    # If 'cafes' button clicked, show list of cafes
    elif cb_data == "review_cafes":
        cafe_rows = [[{"text": c["text"], "callback_data": c["callback_data"]}] for c in REVIEWS.get("cafes", [])]
        send_message(chat_id, "Choose a cafe:", reply_markup=inline_keyboard(cafe_rows))

    # Placeholder for service reviews (not yet implemented)
    elif cb_data == "review_service":
        send_message(chat_id, "Service review coming soon.")

    # --- Individual Review Selection ---

    # If a brand item was selected, send image + review
    elif cb_data in REVIEW_BRANDS:
        item = REVIEW_BRANDS[cb_data]
        send_photo(chat_id, item.get("image_url") or item.get("image_path"))
        send_message(chat_id, build_review_text(item))

    # If a cafe item was selected, send image + review
    elif cb_data in REVIEW_CAFES:
        item = REVIEW_CAFES[cb_data]
        send_photo(chat_id, item.get("image_url") or item.get("image_path"))
        send_message(chat_id, build_review_text(item))

    # Fallback: if callback data is unknown
    else:
        send_message(chat_id, "Unknown action.")
