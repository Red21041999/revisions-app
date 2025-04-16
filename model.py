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
    cur.execute("""
        SELECT id FROM participations
        WHERE user_id = ? AND session_id = ?
    """, (user_id, session_id))
    existing = cur.fetchone()
    if existing:
        conn.close()
        return False
    cur.execute("""
        INSERT INTO participations (user_id, session_id)
        VALUES (?, ?)
    """, (user_id, session_id))
    conn.commit()
    conn.close()
    return True

def delete_session(session_id, user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM study_sessions WHERE id = ? AND creator_id = ?", (session_id, user_id))
    conn.commit()
    conn.close()

# -----------------------
# Gestion des messages de chat par session
# -----------------------

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
    cur.execute("""
        SELECT m.message AS content, m.timestamp AS created_at, u.name AS user_name
        FROM chat_messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.session_id = ?
        ORDER BY m.timestamp ASC
    """, (session_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# -----------------------
# Participants
# -----------------------

def get_participants_for_session(session_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT users.name
        FROM participations
        JOIN users ON participations.user_id = users.id
        WHERE participations.session_id = ?
    """, (session_id,))
    rows = cur.fetchall()
    conn.close()
    return [row["name"] for row in rows]

def get_all_sessions_with_participants():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM study_sessions")
    sessions = cur.fetchall()
    conn.close()

    sessions_with_parts = []
    for s in sessions:
        s_dict = dict(s)
        s_dict["participants"] = get_participants_for_session(s["id"])
        sessions_with_parts.append(s_dict)

    return sessions_with_parts

def user_is_participant(user_id, session_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id
        FROM participations
        WHERE user_id = ? AND session_id = ?
    """, (user_id, session_id))
    row = cur.fetchone()
    conn.close()
    return (row is not None)


