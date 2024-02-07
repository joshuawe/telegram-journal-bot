"""
database_operations.py

This module provides a set of functions to interact with the SQLite database for a Telegram bot application. It includes functionalities to create, read, update, and delete (CRUD) data related to users and messages.

Functions:
    connect_db() -> sqlite3.Connection:
        Establishes and returns a connection to the SQLite database.

    insert_user(user_id: int, name: str, notion_token: str) -> None:
        Inserts a new user record into the Users table.

    get_user(user_id: int) -> tuple:
        Retrieves a single user's details from the Users table based on user_id.

    update_user(user_id: int, **kwargs) -> None:
        Updates a user's information in the Users table.

    delete_user(user_id: int) -> None:
        Deletes a user's record from the Users table.

    insert_message(message_id: int, user_id: int, message: str, word_count: int, message_type: str, audio_length: int) -> None:
        Inserts a new message record into the Messages table.

    get_message(message_id: int) -> tuple:
        Retrieves a single message's details from the Messages table based on message_id.

    update_message(message_id: int, **kwargs) -> None:
        Updates a message's information in the Messages table.

    delete_message(message_id: int) -> None:
        Deletes a message's record from the Messages table.

This module is intended to be used as a part of the Telegram bot application, facilitating the management of database operations in a centralized and organized manner.
"""

import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import random

from verbal_diary_bot import utils


def connect_db():
    """Create a database connection."""
    db_path = utils.get_db_path()
    conn = sqlite3.connect(db_path)
    return conn

def insert_user(user_id: int, name: str, notion_token: str, database_id: str):
    """Insert a new user into the Users table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Users (user_id, name, notion_token, database_id) VALUES (?, ?, ?, ?)', (user_id, name, notion_token, database_id))
    conn.commit()
    conn.close()

def get_user(user_id: int):
    """Retrieve a user's details by user_id."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def get_all_users() -> list:
    """Retrieve all users from the Users table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users')
    user_data = cursor.fetchall()
    conn.close()
    return user_data

def update_user(user_id: int, name: str, notion_token: str, database_id: str):
    """Update a user's information in the Users table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE Users SET name = ?, notion_token = ?, database_id = ? WHERE user_id = ?', (name, notion_token, database_id, user_id))
    conn.commit()
    conn.close()
    
def insert_message(user_id:int, date:datetime, message: str, word_count: str, message_type: str, audio_length: float) -> int:
    """
        Insert a new message into the Messages table.
        Returns the message_id of the newly inserted message.
    """
    date_str = date.strftime('%Y-%m-%d %H:%M:%S %z')
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Messages (user_id, date, message, word_count, message_type, audio_length) VALUES (?, ?, ?, ?, ?, ?)', (user_id, date_str, message, word_count, message_type, audio_length))
    # get the message_id from the last inserted row
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id
    
def get_message(message_id) -> tuple:
    """Retrieve a message's details by message_id."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Messages WHERE message_id = ?', (message_id,))
    message_data = cursor.fetchone()
    conn.close()
    return message_data

def get_all_messages() -> list:
    """Retrieve all messages from the Messages table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Messages')
    message_data = cursor.fetchall()
    conn.close()
    return message_data

def get_messages_by_user(user_id: int) -> list:
    """Retrieve all messages sent by a user."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Messages WHERE user_id = ?', (user_id,))
    message_data = cursor.fetchall()
    conn.close()
    return message_data

def delete_user(user_id: int) -> None:
    """Delete a user's record from the Users and Messages table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Users WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM Messages WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def anonymize_user(user_id: int) -> None:
    """Anonymize a user's record in the Users and Messages table."""
    conn = connect_db()
    cursor = conn.cursor()
    # cursor.execute('DELETE FROM Users WHERE user_id = ?', (user_id,))
    # cursor.execute('DELETE FROM Messages WHERE user_id = ?', (user_id,))
    # delete notion token and database id
    cursor.execute('UPDATE Users SET name = NULL, notion_token = NULL, database_id = NULL WHERE user_id = ?', (user_id,))
    # set all entries of message in Message table of the user to NULL
    cursor.execute('UPDATE Messages SET message = NULL WHERE user_id = ?', (user_id,))
    
    random_user_id = int(f"999{random.randint(1000000000, 9999999999)}")
    # change user_id to a randomly generated number of 10 digits in both tables
    cursor.execute('UPDATE Users SET user_id = ? WHERE user_id = ?', (random_user_id, user_id))
    cursor.execute('UPDATE Messages SET user_id = ? WHERE user_id = ?', (random_user_id, user_id))
    conn.commit()
    conn.close()


def user_exists(user_id) -> bool:
    """Check if a user exists in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT EXISTS(SELECT 1 FROM Users WHERE user_id = ? LIMIT 1)', (user_id,))
    exists = cursor.fetchone()[0]
    conn.close()
    return exists == 1

def get_last_message_of_user(user_id):
    """Retrieve the last message sent by a user."""
    messages = get_messages_by_user(user_id)
    
    
    

if __name__ == '__main__':
    # print all user information
    all_users = get_all_users()
    print(" All users ".center(20, "="))
    for user in all_users:
        print(user)
        
        
    # print all message information
    all_messages = get_all_messages()
    print("\n", " All messages ".center(20, "="))
    for message in all_messages:
        print(message)
        
