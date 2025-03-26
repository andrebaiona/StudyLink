from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import mysql.connector
from argon2 import PasswordHasher, exceptions as argon2_exceptions
from werkzeug.utils import secure_filename
import bleach
import re
import secrets
import os

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

UPLOAD_FOLDER = 'static/uploads/ProfilePics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

csrf = CSRFProtect(app)
app.secret_key = secrets.token_hex(32)
csrf.init_app(app)
app.config['SESSION_COOKIE_HTTPONLY'] = True  
app.config['SESSION_PERMANENT'] = True        
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session expires in 1 hour
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per minute"])

def sanitize_input(data):
    return bleach.clean(data, strip=True)


# MySQL database connection

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

# Initialize Argon2 password hasher
ph = PasswordHasher()

@app.route('/<page>.html')
def html_redirect(page):
    page_map = {
        'login': 'login_page',
        'registo': 'registo_page',
        'conta': 'conta',
    }
    if page in page_map:
        return redirect(url_for(page_map[page]), code=301)

    try:
        return render_template(f"{page}.html")
    except TemplateNotFound:
        flash("Página não encontrada!", "error")
        return redirect(url_for('login_page'))

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

        
        session['form_data'] = {
            'name': name,
            'username': username,
            'email': email
        }

        if password != confirm_password:
            flash("As passwords não coincidem.", "error")
            return redirect(url_for('registo_page'))

        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash("Nome de utilizador ou email já estão registados!", "error")
            return redirect(url_for('registo_page'))

        
        hashed_password = ph.hash(password)

    
        cursor = db.cursor()
        query = "INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, username, email, hashed_password))
        user_id = cursor.lastrowid

        # Create default user settings
        cursor.execute(
            "INSERT INTO user_settings (user_id, profile_pic, bio, class_year, course) VALUES (%s, %s, %s, %s, %s)",
            (user_id, 'static/uploads/ProfilePics/default.jpg', None, None, None)
        )

        db.commit()
        cursor.close()

        # Limpar os dados da sessão após sucesso
        session.pop('form_data', None)

        flash("Registo bem-sucedido!", "success")
        return redirect(url_for('registo_page'))

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
        return redirect(url_for('registo_page'))

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

        # Normalize input to lowercase for consistent matching
        identifier = identifier.lower()
        cursor = db.cursor(dictionary=True)

        
        if "@" in identifier:
            query = "SELECT id, username, password FROM users WHERE email = %s"
        else:
            query = "SELECT id, username, password FROM users WHERE username = %s"

        cursor.execute(query, (identifier,))
        user = cursor.fetchone()
        cursor.close()

        if user and ph.verify(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            # Store login success in session to trigger animation
            session['login_success'] = True  

            flash("🎓Credenciais Aceites! A fazer login...", "success")  
            return redirect(url_for('login_page'))  # Stay on the login page to show animation

        else:
            flash("Nome de utilizador ou password inválidos.", "error")
            return redirect(url_for('login_page', identifier=identifier))

    except argon2_exceptions.VerifyMismatchError:
        flash("Nome de utilizador ou password inválidos.", "error")
        return redirect(url_for('login_page', identifier=identifier))

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
        return redirect(url_for('login_page', identifier=identifier))

    except Exception as e:
        flash(f"Erro geral: {e}", "error")
        return redirect(url_for('login_page', identifier=identifier))



@app.route('/conta')
def conta():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    user_id = session.get('user_id')
    if not user_id:
        flash("Erro de autenticação. Faça login novamente.", "error")
        return redirect(url_for('login_page'))

    cursor = db.cursor(dictionary=True)
    try:
        query = """
            SELECT u.name, u.email, u.username, IFNULL(us.profile_pic, 'static/uploads/ProfilePics/default.jpg') AS profile_pic, 
                   IFNULL(us.bio, '') AS bio, IFNULL(us.class_year, '') AS class_year, IFNULL(us.course, '') AS course
            FROM users u
            LEFT JOIN user_settings us ON u.id = us.user_id
            WHERE u.id = %s
        """
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        if user:
            return render_template('conta.html', user=user)
        else:
            flash("Erro ao carregar dados do utilizador.", "error")
            return redirect(url_for('login_page'))

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
    username = session['username']  # Get username from session
    name = sanitize_input(request.form.get('name', ''))
    bio = sanitize_input(request.form.get('bio', ''))
    class_year = request.form.get('class_year', '')
    course = request.form.get('course', '')

    # Handle profile picture upload
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()  # Get file extension
            filename = f"{username}.{ext}"  # Rename file to username.ext
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Remove old profile picture if exists (except default)
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT profile_pic FROM user_settings WHERE user_id = %s", (user_id,))
            old_profile_pic = cursor.fetchone()

            if old_profile_pic and old_profile_pic['profile_pic'] != 'static/uploads/ProfilePics/default.jpg':
                old_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], old_profile_pic['profile_pic'])
                if os.path.exists(old_pic_path):
                    os.remove(old_pic_path)  # Delete the old profile picture

            file.save(file_path)  # Save new profile picture

            # Convert path for database storage
            relative_file_path = f"static/uploads/ProfilePics/{filename}"

            # Update database with new profile picture path
            cursor.execute("UPDATE user_settings SET profile_pic = %s WHERE user_id = %s", (relative_file_path, user_id))
            db.commit()
            cursor.close()

    try:
        cursor = db.cursor(dictionary=True)
        query = """
            UPDATE users u
            JOIN user_settings us ON u.id = us.user_id
            SET u.name = %s, us.bio = %s, us.class_year = %s, us.course = %s
            WHERE u.id = %s
        """
        cursor.execute(query, (name, bio, class_year, course, user_id))
        db.commit()
        cursor.close()

        flash("Conta atualizada com sucesso!", "success")

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")

    return redirect(url_for('conta'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/registo_page')
def registo_page():
    return render_template('registo.html')

@app.route('/contacto', methods=['POST'])
def contacto():
    try:
        nome = bleach.clean(request.form['nome'])
        email = bleach.clean(request.form['email'])
        mensagem = bleach.clean(request.form['mensagem'])

        cursor = db.cursor()
        query = "INSERT INTO contacto (nome, email, mensagem) VALUES (%s, %s, %s)"
        cursor.execute(query, (nome, email, mensagem))
        db.commit()
        cursor.close()

        flash("Mensagem enviada com sucesso! Obrigado por nos contactar.", "success")
        return redirect(url_for('html_redirect', page='contacto'))

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
        return redirect(url_for('html_redirect', page='contacto'))

    except Exception as e:
        flash(f"Erro geral: {e}", "error")
        return redirect(url_for('html_redirect', page='contacto'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    app.run(debug=True)

