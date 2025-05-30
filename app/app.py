from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit, join_room
from jinja2 import TemplateNotFound
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()

from argon2 import PasswordHasher, exceptions as argon2_exceptions
import bleach
import secrets
import os
import base64

import mysql.connector
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from flask_socketio import SocketIO, emit, join_room

from flask import send_file
import io

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
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
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
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/index.html")
def index_html_redirect():
    return redirect(url_for("home"), code=301)

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

        
        hashed_password = ph.hash(password)
        from cryptography.hazmat.primitives.asymmetric import rsa

# Generate RSA key pair
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
        public_key = private_key.public_key()

# Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

# Save user with keys
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO users (name, username, email, password)
            VALUES (%s, %s, %s, %s)
        """, (name, username, email, hashed_password))
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO user_keys (user_id, public_key, private_key)
            VALUES (%s, %s, %s)
        """, (user_id, public_pem.decode(), private_pem.decode()))
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


@app.route('/generate_keys', methods=['POST'])
def generate_user_keys():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    cursor = db.cursor()
    cursor.execute("""
    INSERT INTO user_keys (user_id, public_key, private_key)
    VALUES (%s, %s, %s)
""", (user_id, public_pem.decode(), private_pem.decode()))
    db.commit()
    cursor.close()

    flash("Chaves regeneradas com sucesso!", "success")
    return redirect(url_for('conta'))


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
    plain_message = data.get('message')

    if not conversation_id or not plain_message:
        return {'status': 'error', 'message': 'Missing fields'}, 400

    try:
        sender_id = session['user_id']
        cursor = db.cursor(dictionary=True)

        # Get recipient ID
        cursor.execute("""
            SELECT user_id FROM conversation_members
            WHERE conversation_id = %s AND user_id != %s
            LIMIT 1
        """, (conversation_id, sender_id))
        recipient = cursor.fetchone()
        if not recipient:
            return {'status': 'error', 'message': 'Recipient not found'}, 404
        recipient_id = recipient['user_id']

        # Get sender's public key
        cursor.execute("""
            SELECT public_key FROM user_keys
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY created_at DESC LIMIT 1
        """, (sender_id,))
        sender_row = cursor.fetchone()
        sender_public_key = serialization.load_pem_public_key(sender_row['public_key'].encode())

        # Get recipient's public key
        cursor.execute("""
            SELECT public_key FROM user_keys
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY created_at DESC LIMIT 1
        """, (recipient_id,))
        recipient_row = cursor.fetchone()
        recipient_public_key = serialization.load_pem_public_key(recipient_row['public_key'].encode())

        # Encrypt message with Fernet
        fernet_key = Fernet.generate_key()
        fernet = Fernet(fernet_key)
        encrypted_message = fernet.encrypt(plain_message.encode())
        encrypted_message_b64 = base64.b64encode(encrypted_message).decode()

        # Encrypt Fernet key for both sender and recipient
        encrypted_fernet_key_sender = sender_public_key.encrypt(
            fernet_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypted_fernet_key_recipient = recipient_public_key.encrypt(
            fernet_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypted_key_sender_b64 = base64.b64encode(encrypted_fernet_key_sender).decode()
        encrypted_key_recipient_b64 = base64.b64encode(encrypted_fernet_key_recipient).decode()

        # Save to database
        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_id, encrypted_message, encrypted_file_key_sender, encrypted_file_key_recipient)
            VALUES (%s, %s, %s, %s, %s)
        """, (conversation_id, sender_id, encrypted_message_b64, encrypted_key_sender_b64, encrypted_key_recipient_b64))
        db.commit()

        # Emit event
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        socketio.emit('new_message', {
            'conversation_id': conversation_id,
            'sender_id': sender_id,
            'message': plain_message,
            'timestamp': timestamp
        }, room=f'conversation_{conversation_id}')

        cursor.close()
        return {'status': 'success'}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500




@app.route('/get_messages/<int:conversation_id>', methods=['GET'])
def get_messages(conversation_id):
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Not authenticated'}, 401

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)

    try:
        # === Step 1: Get user's private key ===
        cursor.execute("""
            SELECT private_key FROM user_keys
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        if not row or not row.get('private_key'):
            return {'status': 'error', 'message': 'No private key found'}, 400

        private_key_pem = row['private_key'].encode()
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)

        # === Step 2: Fetch messages, include both encrypted key fields ===
        
        cursor.execute("""
            SELECT m.id, m.sender_id, u.username, m.timestamp, m.encrypted_message, 
                   m.encrypted_file_key_sender, m.encrypted_file_key_recipient,
                   m.file_name, m.file_data, m.file_mime
            FROM messages m
            JOIN users u ON u.id = m.sender_id
            WHERE m.conversation_id = %s
            ORDER BY m.timestamp ASC
        """, (conversation_id,))
        raw_messages = cursor.fetchall()
        cursor.close()


        decrypted_messages = []

        for m in raw_messages:
            try:
                encrypted_key_b64 = m['encrypted_file_key_sender'] if m['sender_id'] == user_id else m['encrypted_file_key_recipient']
                encrypted_key = base64.b64decode(encrypted_key_b64)
                fernet_key = private_key.decrypt(
                    encrypted_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                fernet = Fernet(fernet_key)

                if m['encrypted_message'] == '[Encrypted file]' and m.get('file_data'):
                    decrypted_file = fernet.decrypt(m['file_data'])
                    file_base64 = base64.b64encode(decrypted_file).decode()

                    decrypted_messages.append({
                        'id': m['id'],
                        'sender_id': m['sender_id'],
                        'sender': m['username'],
                        'timestamp': m['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        'message': None,
                        'is_file': True,
                        'file_name': m['file_name'],
                        'file_mime': m['file_mime'],
                        'file_data': file_base64
                    })
                else:
                    decrypted_text = fernet.decrypt(base64.b64decode(m['encrypted_message'])).decode()
                    decrypted_messages.append({
                        'id': m['id'],
                        'sender_id': m['sender_id'],
                        'sender': m['username'],
                        'timestamp': m['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                        'message': decrypted_text,
                        'is_file': False
                    })

            except Exception:
                decrypted_messages.append({
                    'id': m['id'],
                    'sender_id': m['sender_id'],
                    'sender': m['username'],
                    'timestamp': m['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'message': '[Erro ao decifrar a mensagem]',
                    'is_file': m['encrypted_message'] == '[Encrypted file]'
                })



        return {'messages': decrypted_messages}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/get_user_conversations', methods=['GET'])
def get_user_conversations():
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Not authenticated'}, 401

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.id AS conversation_id, u.id AS other_user_id, u.username, u.name,
                   IFNULL(us.profile_pic, 'static/uploads/ProfilePics/default.jpg') AS profile_pic
            FROM conversations c
            JOIN conversation_members cm1 ON cm1.conversation_id = c.id
            JOIN conversation_members cm2 ON cm2.conversation_id = c.id AND cm2.user_id != %s
            JOIN users u ON u.id = cm2.user_id
            LEFT JOIN user_settings us ON us.user_id = u.id
            WHERE cm1.user_id = %s
        """, (user_id, user_id))
        conversations = cursor.fetchall()
        cursor.close()

        return {'status': 'success', 'conversations': conversations}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


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
    first_message = data.get('first_message', '').strip()

    if not mentor_id:
        return {'status': 'error', 'message': 'Missing mentor_id'}, 400

    try:
        mentor_id = int(mentor_id)
    except ValueError:
        return {'status': 'error', 'message': 'Invalid mentor_id'}, 400

    try:
        cursor = db.cursor(dictionary=True)

        # Check if conversation already exists
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
            conversation_id = existing['id']
        else:
            # Create new conversation
            cursor.execute("INSERT INTO conversations () VALUES ()")
            conversation_id = cursor.lastrowid
            cursor.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)", (conversation_id, user_id))
            cursor.execute("INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)", (conversation_id, mentor_id))
            db.commit()

        # OPTIONAL: Insert first message if provided
        if first_message:
            # Get both public keys
            cursor.execute("""
                SELECT public_key FROM user_keys WHERE user_id = %s AND is_active = TRUE ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
            sender_row = cursor.fetchone()
            sender_public_key = serialization.load_pem_public_key(sender_row['public_key'].encode())

            cursor.execute("""
                SELECT public_key FROM user_keys WHERE user_id = %s AND is_active = TRUE ORDER BY created_at DESC LIMIT 1
            """, (mentor_id,))
            recipient_row = cursor.fetchone()
            recipient_public_key = serialization.load_pem_public_key(recipient_row['public_key'].encode())

            # Encrypt with Fernet
            fernet_key = Fernet.generate_key()
            fernet = Fernet(fernet_key)
            encrypted_message = fernet.encrypt(first_message.encode())
            encrypted_message_b64 = base64.b64encode(encrypted_message).decode()

            # Encrypt Fernet key for both
            encrypted_fernet_key_sender = sender_public_key.encrypt(
                fernet_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_fernet_key_recipient = recipient_public_key.encrypt(
                fernet_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_key_sender_b64 = base64.b64encode(encrypted_fernet_key_sender).decode()
            encrypted_key_recipient_b64 = base64.b64encode(encrypted_fernet_key_recipient).decode()

            cursor.execute("""
                INSERT INTO messages (conversation_id, sender_id, encrypted_message, encrypted_file_key_sender, encrypted_file_key_recipient)
                VALUES (%s, %s, %s, %s, %s)
            """, (conversation_id, user_id, encrypted_message_b64, encrypted_key_sender_b64, encrypted_key_recipient_b64))
            db.commit()

        cursor.close()
        return {'status': 'success', 'conversation_id': conversation_id}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500



@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Not authenticated'}, 401

    conversation_id = request.form.get('conversation_id')
    file = request.files.get('file')

    if not file or not conversation_id:
        return {'status': 'error', 'message': 'Missing file or conversation ID'}, 400

    sender_id = session['user_id']
    cursor = db.cursor(dictionary=True)

    try:
        # Get recipient ID
        cursor.execute("""
            SELECT user_id FROM conversation_members
            WHERE conversation_id = %s AND user_id != %s
            LIMIT 1
        """, (conversation_id, sender_id))
        recipient = cursor.fetchone()
        if not recipient:
            return {'status': 'error', 'message': 'Recipient not found'}, 404
        recipient_id = recipient['user_id']

        # Get sender & recipient public keys
        cursor.execute("SELECT public_key FROM user_keys WHERE user_id = %s AND is_active = TRUE ORDER BY created_at DESC LIMIT 1", (sender_id,))
        sender_key = cursor.fetchone()
        cursor.execute("SELECT public_key FROM user_keys WHERE user_id = %s AND is_active = TRUE ORDER BY created_at DESC LIMIT 1", (recipient_id,))
        recipient_key = cursor.fetchone()

        sender_pub = serialization.load_pem_public_key(sender_key['public_key'].encode())
        recipient_pub = serialization.load_pem_public_key(recipient_key['public_key'].encode())

        # Generate Fernet key for the file
        fernet_key = Fernet.generate_key()
        fernet = Fernet(fernet_key)

        # Encrypt file data
        file_data = file.read()
        encrypted_file = fernet.encrypt(file_data)

        # Encrypt Fernet key for both users
        encrypted_key_sender = base64.b64encode(
            sender_pub.encrypt(
                fernet_key,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
        ).decode()
        encrypted_key_recipient = base64.b64encode(
            recipient_pub.encrypt(
                fernet_key,
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
        ).decode()

        # Store file in DB with [Encrypted file] marker
        cursor.execute("""
            INSERT INTO messages (
                conversation_id, sender_id, encrypted_message,
                encrypted_file_key_sender, encrypted_file_key_recipient,
                file_name, file_data, file_mime
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            conversation_id, sender_id, '[Encrypted file]',
            encrypted_key_sender, encrypted_key_recipient,
            file.filename, encrypted_file, file.mimetype
        ))
        db.commit()
        return {'status': 'success'}

    except Exception as e:
        db.rollback()
        return {'status': 'error', 'message': str(e)}, 500

    finally:
        cursor.close()

@app.route('/download_file/<int:message_id>', methods=['GET'])
def download_file(message_id):
    if 'user_id' not in session:
        return {'status': 'error', 'message': 'Not authenticated'}, 401

    user_id = session['user_id']
    cursor = db.cursor(dictionary=True)

    try:
        # Get user's private key
        cursor.execute("""
            SELECT private_key FROM user_keys
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        if not row or not row.get('private_key'):
            return {'status': 'error', 'message': 'No private key found'}, 400

        private_key_pem = row['private_key'].encode()
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)

        # Get message details
        cursor.execute("""
            SELECT sender_id, file_path, encrypted_file_key_sender, encrypted_file_key_recipient
            FROM messages
            WHERE id = %s
        """, (message_id,))
        msg = cursor.fetchone()
        cursor.close()

        if not msg or not msg['file_path']:
            return {'status': 'error', 'message': 'File not found'}, 404

        # Decide which encrypted key to use
        if msg['sender_id'] == user_id:
            encrypted_key_b64 = msg['encrypted_file_key_sender']
        else:
            encrypted_key_b64 = msg['encrypted_file_key_recipient']

        encrypted_key = base64.b64decode(encrypted_key_b64)
        fernet_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        fernet = Fernet(fernet_key)

        # Load and decrypt file
        with open(msg['file_path'], 'rb') as f:
            encrypted_file_data = f.read()
        decrypted_file_data = fernet.decrypt(encrypted_file_data)

        # Prepare file for sending
        filename = os.path.basename(msg['file_path'])
        return send_file(
            io.BytesIO(decrypted_file_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

# --- RUN ---



socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

@socketio.on('join')
def handle_join(data):
    join_room(f"conversation_{data['conversation_id']}")

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return public_pem.decode(), private_pem.decode()
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

