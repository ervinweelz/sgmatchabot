from typing import Final 
from telegram import Update , InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes , CallbackQueryHandler

TOKEN : Final = '7971717836:AAEg-0paQG3qBzbYOfvnpkY4DQHRk6YAj00'
BOT_USERNAME : Final = 'sgmatchabot'


# Commands 
async def start_command(update: Update, context:ContextTypes.DEFAULT_TYPE) : 
    await update.message.reply_text('Welcome my fellow Matcha lovers 🍵')


async def about_command(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None : 
    about_text = """

*SGMATCHA* 🤖

Hi there fellow matcha lovers 🍵 , this is a bot i created to document down my journey in SG 🇸🇬 so far into the world of matcha 

Feel free to use this bot to get the latest recipes, very biased reviews and random content that I'll be adding \here 😎
 
*disclaimer* : I am in no way an expert in matcha, this serves as my matcha journal for everyone to read 
"""
    await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN_V2)

async def recipes_command(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None : 
    await recipes_buttons(update, context)


async def reviews_command(update: Update, context:ContextTypes.DEFAULT_TYPE) : 
    await update.message.reply_text('this is custom')



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) : 
    message_type: str = update.message.chat.type 
    text : str = update.message.chat.type 

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group' : 
        if BOT_USERNAME in text : 
            new_text : str = text.replace(BOT_USERNAME, '').strip()
            response : str = handle_response(new_text)
        else : 
            return 
    
    else : 
        response: str = handle_response(text)
    
    print('Bot: ', response)

    await update.message.reply_text(response)


# Responses

def handle_response(text:str) -> str : 
    processed: str = text.lower()

    if 'hello' in processed : 
        return 'Hey there!'
    
    if 'how are you' in processed : 
        return 'I am good'
    
    return 'Please try again'


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) : 
    print(f'Update {update} caused error {context.error}')


async def recipes_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🍵 Usucha", callback_data='button_1')],
        [InlineKeyboardButton("🍵🥛 Matcha Latte", callback_data='button_2')],
    
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select your recipe to view', reply_markup=reply_markup)

async def button_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data.split("_")[1] == '1':
        recipe_text = """
🍵 *Usucha Recipe*

🌿 *Ingredients*
• 4g of Matcha Powder
• 120ml of non boiling water, about 80°C 

📝 *Directions*
• Soften Whisk in 80°C water
• Sieve 1 scoop of powder
• Add 20ml to blend powder
• Add in remaining water
• Whisk for 2 mins in a bowl, no grains and foamy 
• Mix well and enjoy\! 
"""
      

    if query.data.split("_")[1] == '2' : 
        recipe_text = """
🍵🥛 *Matcha Latte Recipe*

🌿 *Ingredients* 
• 6g of Matcha Powder 
• 30ml of non boiling water, about 80°C
• 120ml of oat milk, prefably oatside barista
• 1 tsp sugar

📝 *Directions* 
• Soften Whisk in 80 deg water for 5 mins
• Sieve 2 scoops of powder
• Add 30ml of water
• Whisk for 2 mins in a bowl, no grains and thick consistency
• Whisk in sugar
• Prepare Cup, add Ice
• Add oatmilk into cup
• Add the whisked Matcha slowly
• Enjoy\! 
"""
        
    await query.edit_message_text(recipe_text, parse_mode=ParseMode.MARKDOWN_V2)

       



if __name__ == '__main__' : 
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('about', about_command))
    app.add_handler(CommandHandler('recipes', recipes_command))
    app.add_handler(CommandHandler('reviews', reviews_command))
    app.add_handler(CallbackQueryHandler(button_selection_handler))

    # Messages 
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors 
    app.add_error_handler(error)

    #polls the bot 
    print('Polling...')
    app.run_polling(poll_interval=3)
