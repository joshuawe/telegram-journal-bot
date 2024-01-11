"""This script sets up the database that stores all the user information."""

import sqlite3
from pathlib import Path

import utils

def create_table(conn, table_name, fields):
    """Create a table with the given name and fields."""
    cursor = conn.cursor()
    fields_str = ', '.join(fields)
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({fields_str})')
    conn.commit()


def setup_db():
    """
    Sets up the database that stores all the user information.
    """
    db_path = Path(utils.get_db_path())
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Connect to SQLite database (creates the file if it doesn't exist)
    conn = sqlite3.connect(db_path)

    # Define the fields for the Users table
    db_configs = utils.get_config()['database']
    USER_FIELDS = db_configs['Users_fields']
    MESSAGE_FIELDS = db_configs['Messages_fields']

    # Create the Users table
    create_table(conn, 'Users', USER_FIELDS)

    # Create the Messages table
    create_table(conn, 'Messages', MESSAGE_FIELDS)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()



if __name__ == '__main__':
    setup_db()
