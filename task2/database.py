import sqlite3

DB_NAME = "parser.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def clear_pages():
    """Удаляет все записи из таблицы pages."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pages")
    conn.commit()
    conn.close()

def save_page(url, title):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pages (url, title) VALUES (?, ?)",
        (url, title)
    )
    conn.commit()
    conn.close()

def get_all_pages():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url, title, created_at FROM pages")
    rows = cursor.fetchall()
    conn.close()
    return rows