from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jinja2 import TemplateNotFound
import mysql.connector
from argon2 import PasswordHasher, exceptions as argon2_exceptions
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()
import bleach
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config.update({
    'TEMPLATES_AUTO_RELOAD': True,
    'UPLOAD_FOLDER': 'static/uploads/ProfilePics',
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_PERMANENT': True,
    'PERMANENT_SESSION_LIFETIME': 3600,
    'SESSION_COOKIE_SAMESITE': 'Lax'
})

FERNET_KEY = os.environ['FERNET_KEY'] 
fernet = Fernet(FERNET_KEY)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per minute"])
ph = PasswordHasher()

# --- DB Connection ---
db = mysql.connector.connect(
    host="studylink_mysql_db",
    user="root",
    password="root",
    database="studylink",
    charset='utf8mb4',
    collation='utf8mb4_unicode_ci'
)
cursor = db.cursor()
cursor.execute("SET NAMES utf8mb4")
cursor.execute("SET CHARACTER SET utf8mb4")
cursor.execute("SET character_set_connection=utf8mb4")
cursor.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_input(data):
    return bleach.clean(data, strip=True)


# --- ROUTES ---

# HTML Redirects

@app.route('/<page>.html')
def html_redirect(page):
    # Special case: redirect /conversa.html to /conversa/0
    if page == 'conversa':
        return redirect(url_for('conversa', conversation_id=0), code=301)

    page_map = {
        'login': 'login_page',
        'registo': 'registo_page',
        'conta': 'conta',
        'dashboard': 'dashboard',
        'matching': 'matching',
    }

    if page in page_map:
        return redirect(url_for(page_map[page]), code=301)

    try:
        return render_template(f"{page}.html")
    except TemplateNotFound:
        flash("Página não encontrada!", "error")
        return redirect(url_for('login_page'))


# Auth
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('registo.html')

    try:
        name = bleach.clean(request.form['name'])
        username = bleach.clean(request.form['username'].strip().lower())
        email = bleach.clean(request.form['email'].strip().lower())
        password = bleach.clean(request.form['password'])
        confirm_password = bleach.clean(request.form['confirm-password'])

        session['form_data'] = {'name': name, 'username': username, 'email': email}

        if password != confirm_password:
            flash("As passwords não coincidem.", "error")
            return redirect(url_for('registo_page'))

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            flash("Nome de utilizador ou email já estão registados!", "error")
            return redirect(url_for('registo_page'))
        cursor.close()

        hashed_password = ph.hash(password)

        cursor = db.cursor()
        cursor.execute("INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)",
                       (name, username, email, hashed_password))
        user_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO user_settings (user_id, profile_pic, bio, class_year, course)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, 'static/uploads/ProfilePics/default.jpg', None, None, None))
        db.commit()
        cursor.close()

        session.pop('form_data', None)
        flash("Registo bem-sucedido!", "success")
        return redirect(url_for('registo_page'))

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
    except Exception as e:
        flash(f"Erro inesperado: {e}", "error")

    return redirect(url_for('registo_page'))


@app.route('/login', methods=['POST'])
def login():
    try:
        identifier = bleach.clean(request.form.get('identifier'))
        password = bleach.clean(request.form.get('password'))
        if not identifier or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('login_page', identifier=identifier))

        identifier = identifier.lower()
        cursor = db.cursor(dictionary=True)
        query = "SELECT id, username, password FROM users WHERE email = %s" if "@" in identifier else \
                "SELECT id, username, password FROM users WHERE username = %s"
        cursor.execute(query, (identifier,))
        user = cursor.fetchone()
        cursor.close()

        if user and ph.verify(user['password'], password):
            session.update({'user_id': user['id'], 'username': user['username'], 'login_success': True})
            flash("🎓Credenciais Aceites! A fazer login...", "success")
            return redirect(url_for('login_page'))

        flash("Nome de utilizador ou password inválidos.", "error")

    except argon2_exceptions.VerifyMismatchError:
        flash("Nome de utilizador ou password inválidos.", "error")
    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
    except Exception as e:
        flash(f"Erro geral: {e}", "error")

    return redirect(url_for('login_page', identifier=identifier))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))


