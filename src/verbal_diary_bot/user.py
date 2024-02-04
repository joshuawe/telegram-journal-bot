"""This script defines the User class."""

from typing import Optional
from datetime import datetime

from . import database_operations as db

class User:
    user_id: str
    last_message_date: datetime
    
    
    def __init__(self, user_id: str, user_name: Optional[str] = None, notion_token: Optional[str] = None):
        self.user_id = user_id
        self.last_message_date = None
        # does user exist in the database?
        user_exists = db.user_exists(user_id)
        if not user_exists:
            # if not, add user to the database
            db.insert_user(user_id, user_name, notion_token)
        else:
            # load user data
            pass
        
    def add_message(self, message: str, word_count: int, message_type: str, audio_length: int):
        db.insert_message(self.user_id, message, word_count, message_type, audio_length)