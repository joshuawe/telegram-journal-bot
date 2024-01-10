import json
from pathlib import Path

TOKEN_PATH = 'configs.json'

def get_config():
    with open(TOKEN_PATH) as token_file:
        config = json.load(token_file)
    return config

def get_telegram_token():
    with open(TOKEN_PATH) as token_file:
        token = json.load(token_file)['telegram']['token']
    return token

def get_allowed_chat_ids():
    with open(TOKEN_PATH) as token_file:
        json_file = json.load(token_file)['telegram']
        user_ids = json_file['allowed_chat_ids']
        user_names = json_file['allowed_chat_names']
    return user_ids, user_names

def get_voice_save_path():
    with open(TOKEN_PATH) as token_file:
        voice_save_path = json.load(token_file)['save_paths']['voice_messages']
    return Path(voice_save_path)

def get_huggingface_token():
    with open(TOKEN_PATH) as token_file:
        token = json.load(token_file)['huggingface']['token']
    return token

def get_speech2text_model_name():
    with open(TOKEN_PATH) as token_file:
        model_name = json.load(token_file)['huggingface']['speech2text_model_name']
    return model_name

def get_notion_token():
    with open(TOKEN_PATH) as token_file:
        token = json.load(token_file)['notion']['token']
    return token

def get_notion_database_id():
    with open(TOKEN_PATH) as token_file:
        database_id = json.load(token_file)['notion']['database_id']
    return database_id

def get_notion_page_properties():
    with open(TOKEN_PATH) as token_file:
        page_properties = json.load(token_file)['notion']['page_properties']
    return page_properties

def get_openai_token():
    with open(TOKEN_PATH) as token_file:
        token = json.load(token_file)['openai']['token']
    return token