# Pages
@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/registo_page')
def registo_page():
    return render_template('registo.html')


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.name, IFNULL(us.profile_pic, 'static/uploads/ProfilePics/default.jpg') AS profile_pic
        FROM users u LEFT JOIN user_settings us ON u.id = us.user_id
        WHERE u.id = %s
    """, (session.get('user_id'),))
    user = cursor.fetchone()
    cursor.close()
    return render_template('dashboard.html', user=user)


@app.route('/conta')
def conta():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    user_id = session.get('user_id')
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT u.name, u.email, u.username,
                   IFNULL(us.profile_pic, 'static/uploads/ProfilePics/default.jpg') AS profile_pic,
                   IFNULL(us.bio, '') AS bio, IFNULL(us.class_year, '') AS class_year,
                   IFNULL(us.course, '') AS course
            FROM users u LEFT JOIN user_settings us ON u.id = us.user_id
            WHERE u.id = %s
        """, (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT name FROM courses")
        courses = cursor.fetchall()

        course_units = []
        if user and user['course']:
            cursor.execute("""
                SELECT cu.id, cu.name FROM courses c
                JOIN course_curricular_units ccu ON c.id = ccu.course_id
                JOIN curricular_units cu ON cu.id = ccu.curricular_unit_id
                WHERE c.name = %s ORDER BY cu.name
            """, (user['course'],))
            course_units = cursor.fetchall()

        cursor.execute("SELECT subject_id, role FROM user_subjects WHERE user_id = %s", (user_id,))
        subject_roles = cursor.fetchall()

        mentor_unit_ids = [str(r['subject_id']) for r in subject_roles if r['role'] == 'mentor']
        mentee_unit_ids = [str(r['subject_id']) for r in subject_roles if r['role'] == 'mentee']

        return render_template('conta.html', user=user, courses=courses, units=course_units,
                               mentor_unit_ids=mentor_unit_ids, mentee_unit_ids=mentee_unit_ids)
    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
        return redirect(url_for('login_page'))
    finally:
        cursor.close()


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    username = session['username']
    name = sanitize_input(request.form.get('name', ''))
    bio = sanitize_input(request.form.get('bio', ''))
    class_year = request.form.get('class_year', '')
    course = request.form.get('course', '')

    # Handle profile image
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{username}.{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT profile_pic FROM user_settings WHERE user_id = %s", (user_id,))
            old_pic = cursor.fetchone()
            if old_pic and old_pic['profile_pic'] != 'static/uploads/ProfilePics/default.jpg':
                if os.path.exists(old_pic['profile_pic']):
                    os.remove(old_pic['profile_pic'])

            file.save(file_path)
            relative_path = f"static/uploads/ProfilePics/{filename}"
            cursor.execute("UPDATE user_settings SET profile_pic = %s WHERE user_id = %s",
                           (relative_path, user_id))
            db.commit()
            cursor.close()

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            UPDATE users u JOIN user_settings us ON u.id = us.user_id
            SET u.name = %s, us.bio = %s, us.class_year = %s, us.course = %s
            WHERE u.id = %s
        """, (name, bio, class_year, course, user_id))

        cursor.execute("DELETE FROM user_subjects WHERE user_id = %s", (user_id,))

        for uid in request.form.getlist('mentor_units'):
            cursor.execute("INSERT INTO user_subjects (user_id, subject_id, role) VALUES (%s, %s, 'mentor')", (user_id, uid))

        for uid in request.form.getlist('mentee_units'):
            if uid not in request.form.getlist('mentor_units'):
                cursor.execute("INSERT INTO user_subjects (user_id, subject_id, role) VALUES (%s, %s, 'mentee')", (user_id, uid))

        db.commit()
        flash("Conta atualizada com sucesso!", "success")

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
    finally:
        cursor.close()

    return redirect(url_for('conta'))


@app.route('/matching')
def matching():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    user_id = session.get('user_id')
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT subject_id FROM user_subjects WHERE user_id = %s AND role = 'mentee'", (user_id,))
        mentee_subjects = [row['subject_id'] for row in cursor.fetchall()]

        if not mentee_subjects:
            flash("Define as disciplinas em que queres ser mentorado no teu perfil.", "info")
            return render_template('matching.html', mentors=[])

        format_strings = ','.join(['%s'] * len(mentee_subjects))
        cursor.execute(f"""
            SELECT u.id AS mentor_id, u.name, u.username, cu.name AS subject_name,
                   IFNULL(us.profile_pic, 'static/uploads/ProfilePics/default.jpg') AS profile_pic,
                   IFNULL(us.bio, '') AS bio
            FROM user_subjects s
            JOIN users u ON u.id = s.user_id
            JOIN user_settings us ON us.user_id = u.id
            JOIN curricular_units cu ON cu.id = s.subject_id
            WHERE s.subject_id IN ({format_strings}) AND s.role = 'mentor' AND u.id != %s
            ORDER BY u.name
        """, (*mentee_subjects, user_id))
        mentors = cursor.fetchall()
        return render_template('matching.html', mentors=mentors)

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
        return redirect(url_for('dashboard'))
    finally:
        cursor.close()


@app.route('/contacto', methods=['POST'])
def contacto():
    try:
        nome = bleach.clean(request.form['nome'])
        email = bleach.clean(request.form['email'])
        mensagem = bleach.clean(request.form['mensagem'])

        cursor = db.cursor()
        cursor.execute("INSERT INTO contacto (nome, email, mensagem) VALUES (%s, %s, %s)",
                       (nome, email, mensagem))
        db.commit()
        cursor.close()

        flash("Mensagem enviada com sucesso! Obrigado por nos contactar.", "success")

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
    except Exception as e:
        flash(f"Erro geral: {e}", "error")

    return redirect(url_for('html_redirect', page='index') + "#connect")


@app.route('/get_units_by_course', methods=['POST'])
def get_units_by_course():
    course = request.json.get('course')
    if not course:
        return {'units': []}

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT cu.id, cu.name
        FROM courses c
        JOIN course_curricular_units ccu ON c.id = ccu.course_id
        JOIN curricular_units cu ON cu.id = ccu.curricular_unit_id
        WHERE c.name = %s ORDER BY cu.name
    """, (course,))
    units = cursor.fetchall()
    cursor.close()
    return {'units': units}




@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Not authenticated'}, 401

    data = request.json
    conversation_id = data.get('conversation_id')
    message = data.get('message')

    if not conversation_id or not message:
        return {'status': 'error', 'message': 'Missing fields'}, 400

    encrypted_message = fernet.encrypt(message.encode())

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_id, encrypted_message)
            VALUES (%s, %s, %s)
        """, (conversation_id, session['user_id'], encrypted_message))
        db.commit()
        cursor.close()
        return {'status': 'success'}

    except mysql.connector.Error as err:
        return {'status': 'error', 'message': str(err)}, 500


@app.route('/get_messages/<int:conversation_id>', methods=['GET'])
def get_messages(conversation_id):
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Not authenticated'}, 401

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.id, m.sender_id, u.username, m.timestamp, m.encrypted_message
        FROM messages m
        JOIN users u ON u.id = m.sender_id
        WHERE m.conversation_id = %s
        ORDER BY m.timestamp ASC
    """, (conversation_id,))
    raw_messages = cursor.fetchall()
    cursor.close()

    decrypted = [
        {
            'id': m['id'],
            'sender_id': m['sender_id'],
            'sender': m['username'],
            'timestamp': m['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'message': fernet.decrypt(m['encrypted_message'].encode()).decode()
        }
        for m in raw_messages
    ]

    return {'messages': decrypted}



@app.route('/conversa/<int:conversation_id>')
def conversa(conversation_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
    SELECT u.id AS mentor_id, u.name, u.username,
           IFNULL(us.profile_pic, 'static/uploads/ProfilePics/default.jpg') AS profile_pic,
           c.id AS conversation_id,
           (
             SELECT cu.name
             FROM user_subjects s
             JOIN curricular_units cu ON cu.id = s.subject_id
             WHERE s.user_id = u.id
             LIMIT 1
           ) AS subject
    FROM conversations c
    JOIN conversation_members cm1 ON cm1.conversation_id = c.id
    JOIN conversation_members cm2 ON cm2.conversation_id = c.id AND cm2.user_id != %s
    JOIN users u ON u.id = cm2.user_id
    LEFT JOIN user_settings us ON us.user_id = u.id
    WHERE cm1.user_id = %s
    GROUP BY u.id, c.id
""", (user_id, user_id))

    mentors = cursor.fetchall()
    cursor.close()

    
    # Fetch mentor info for the selected conversation
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.name, cu.name AS subject, 
               IFNULL(us.profile_pic, 'static/uploads/ProfilePics/default.jpg') AS profile_pic
        FROM conversation_members cm
        JOIN users u ON u.id = cm.user_id
        JOIN user_settings us ON us.user_id = u.id
        JOIN user_subjects s ON s.user_id = u.id
        JOIN curricular_units cu ON cu.id = s.subject_id
        WHERE cm.conversation_id = %s AND u.id != %s
        LIMIT 1
    """, (conversation_id, user_id))
    mentor_info = cursor.fetchone()
    cursor.close()

    return render_template('conversa.html',
                           conversation_id=conversation_id,
                           user_id=user_id,
                           mentors=mentors,
                           mentor_info=mentor_info)






@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Not authenticated'}, 401

    data = request.get_json()
    user_id = session['user_id']
    mentor_id = data.get('mentor_id')

    if not mentor_id:
        return {'status': 'error', 'message': 'Missing mentor_id'}, 400

    try:
        mentor_id = int(mentor_id)
    except ValueError:
        return {'status': 'error', 'message': 'Invalid mentor_id'}, 400

    try:
        cursor = db.cursor()

        # Check if a conversation already exists between both users
        cursor.execute("""
            SELECT c.id
            FROM conversations c
            JOIN conversation_members cm1 ON cm1.conversation_id = c.id
            JOIN conversation_members cm2 ON cm2.conversation_id = c.id
            WHERE cm1.user_id = %s AND cm2.user_id = %s
            LIMIT 1
        """, (user_id, mentor_id))
        existing = cursor.fetchone()

        if existing:
            conversation_id = existing[0]
        else:
            # Create new conversation
            cursor.execute("INSERT INTO conversations () VALUES ()")
            conversation_id = cursor.lastrowid
            cursor.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)", (conversation_id, user_id))
            cursor.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)", (conversation_id, mentor_id))
            db.commit()

        cursor.close()
        return {'status': 'success', 'conversation_id': conversation_id}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
# --- RUN ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
