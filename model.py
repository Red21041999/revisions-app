import sqlite3

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------
# Gestion des utilisateurs
# -----------------------

def get_user_by_name(name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = ?", (name,))
    user = cur.fetchone()
    conn.close()
    return user

def create_user(name, hashed_password):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, hashed_password))
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return {'id': user_id, 'name': name}
    except sqlite3.IntegrityError:
        return None

# -----------------------
# Gestion des cours
# -----------------------

def get_all_courses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    conn.close()
    return [dict(course) for course in courses]

def add_course(title, description, file, user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO courses (title, description, file, user_id) VALUES (?, ?, ?, ?)",
                (title, description, file, user_id))
    conn.commit()
    conn.close()

def delete_course(course_id, user_id):
    conn = get_db()
    cur = conn.cursor()
    # Suppression seulement si le cours appartient à l'utilisateur
    cur.execute("DELETE FROM courses WHERE id = ? AND user_id = ?", (course_id, user_id))
    conn.commit()
    conn.close()


# -----------------------
# Gestion des sessions de révision
# -----------------------

def get_all_sessions():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM study_sessions")
    sessions = cur.fetchall()
    conn.close()
    return [dict(session) for session in sessions]

def add_session(subject, date, time, creator_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO study_sessions (subject, date, time, creator_id) VALUES (?, ?, ?, ?)",
                (subject, date, time, creator_id))
    conn.commit()
    conn.close()

def add_participation(user_id, session_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO participations (user_id, session_id) VALUES (?, ?)",
                (user_id, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id, user_id):
    conn = get_db()
    cur = conn.cursor()
    # Suppression seulement si la session a été créée par cet utilisateur
    cur.execute("DELETE FROM study_sessions WHERE id = ? AND creator_id = ?", (session_id, user_id))
    conn.commit()
    conn.close()

def add_chat_message(session_id, user_id, message):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_messages (session_id, user_id, message) VALUES (?, ?, ?)",
                (session_id, user_id, message))
    conn.commit()
    conn.close()

def get_chat_messages(session_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT m.message, m.timestamp, u.name FROM chat_messages m JOIN users u ON m.user_id = u.id WHERE m.session_id = ? ORDER BY m.timestamp ASC", (session_id,))
    messages = cur.fetchall()
    conn.close()
    return [dict(msg) for msg in messages]
