import json
from typing import Callable
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        await update.message.reply_text(data['commands']['about']['text'])
    except FileNotFoundError:
        await update.message.reply_text(
            "Error: Could not find data.json file",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    except json.JSONDecodeError:
        await update.message.reply_text(
            "Error: Invalid JSON format in data.json",
            parse_mode=ParseMode.MARKDOWN_V2
        )