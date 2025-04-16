import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Création de la table des utilisateurs
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Table des cours partagés
c.execute('''
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    file TEXT,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Table des sessions de révision
c.execute('''
CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    creator_id INTEGER,
    FOREIGN KEY(creator_id) REFERENCES users(id)
)
''')

# Table des participations aux sessions (avec contrainte pour éviter les doublons)
c.execute('''
CREATE TABLE IF NOT EXISTS participations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(session_id) REFERENCES study_sessions(id),
    UNIQUE(user_id, session_id)
)
''')

# Table des messages de chat liés à une session
c.execute('''
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES study_sessions(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Enregistrement et fermeture
conn.commit()
conn.close()


