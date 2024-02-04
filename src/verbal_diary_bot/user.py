"""This script defines the User class."""

from typing import Optional, Literal
from datetime import datetime
from zoneinfo import ZoneInfo

from . import database_operations as db

class User:
    user_id: str
    last_message_date: datetime
    
    
    def __init__(self, user_id: str, user_name: Optional[str] = None, notion_token: Optional[str] = None):
        self.user_id = user_id
        self.user_name = user_name
        # does user exist in the database?
        user_exists = db.user_exists(user_id)
        if not user_exists:
            # if not, add user to the database
            db.insert_user(user_id, user_name, notion_token)
        else:
            # check whether to update or not
            user_data = db.get_user(user_id)
            user_name = user_data[1] if user_name is None else user_name
            notion_token = user_data[2] if notion_token is None else notion_token
            if (user_name is not None) or (notion_token is not None):
                db.update_user(user_id, user_name, notion_token)
        
    def add_message(self, message: str, word_count: int, message_type: Literal['audio'], audio_length: float, date: Optional[datetime]=None,) -> None:
        """
        Adds a message to the database.

        Parameters
        ----------
        message : str
            The message in text format.
        word_count : int
            Number of words
        message_type : 'audio'
            For now only 'audio' is supported.
        audio_length : float
            Lenght of audio in seconds.
        """
        if date is None:
            date = datetime.now(ZoneInfo("Europe/Berlin"))
            
        db.insert_message(self.user_id, date, message, word_count, message_type, audio_length)
        return True


    def last_online(self) -> datetime:
        """Returns the date and time of the user's last message."""
        user_messages = db.get_messages_by_user(self.user_id)
        last_message = user_messages[-1]
        last_message_date = last_message[2]
        last_message_date = datetime.strptime(last_message_date, '%Y-%m-%d %H:%M:%S %z')
        return last_message_date


    def get_user_info(self) -> str:
        """
        Get some user data and associated statistics.
        """
        info_text = " USER INFO ".center(40, "=") + "\n"
        # add basic info (user_id, name, last_message_date, etc.)
        info_text += f"User ID: {self.user_id}\n"
        info_text += f"Name: {self.user_name}\n"
        last_message_date = self.last_online().strftime('%Y-%m-%d %H:%M:%S')        
        info_text += f"Last message date: {self.last_online()}\n"
        
        # number of messages sent
        user_messages = db.get_messages_by_user(self.user_id)
        num_messages = len(user_messages)
        avg_word_count = sum([message[4] for message in user_messages]) / num_messages
        total_word_count = sum([message[4] for message in user_messages])
        avg_audio_length = sum([message[6] for message in user_messages]) / num_messages
        total_audio_length = sum([message[6] for message in user_messages])
        
        info_text += f"Number of messages sent: {num_messages}\n"
        info_text += f"Average word count: {avg_word_count:.1f}\n"
        info_text += f"Total word count: {total_word_count}\n"
        info_text += f"Average audio length: {avg_audio_length:.1f}s ({avg_audio_length/60:.1f}min)\n"
        info_text += f"Total audio length: {total_audio_length:.1f}s ({total_audio_length/60:.1f}min)\n"
        
        info_text += "="*40
        
        return info_text


    def get_messages(self):
        user_messages = db.get_messages_by_user(self.user_id)
        return user_messages
