from datetime import datetime, timedelta
from typing import Literal, Optional

from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

import verbal_diary_bot as vdb

from . import utils, notion, transcribe

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle audio messages. These are audio files sent to the chat. This is a wrapper."""
    await audio_or_voice(update, context, 'audio')
    
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages. These are voice messages sent to the chat. This is wrapper."""
    await audio_or_voice(update, context, 'voice')

async def audio_or_voice(update: Update, context: ContextTypes.DEFAULT_TYPE, audio_or_voice: Literal['audio', 'voice']):   
    """
    Handle audio or voice messages. Transcribe them, and then store them in the database.

    Parameters
    ----------
    update : Update
        The update object from the Telegram API.
    context : ContextTypes.DEFAULT_TYPE
        The context object from the Telegram API.
    audio_or_voice : Literal['audio', 'voice']
        Whether it is a voice or audio message. Telegram stores the associated data slightly differently.

    Raises
    ------
    ValueError
        If audio_or_voice is not 'audio' or 'voice'.
    RuntimeError
        If an error occurs in the transcription process.
    e
        If an error occurs in the Notion append process.
    """
    # Create the user object
    user_id = update.effective_user.id
    user_name = update.effective_user.username
    user = vdb.user.User(user_id, user_name)
    last_online = user.last_online()
    
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
            user.get_notion_token(), 
            user.get_database_id(), 
            utils.get_notion_page_properties(), 
            transcription
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=u"\u2705 Transcription appended to Notion.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Notion Error: {e}")
        raise e
    
    
    # get message date from update
    message_date = update.message.date
    # add user's message to the database
    word_count = len(text.split())
    audio_length = message.duration if audio_or_voice == 'audio' else message.duration
    user.add_message(text, word_count, 'audio', audio_length, message_date)
    
    # send user stats
    await user_stats(update, context, last_online)
    
    
    
async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, last_online: Optional[datetime]=None):
    """
        Send user statistics if they have not been provided already within the last 24 h.
    """
    user_id = update.effective_user.id
    user = vdb.user.User(user_id)
    # check if last message is more than 24 hours ago
    if last_online is None:
        last_online = user.last_online()
    now = datetime.now(last_online.tzinfo)
    elapsed_time = now - last_online
    if elapsed_time > timedelta(hours=12):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=user.get_user_info())