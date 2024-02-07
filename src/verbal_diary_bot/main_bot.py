import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler


import verbal_diary_bot as vdb
from verbal_diary_bot import utils
from verbal_diary_bot.telegram_handlers import voice, audio, register_handler, deregister_handler, echo

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a your Verbal Diary Bot, please talk to me!")
    
# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(update.message.text)
    
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
    
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    
async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = vdb.user.User(update.effective_user.id, update.effective_user.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=user.get_user_info())

if __name__ == '__main__':
    application = ApplicationBuilder().token(utils.get_telegram_token()).build()
    
    # add user registration handler
    application.add_handler(register_handler)
    # add user deregistration handler
    application.add_handler(deregister_handler)
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    caps_handler = CommandHandler('caps', caps)
    application.add_handler(caps_handler)
    user_stats_handler = CommandHandler('user_stats', user_stats)
    application.add_handler(user_stats_handler)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)
    voice_handler = MessageHandler(filters.VOICE, voice)
    application.add_handler(voice_handler)
    audio_handler = MessageHandler(filters.AUDIO, audio)
    application.add_handler(audio_handler)   
    
    application.run_polling()