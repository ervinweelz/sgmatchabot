#https://api.telegram.org/bot<7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00>/setWebhook?url=https://yourapp.onrender.com/webhook/<7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00>

import os
import json
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
)
from commands import (
    about_command, matcha101_command, channel_command,
    recipes_command, quiz_command, reviews_command
)

TOKEN = ("7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00")
BOT_USERNAME = 'sgmatchabot'

def load_json_data() -> dict:
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: Could not find data.json file")
        raise
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in data.json")
        raise

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_json_data()
    await update.message.reply_text(data['commands']['start']['response'])

def handle_response(text: str) -> str:
    processed = text.lower()
    if 'hello' in processed:
        return 'Hey there!'
    if 'how are you' in processed:
        return 'I am good'
    return 'Please try again'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')
    
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response = handle_response(new_text)
        else:
            return
    else:
        response = handle_response(text)
    
    print('Bot: ', response)
    await update.message.reply_text(response)

async def error(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# --- Flask App Setup ---
app = Flask(__name__)

# --- Telegram Application Setup ---
telegram_app = Application.builder().token(TOKEN).build()

# Register handlers
telegram_app.add_handler(CommandHandler('start', start_command))
telegram_app.add_handler(CommandHandler('about', about_command.about))
telegram_app.add_handler(CommandHandler('matcha101', matcha101_command.matcha101))
telegram_app.add_handler(CommandHandler('recipes', recipes_command.recipes))
telegram_app.add_handler(CommandHandler('quiz', quiz_command.quiz))
telegram_app.add_handler(CommandHandler('channel', channel_command.channel))
telegram_app.add_handler(CommandHandler('reviews', reviews_command.reviews))
telegram_app.add_handler(CallbackQueryHandler(recipes_command.recipes_button_handler, pattern='^button_'))
telegram_app.add_handler(CallbackQueryHandler(quiz_command.quiz_button_handler, pattern='^quiz_'))
telegram_app.add_handler(CallbackQueryHandler(reviews_command.reviews_button_handler, pattern='^review_'))
telegram_app.add_handler(MessageHandler(filters.TEXT, handle_message))
telegram_app.add_error_handler(error)

# --- Webhook Endpoint ---
@flask_app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.create_task(telegram_app.process_update(update))
    return 'ok', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host='0.0.0.0', port=port)
