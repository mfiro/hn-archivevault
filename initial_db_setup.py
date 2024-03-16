import sqlite3


def setup_database():
    connection = sqlite3.connect('./hn_archive.db')
    cursor = connection.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY,
        by TEXT,
        score INTEGER,
        time INTEGER,
        title TEXT,
        type TEXT,
        url TEXT,
        time_str TEXT,
        synced_at INTEGER,
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY,
        by TEXT,
        parent INTEGER,
        text TEXT,
        time INTEGER,
        type TEXT,
        time_str TEXT
    )
    ''')
    
    connection.commit()
    connection.close()

setup_database()