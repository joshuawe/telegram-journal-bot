from datetime import datetime, timedelta
from typing import Literal, Optional
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler


import verbal_diary_bot as vdb

from verbal_diary_bot import utils, notion, transcribe

logger = logging.getLogger(__name__)

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
        

def is_user_registered(func):
    def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
            Check if the user is registered
            If not, user will first have to register.
            Otherwise, the function/handler will be called.
        """
        user_id = update.effective_user.id
        user_exists = vdb.database_operations.user_exists(user_id)
        if not user_exists:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You are not registered. Please register first.")
        else:
            return func(update, context)
    return 
















""" ----------------------------------------------------------------
                        Register User
        This is part of an interactive session in the Telegram 
        chat. It will register a new user and ask a few quest-
        ions.
    ----------------------------------------------------------------
"""

NAME, PRIVACY, API_KEY, DATABASE_ID = range(4)
_api_key = None

# def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#         Register a new user in an interactive session in the Telegram chat.
#     """
#     user_id = update.effective_user.id
#     user_name = update.effective_user.username
#     notion_token = context.args[0] if len(context.args) > 0 else None
#     user = vdb.user.User(user_id, user_name, notion_token)
#     context.bot.send_message(chat_id=update.effective_chat.id, text="You are registered.")
    
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.username
    user_id = update.effective_user.id
    user_exists = vdb.database_operations.user_exists(user_id)
    # End converstaion if user is already registered
    if user_exists:
        await update.message.reply_text("You are already registered. To deregister use the command /deregister.", parse_mode='HTML')
        return ConversationHandler.END
    # Continue with registration if user not yet registered
    message1 = """Hello, I am your <b>Verbal Diary Assistant</b>!
I am here to assist you in your daily life. You want to journal and keep a diary, right? I see, it can be very tedious to write everything down. This is where I can assist you. You send me a voice message, whenever you feel like it and from wherever you are. Then I transcribe your message ans send you the transcription. In addition, I also store your transcription with your digital notes <i>(currently, only Notion is supported)</i>.
This means you can also access your diary entries digitally, alter them, add to them and more."""
    message2 = """How does this work?
Well, I am a Telegram Bot running on some Google Cloud server, trying to make sense of what you brabble. The latest speech2text recognition AI models help me with that. For this I currently user WhisperAI from OpenAI.
If you want to know more, just check out more about me here: 
<a href="https://github.com/joshuawe/telegram-journal-bot">Verbal Diary Assistant - Project Page</a>"""
    message3 = """Before we start, I would like to let you know about my privacy policy. All your data is used confidentially. No data is shared with third parties. No audio data is stored. You can delete all you user data at any time by using the <ins>/deregister</ins> command.

Do you agree to the privacy policy? Answer with 'yes' or 'no'."""
    await update.message.reply_text(message1, parse_mode='HTML')
    await update.message.reply_text(message2, parse_mode='HTML', disable_web_page_preview=True)
    await update.message.reply_text(message3, parse_mode='HTML')
    return PRIVACY

async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    privacy = update.message.text
    privacy = privacy.strip().lower()
    if privacy.lower() == 'yes':
        await update.message.reply_text("Thank you for agreeing to the privacy policy.")
        user_name = update.effective_user.username
        message1 = f"Your name is <b>{user_name}</b>, that is what you told Telegram and that is what I will remember."
        message2 = """To upload your transcription to Notion, I need your respective API key.
<i>Note: Providing the key will not grant me access to your entire Notion workspace. Instead it only allows access to a specific page, which you define.</i>
For more information on how to get your Notion API key, check out the <a href="https://github.com/joshuawe/telegram-journal-bot">Tutorial on retrieving page specific API key</a>.
Please provide your Notion API key."""
        await update.message.reply_text(message1, parse_mode='HTML')
        await update.message.reply_text(message2, parse_mode='HTML', disable_web_page_preview=True)
        return API_KEY
    else:
        await update.message.reply_text("I am sorry, but I cannot register you if you do not agree to the privacy policy.")
        return ConversationHandler.END

async def api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _api_key
    api_key = update.message.text
    _api_key = api_key.strip()
    # Here you can add the logic to register the user with their name and API key
    
    await update.message.reply_text("Received the API KEY. \nTo do: Test the API key first.")
    await update.message.reply_text('Next and final step: Provide the Database ID of the Notion page where you want to store your transcriptions.\n<i>For details check <a href="https://github.com/joshuawe/telegram-journal-bot">Tutorial</a></i>.', parse_mode='HTML', disable_web_page_preview=True)
    
    return DATABASE_ID

async def database_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _api_key
    user_id = update.effective_user.id
    user_name = update.effective_user.username
    notion_database_id = update.message.text.strip()
    user = vdb.user.User(user_id, user_name, _api_key, notion_database_id)
    await update.message.reply_text(u"\u2705" + " Thank you for registering. You can now send voice messages.")
    _api_key = None
    return ConversationHandler.END  # This ends the conversation

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _api_key
    _api_key = None
    user = update.message.from_user
    print(f"User {user.first_name} canceled the conversation.")
    await update.message.reply_text('Registration cancelled.')
    return ConversationHandler.END



register_handler = ConversationHandler(
        entry_points=[CommandHandler('register', start_registration)],
        states={
            PRIVACY: [MessageHandler(filters.TEXT & ~filters.COMMAND, privacy)],
            API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, api_key)],
            DATABASE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, database_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )




""" ----------------------------------------------------------------
                        /deregister User
        This is part of an interactive session in the Telegram 
        chat. It will register a new user and ask a few quest-
        ions.
    ----------------------------------------------------------------
"""
CONFIRM_DEREGISTER, FINAL_CONFIRMATION, CANCEL = range(3)

# async def deregister(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     user_name = update.effective_user.username
#     user = vdb.user.User(user_id, user_name)
#     context.bot.send_message(chat_id=update.effective_chat.id, text="You are deregistered.")
    
async def deregister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='yes'),
        InlineKeyboardButton("No", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Do you really want to deregister?', reply_markup=reply_markup)
    return CONFIRM_DEREGISTER

    
async def confirm_deregister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'yes':
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data='final_yes'),
            InlineKeyboardButton("No", callback_data='final_no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Are you sure you want to deregister? This action cannot be undone.", reply_markup=reply_markup)
        return FINAL_CONFIRMATION
    else:
        return CANCEL


async def final_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'final_yes':
        # Perform deregistration logic here
        vdb.user.delete_user_from_database(update.effective_user.id)
        print('User deleted!')  # Replace this with actual deregistration code
        await query.edit_message_text(text=u"\u2705" + " You have been deregistered.")
        return ConversationHandler.END
    else:
        return CANCEL

async def cancel_deregister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, id = update.effective_user.name, update.effective_user.id
    logger.info(f"User {user} (id: {id}) canceled the conversation.")
    # emoji green checkmark
    emoji = u"\u2705"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=u"\u274C" + ' Deregistration cancelled.')
    # await update.message.reply_text(u"\u274C" + ' Deregistration cancelled.')
    return ConversationHandler.END

    
    
    

deregister_handler = ConversationHandler(
    entry_points=[CommandHandler('deregister', deregister)],
    states={
        CONFIRM_DEREGISTER: [CallbackQueryHandler(confirm_deregister)],
        FINAL_CONFIRMATION: [CallbackQueryHandler(final_confirmation)],
        CANCEL: [CallbackQueryHandler(cancel_deregister)],
    },
    fallbacks=[CommandHandler('cancel', cancel_deregister)],
    # per_message=True
)
