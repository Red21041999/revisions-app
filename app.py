from flask import Flask, render_template, request, redirect, session, abort, url_for, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import model
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'

# Dossier de fichiers uploadés
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Sessions
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# -----------------------
# Décorateur
# -----------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

# -----------------------
# Routes publiques
# -----------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        hashed = generate_password_hash(password)
        user = model.create_user(name, hashed)
        if user is None:
            flash("Nom d'utilisateur déjà pris.")
            return redirect(url_for('register'))
        session['user_id'] = user['id']
        session['user_name'] = name
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = model.get_user_by_name(name)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash("Connexion réussie.")
            return redirect(url_for('dashboard'))
        else:
            flash("Identifiants incorrects.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    flash("Déconnexion réussie.")
    return redirect(url_for('index'))

# -----------------------
# Routes protégées
# -----------------------
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/courses')
@login_required
def courses():
    courses = model.get_all_courses()
    return render_template('courses.html', courses=courses)

@app.route('/upload_course', methods=['GET', 'POST'])
@login_required
def upload_course():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        uploaded_file = request.files.get('file')

        if uploaded_file and uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
        else:
            filename = None

        model.add_course(title, description, filename, session['user_id'])
        flash("Cours ajouté avec succès.")
        return redirect(url_for('courses'))

    return render_template('upload_course.html')

@app.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    model.delete_course(course_id, session['user_id'])
    flash("Cours supprimé avec succès.")
    return redirect(url_for('courses'))

@app.route('/sessions')
@login_required
def sessions():
    # On récupère toutes les sessions avec leur liste de participants
    sessions_list = model.get_all_sessions_with_participants()
    return render_template('sessions.html', sessions=sessions_list)

@app.route('/create_session', methods=['GET', 'POST'])
@login_required
def create_session():
    if request.method == 'POST':
        subject = request.form['subject']
        date = request.form['date']
        time = request.form['time']
        model.add_session(subject, date, time, session['user_id'])
        flash("Session créée.")
        return redirect(url_for('sessions'))
    return render_template('create_session.html')

@app.route('/join_session', methods=['POST'])
@login_required
def join_session():
    session_id = request.form['session_id']
    user_id = session['user_id']  # on récupère l'utilisateur connecté
    model.add_participation(user_id, session_id)
    flash("Inscription à la session réussie.")
    return redirect(url_for('sessions'))

@app.route('/delete_session/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    model.delete_session(session_id, session['user_id'])
    flash("Session supprimée avec succès.")
    return redirect(url_for('sessions'))

@app.route('/session/<int:session_id>/chat', methods=['GET', 'POST'])
@login_required
def session_chat(session_id):
    user_id = session['user_id']

    # Vérifier si l'utilisateur est déjà inscrit à la session
    if not model.user_is_participant(user_id, session_id):
        flash("Vous n'êtes pas inscrit à cette session, accès refusé.")
        return redirect(url_for('sessions'))  # ou page d'erreur si tu préfères

    if request.method == 'POST':
        message = request.form['message']
        if message.strip() != "":
            model.add_chat_message(session_id, user_id, message)
        return redirect(url_for('session_chat', session_id=session_id))

    messages = model.get_chat_messages(session_id)
    return render_template('chat.html', session_id=session_id, messages=messages)

@app.route('/add_chat_message', methods=['POST'])
@login_required
def add_chat_message():
    session_id = int(request.form['session_id'])  # cast en int, plus sûr
    content = request.form['content']
    user_id = session['user_id']

    # Vérifier que l'utilisateur est inscrit
    if not model.user_is_participant(user_id, session_id):
        flash("Vous n'êtes pas inscrit à cette session.")
        return redirect(url_for('sessions'))

    # ✅ Bon ordre des arguments
    model.add_chat_message(session_id, user_id, content)
    return redirect(url_for('session_chat', session_id=session_id))




# -----------------------
# Gestion des erreurs
# -----------------------
@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

# -----------------------
# Lancement
# -----------------------
if __name__ == '__main__':
    app.run(debug=True)

