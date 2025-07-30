from typing import Final
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

async def reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reviews command"""
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    keyboard = [
        InlineKeyboardButton(button['text'], callback_data=button['callback_data'])
        for button in data['reviews']['buttons']
    ]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text('Select your review category', reply_markup=reply_markup)

async def reviews_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle initial review buttons"""
    query = update.callback_query
    await query.answer()
    
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if query.data == 'review_matcha_brands':
        keyboard = [
            InlineKeyboardButton(brand['text'], callback_data=brand['callback_data'])
            for brand in data['reviews']['brands']
        ]
        reply_markup2 = InlineKeyboardMarkup([keyboard])
        print(reply_markup2)
        await update.message.reply_text('Select your matcha brand', reply_markup=reply_markup2)

# async def brand_review_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handle matcha brand selection"""
#     query = update.callback_query
#     await query.answer()
    
#     try:
#         # Load JSON file
#         with open('data.json', 'r', encoding='utf-8') as f:
#             data = json.load(f)
        
#         # Find selected brand
#         selected_brand = next(
#             (brand for brand in data['reviews']['brands'] 
#              if brand['callback_data'] == query.data),
#             None
#         )
        
#         if selected_brand is None:
#             await query.edit_message_text("Brand not found.")
#             return
            
#         if 'review' not in selected_brand:
#             await query.edit_message_text("No review available for this brand.")
#             return
        
#         # Create navigation buttons
#         keyboard = [
#             InlineKeyboardButton("Back to Brands", callback_data="review_matcha_brands"),
#             InlineKeyboardButton("Service Review", callback_data="review_service")
#         ]
#         reply_markup = InlineKeyboardMarkup([keyboard])
        
#         # Display review with brand name
#         review_text = f"<b>{selected_brand['text']}</b>\n\n{selected_brand['review']}"
#         await query.edit_message_text(review_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        
#     except Exception as e:
#         await query.edit_message_text("An unexpected error occurred.")
#         print(f"Error handling brand review: {str(e)}")