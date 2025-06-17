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

Hi there fellow matcha lovers 💚 , this is a bot I have created to document down my journey in SG 🇸🇬 so far into the world of matcha 🍵

Feel free to use this bot to get the latest recipes, very biased reviews and random content that I'll be adding \here 😎
 
*disclaimer* : I am in no way an expert in matcha, this serves as my matcha journal for everyone to read 
"""
    await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN_V2)


async def matcha101_command(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None : 
    matcha101_text = """

*WHY MATCHA 🍵* 

Matcha is a powdered green tea where you drink the entire leaf 🌱, giving you more nutrients than regular steeped tea 🤯

*Key Health Benefits*
🧠 Improved Brain Function 
❤️‍🔥 Better Heart Health 
🏋️ Weight Management
💪 Antioxidant Power 

*Quick Tips for Maximum Benefit*
• Start small ¼ tsp to adjust to the taste
• Store properly in fridge to preserve nutrients
• Can mix with water or milk based on preference
• No special equipment needed for basic \preparation


"""
    await update.message.reply_text(matcha101_text, parse_mode=ParseMode.MARKDOWN_V2)

async def channel_command(update: Update, context:ContextTypes.DEFAULT_TYPE)  : 
    channel_text = """

Join my matcha Tele channel 😎  https://t.me/+QxqtsjTl5dZlMmM1

"""
    await update.message.reply_text(channel_text, parse_mode= None)

async def recipes_command(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None : 
    await recipes_buttons(update, context)


async def quiz_command(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None : 
    await quiz_buttons(update, context)


async def reviews_command(update: Update, context:ContextTypes.DEFAULT_TYPE)  -> None : 
    await reviews_buttons(update, context)
    # await update.message.reply_text('Reviews coming Soon!')



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
• Enjoy 🤤
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
• Enjoy 🤤
"""
        
    await query.edit_message_text(recipe_text, parse_mode=ParseMode.MARKDOWN_V2)


async def reviews_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Matcha Brands", callback_data='review_1')],
        [InlineKeyboardButton("Cafes in SG 🇸🇬 ", callback_data='review_2')],
    
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Select your recipe to view', reply_markup=reply_markup)

async def reviews_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data.split("_")[1] == '1':
        review_text = """
        Coming Soon 🌚
"""
      

    if query.data.split("_")[1] == '2' : 
        review_text = """
        Coming Soon 🌚
"""
        
    await query.edit_message_text(review_text, parse_mode=ParseMode.MARKDOWN_V2)


       
async def quiz_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Chanoyu", callback_data='quiz_1')],
        [InlineKeyboardButton("Gyokuro", callback_data='quiz_2')],
        [InlineKeyboardButton("Sencha", callback_data='quiz_3')],
        [InlineKeyboardButton("Matcha-do", callback_data='quiz_4')],
    
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('What is the traditional Japanese tea ceremony called 🤔', reply_markup=reply_markup)


async def quiz_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data.split("_")[1] == '1':
        quiz_text = """
         ✅ *Wa so smart*
"""
      

    if query.data.split("_")[1] == '2' : 
        quiz_text = """
         ❌ *Gyokuro* is a type of green tea from Japan
"""

    if query.data.split("_")[1] == '3' : 
            quiz_text = """
        ❌ *Sencha* is a type of Japanese green tea which is prepared by infusing the processed whole tea leaves in hot water
"""

    if query.data.split("_")[1] == '4' : 
            quiz_text = """
        ❌ *Matcha\-do* is the way of matcha \(I think\)
"""
        
    await query.edit_message_text(quiz_text, parse_mode=ParseMode.MARKDOWN_V2)


if __name__ == '__main__' : 
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('about', about_command))
    app.add_handler(CommandHandler('recipes', recipes_command))
    app.add_handler(CommandHandler('quiz', quiz_command))
    app.add_handler(CommandHandler('matcha101', matcha101_command))
    app.add_handler(CommandHandler('channel', channel_command))
    app.add_handler(CommandHandler('reviews', reviews_command))
    app.add_handler(CallbackQueryHandler(reviews_button_handler, pattern='^review_'))
    app.add_handler(CallbackQueryHandler(button_selection_handler, pattern='^button_'))
    app.add_handler(CallbackQueryHandler(quiz_button_handler, pattern='^quiz_'))
    

    # Messages 
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors 
    app.add_error_handler(error)

    #polls the bot 
    print('Polling...')
    app.run_polling(poll_interval=3)
