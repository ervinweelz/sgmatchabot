from typing import Final
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

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