import json

TOKEN_PATH = 'configs.json'

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