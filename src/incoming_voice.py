from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I see, you are sending me an audio message. I am still learning how to process audio messages.")

    # Getting the voice message
    voice_message = update.message.voice
    # Getting the file ID
    file_id = voice_message.file_id

    # Downloading the file
    new_file = await context.bot.get_file(file_id)
    file_path = new_file.file_path

    # Save the audio file locally (Optional)
    await new_file.download(f"{file_id}.ogg")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Audio message received and downloaded.")
