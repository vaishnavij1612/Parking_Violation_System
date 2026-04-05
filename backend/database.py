import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'violations.db')


def get_db_connection():
    """
    Open and return a SQLite connection.
    Creates the violations table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            plate      TEXT    NOT NULL,
            timestamp  INTEGER NOT NULL,
            dwell_time INTEGER NOT NULL,
            fine       INTEGER NOT NULL,
            severity   TEXT    NOT NULL,
            image_path TEXT    NOT NULL
        )
    ''')
    
    # Check if severity column exists (for backward compatibility)
    cursor = conn.execute("PRAGMA table_info(violations)")
    columns = [row['name'] for row in cursor.fetchall()]
    if 'severity' not in columns:
        conn.execute("ALTER TABLE violations ADD COLUMN severity TEXT NOT NULL DEFAULT 'N/A'")
    
    conn.commit()

    return conn


def insert_violation(conn, plate, timestamp, dwell_time, fine, severity, image_path):
    """
    Insert a violation record into the database.
    Caller is responsible for commit() and close().
    """
    conn.execute(
        '''
        INSERT INTO violations (plate, timestamp, dwell_time, fine, severity, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (plate, timestamp, dwell_time, fine, severity, image_path)
    )
