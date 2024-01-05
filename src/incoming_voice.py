from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

import utils

async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # send 'not yet implemented' message
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I see, you are sending me an audio message. I am still learning how to process audio messages.")
    

    # Getting the voice message
    voice_message = update.message.voice
    # Getting the file ID
    file_id = voice_message.file_id

    # Downloading the file
    new_file = await context.bot.get_file(file_id)
    file_path = new_file.file_path

    # Save the audio file locally (Optional)
    save_path = utils.get_voice_save_path() / f"{file_id}.ogg"
    # create folder if not exists
    save_path.parent.mkdir(parents=True, exist_ok=True)
    print(save_path.exists())
    
    
    await new_file.download_to_drive(save_path)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Audio message received and downloaded.")