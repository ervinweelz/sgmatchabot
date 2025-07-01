from typing import Final
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from commands import about_command, matcha101_command


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

# async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     data = load_json_data()
#     cmd_data = data['commands']['about']
#     await update.message.reply_text(
#         cmd_data['text'],
#         parse_mode=ParseMode.MARKDOWN_V2 if cmd_data.get('parse_mode') == 'MarkdownV2' else None
#     )

# async def matcha101_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     data = load_json_data()
#     cmd_data = data['commands']['matcha101']
#     await update.message.reply_text(
#         cmd_data['text'],
#         parse_mode=ParseMode.MARKDOWN_V2 if cmd_data.get('parse_mode') == 'MarkdownV2' else None
#     )

async def channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_json_data()
    cmd_data = data['commands']['channel']
    await update.message.reply_text(cmd_data['text'], 
                                  parse_mode=None if cmd_data.get('parse_mode') is None else ParseMode.HTML)

async def recipes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_json_data()
    keyboard = [InlineKeyboardButton(button['text'], callback_data=button['callback_data'])
               for button in data['recipes']['buttons']]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text('Select your recipe to view', reply_markup=reply_markup)

async def recipes_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_json_data()
    query = update.callback_query
    
    if query.data.split("_")[1] == '1':
        recipe = data['recipes']['usucha']
        recipe_text = f"""
🍵 *Usucha Recipe*
🌿 *Ingredients*
{'\n• '.join(recipe['ingredients'])}
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

async def reviews_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_json_data()
    keyboard = [InlineKeyboardButton(button['text'], callback_data=button['callback_data'])
               for button in data['reviews']['buttons']]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text('Select your review category', reply_markup=reply_markup)

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_json_data()
    keyboard = [InlineKeyboardButton(option['text'], callback_data=option['data'])
                for option in data['quiz']['options']]
    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text(data['quiz']['question'], reply_markup=reply_markup)

async def quiz_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_json_data()
    query = update.callback_query
    
    for option in data['quiz']['options']:
        if query.data == option['data']:
            if option.get('correct'):
                response = "✅ *Wa so smart*"
            else:
                response = "❌ " + option.get('incorrect_response', 'Incorrect answer')
            
            await query.edit_message_text(response, parse_mode=ParseMode.MARKDOWN_V2)
            return

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
    # app.add_handler(CommandHandler('about', about_command))
    app.add_handler(CommandHandler('recipes', recipes_command))
    app.add_handler(CommandHandler('quiz', quiz_command))
    # app.add_handler(CommandHandler('matcha101', matcha101_command))
    app.add_handler(CommandHandler('channel', channel_command))
    app.add_handler(CommandHandler('reviews', reviews_command))

    # Callback handlers
    # app.add_handler(CallbackQueryHandler(reviews_button_handler, pattern='^review_'))
    app.add_handler(CallbackQueryHandler(recipes_button_handler, pattern='^button_'))
    app.add_handler(CallbackQueryHandler(quiz_button_handler, pattern='^quiz_'))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)