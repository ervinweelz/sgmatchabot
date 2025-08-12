# https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://yourapp.onrender.com/webhook/<YOUR_TOKEN>

from typing import Final
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from commands import about_command, matcha101_command, channel_command, recipes_command, quiz_command , reviews_command


TOKEN: Final = '7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00'
BOT_USERNAME: Final = 'sgmatchabot'

def load_json_data() -> dict:
    """Load data from JSON file."""
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

def handle_response(text: str) -> str:
    processed = text.lower()
    if 'hello' in processed:
        return 'Hey there!'
    if 'how are you' in processed:
        return 'I am good'
    return 'Please try again'

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('about', about_command.about))
    app.add_handler(CommandHandler('matcha101', matcha101_command.matcha101))
    app.add_handler(CommandHandler('recipes', recipes_command.recipes))
    app.add_handler(CommandHandler('quiz', quiz_command.quiz))
    app.add_handler(CommandHandler('channel', channel_command.channel))
    app.add_handler(CommandHandler('reviews', reviews_command.reviews))

    # Callback handlers
    # app.add_handler(CallbackQueryHandler(reviews_button_handler, pattern='^review_'))
    app.add_handler(CallbackQueryHandler(recipes_command.recipes_button_handler, pattern='^button_'))
    app.add_handler(CallbackQueryHandler(quiz_command.quiz_button_handler, pattern='^quiz_'))
# In the Application setup section, add:
    app.add_handler(CallbackQueryHandler(reviews_command.reviews_button_handler, pattern='^review_'))
    

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)
