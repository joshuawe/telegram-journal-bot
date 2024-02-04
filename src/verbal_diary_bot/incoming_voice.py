from datetime import datetime
from typing import Literal

from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

from . import utils, notion, transcribe

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await audio_or_voice(update, context, 'audio')
    
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await audio_or_voice(update, context, 'voice')

async def audio_or_voice(update: Update, context: ContextTypes.DEFAULT_TYPE, audio_or_voice: Literal['audio', 'voice']):   
    
    # chose which API to use (OpenAI/Hugginface)
    # transcribe_from_file = transcribe.transcribe_from_file_huggingface 
    transcribe_from_file = transcribe.transcribe_from_file_openai 

    # Getting the voice message
    if audio_or_voice == 'audio':
        message = update.message.audio
    elif audio_or_voice == 'voice':
        message = update.message.voice
    else:
        raise ValueError(f"audio_or_voice must be either 'audio' or 'voice'. Got {audio_or_voice}")

    # Getting the file ID
    file_id = message.file_id

    # Downloading the file
    new_file = await context.bot.get_file(file_id)
    file_path = new_file.file_path

    # Save the audio file locally (Optional)
    if audio_or_voice == 'audio':
        print(message.mime_type, "\n\n")
        save_path = utils.get_voice_save_path() / f"{file_id}.m4a"
    else:
        save_path = utils.get_voice_save_path() / f"{file_id}.ogg"
    # create folder if not exists
    save_path.parent.mkdir(parents=True, exist_ok=True)
    print(save_path.exists())
    
    
    await new_file.download_to_drive(save_path)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=u"\u2705 Audio message received and downloaded.")

    # --- Transcribe the audio file ---
    transcription = await transcribe_from_file(save_path, context, update.effective_chat.id)
    
    # Check for error
    if 'error' in transcription.keys():
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {transcription}")  
        raise RuntimeError(f"Error in function {transcribe_from_file}: {transcription}")     
        
        
    else:
        # check for empty string
        text = transcription['text'] if transcription['text'] != "" else " "
        # check for too long string
        if len(text) > 4096:  # telegram message char limit
            for x in range(0, len(text), 4096):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=text[x:x+4096])
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    # save transcription to file
    transcription_save_path = save_path.parent / f"{file_id}.txt"
    transcription_save_path.write_text(transcription['text'])
    
    # --- append to Notion page ---
    try:
        response = notion.append_transcription(
            utils.get_notion_token(), 
            utils.get_notion_database_id(), 
            utils.get_notion_page_properties(), 
            transcription
        )
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Notion Error: {e}")
        raise e
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=u"\u2705 Transcription appended to Notion.")