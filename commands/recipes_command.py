from typing import Final
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /recipes command"""
    with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

    keyboard = [
        InlineKeyboardButton(button['text'], callback_data=button['callback_data'])
        for button in data['recipes']['buttons']
    ]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text('Select your recipe to view', reply_markup=reply_markup)

async def recipes_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

    """Handle recipe selection buttons"""
    query = update.callback_query
    
    if query.data.split("_")[1] == '1':
        recipe = data['recipes']['usucha']
        recipe_text = f"""
🍵 *Usucha Recipe*\n
🌿 *Ingredients*
• {'\n• '.join(recipe['ingredients'])}\n
📝 *Directions*
{'\n'.join(f'• {step}' for step in recipe['directions'])}
"""
    elif query.data.split("_")[1] == '2':
        recipe = data['recipes']['matcha_latte']
        recipe_text = f"""
🍵🥛 *Matcha Latte Recipe*
🌿 *Ingredients*
{'\n• '.join(recipe['ingredients'])}
📝 *Directions*
{'\n'.join(f'• {step}' for step in recipe['directions'])}
"""
    
    await query.edit_message_text(recipe_text, parse_mode=ParseMode.MARKDOWN_V2)