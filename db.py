import os
import sqlite3

conn = sqlite3.connect(os.path.join('db', 'reviews.db'), check_same_thread=False)
cursor = conn.cursor()


def get_cursor():
    return cursor


def _init_db():
    """Initializes the database"""
    with open('createdb.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Checks if the database is initialized, if not, initializes"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type = 'table' AND name = 'user'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
