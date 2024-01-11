"""This script sets up the database that stores all the user information."""

import sqlite3
from pathlib import Path

import utils


def setup_db():
    """
    Sets up the database that stores all the user information.
    """
    db_path = Path(utils.get_db_path())
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Connect to SQLite database (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Create a cursor object using the cursor method
    cursor = conn.cursor()

    # Create the Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        api_token TEXT,
        last_message DATETIME
    )
    ''')

    # Create the Messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Messages (
        message_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        message TEXT,
        word_count INTEGER,
        message_type TEXT,
        audio_length INTEGER,
        FOREIGN KEY(user_id) REFERENCES Users(user_id)
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()



if __name__ == '__main__':
    setup_db()
