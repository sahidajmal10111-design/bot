import sqlite3

DB_NAME = "chat_memory.db"


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (user_id INTEGER, role TEXT, content TEXT,
                  ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS profiles
                 (user_id INTEGER PRIMARY KEY, name TEXT, preferences TEXT)''')
    conn.commit()
    conn.close()


def save_message(user_id, role, content):
    """Save a message and keep only the last 20 per user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
              (user_id, role, content))
    c.execute("""DELETE FROM messages WHERE user_id=? AND rowid NOT IN 
                 (SELECT rowid FROM messages WHERE user_id=? 
                  ORDER BY rowid DESC LIMIT 20)""",
              (user_id, user_id))
    conn.commit()
    conn.close()


def get_history(user_id):
    """Return chat history for a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE user_id=? ORDER BY rowid ASC",
              (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]


def update_profile(user_id, name=None, preferences=None):
    """Update user profile (long-term memory)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO profiles (user_id) VALUES (?)", (user_id,))
    if name:
        c.execute("UPDATE profiles SET name=? WHERE user_id=?", (name, user_id))
    if preferences:
        c.execute("UPDATE profiles SET preferences=? WHERE user_id=?",
                  (preferences, user_id))
    conn.commit()
    conn.close()


def get_profile(user_id):
    """Get stored user profile."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, preferences FROM profiles WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"name": row[0], "preferences": row[1]}
    return {"name": None, "preferences": None}


def clear_history(user_id):
    """Delete all messages for a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
