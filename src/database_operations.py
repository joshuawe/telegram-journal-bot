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

import utils


def connect_db():
    """Create a database connection."""
    db_path = utils.get_db_path()
    conn = sqlite3.connect(db_path)
    return conn

def insert_user(user_id, name, notion_token):
    """Insert a new user into the Users table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Users (user_id, name, notion_token) VALUES (?, ?, ?)', (user_id, name, notion_token))
    conn.commit()
    conn.close()

def get_user(user_id):
    """Retrieve a user's details by user_id."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def update_user(user_id, name, notion_token):
    """Update a user's information in the Users table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE Users SET name = ?, notion_token = ? WHERE user_id = ?', (name, notion_token, user_id))
    conn.commit()
    conn.close()
    
def insert_message(user_id, message, word_count, message_type, audio_length):
    """Insert a new message into the Messages table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Messages (user_id, message, word_count, message_type, audio_length) VALUES (?, ?, ?, ?, ?)', (user_id, message, word_count, message_type, audio_length))
    conn.commit()
    conn.close()
    
def get_message(message_id):
    """Retrieve a message's details by message_id."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Messages WHERE message_id = ?', (message_id,))
    message_data = cursor.fetchone()
    conn.close()
    return message_data

def delete_user(user_id):
    """Delete a user's record from the Users table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# Similarly, define functions for insert_message, get_message, update_user, delete_user, etc.

# Example of usage
# insert_user(1, 'Alice', 'token123')
# user = get_user(1)
# print(user)
