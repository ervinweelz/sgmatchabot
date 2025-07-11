from typing import Final
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None :
    """Handle /quiz command"""
    with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

    keyboard = [
        InlineKeyboardButton(option['text'], callback_data=option['data'])
        for option in data['quiz']['options']
    ]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text(data['quiz']['question'], reply_markup=reply_markup)

async def quiz_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

    query = update.callback_query
    for option in data['quiz']['options']:
        if query.data == option['data']:
            if option.get('correct'):
                response = "✅ *Wa so smart*"
            else:
                response = "❌ " + option.get('incorrect_response', 'Incorrect answer')
            await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN_V2)
            return