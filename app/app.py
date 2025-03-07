from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import mysql.connector
from argon2 import PasswordHasher, exceptions as argon2_exceptions
import bleach
import re
import secrets

app = Flask(__name__)

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
    database="studylink"
)

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
        username = bleach.clean(request.form.get('username'))
        password = bleach.clean(request.form.get('password'))

        if not username or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('login_page', username=username))

        username = username.lower()
        cursor = db.cursor(dictionary=True)
        query = "SELECT username, password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and ph.verify(user['password'], password):
            session['username'] = user['username']
            flash("🎓Credenciais Aceites! A fazer login...", "success")  
            return redirect(url_for('login_page'))  

        else:
            flash("Nome de utilizador ou password inválidos.", "error")
            return redirect(url_for('login_page', username=username))

    except argon2_exceptions.VerifyMismatchError:
        flash("Nome de utilizador ou password inválidos.", "error")
        return redirect(url_for('login_page', username=username))

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
        return redirect(url_for('login_page', username=username))

    except Exception as e:
        flash(f"Erro geral: {e}", "error")
        return redirect(url_for('login_page', username=username))

@app.route('/conta')
def conta():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    cursor = db.cursor(dictionary=True)
    query = "SELECT name, email FROM users WHERE username = %s"
    cursor.execute(query, (session['username'],))
    user = cursor.fetchone()
    cursor.close()

    if user:
        session['name'] = user['name']
        session['email'] = user['email']
        return render_template('conta.html')
    else:
        flash("Erro ao carregar dados do utilizador.", "error")
        return redirect(url_for('login_page'))

@app.route('/update_account', methods=['POST'])
def update_account():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    try:
        name = sanitize_input(request.form.get('name', ''))
        email = sanitize_input(request.form.get('email', ''))
        new_password = sanitize_input(request.form.get('new_password', ''))
        confirm_password = sanitize_input(request.form.get('confirm_password', ''))

        cursor = db.cursor(dictionary=True)

       
        query = "SELECT password, email FROM users WHERE username = %s"
        cursor.execute(query, (session['username'],))
        user = cursor.fetchone()

        if not user:
            flash("Erro: Utilizador não encontrado.", "error")
            return redirect(url_for('conta'))

        # Verificar se a password atual está correta
        
        if not ph.verify(user['password'], request.form.get('current_password')):
            flash("Erro: Password atual incorreta.", "error")
            return redirect(url_for('conta'))

       
        
        email = user['email']

        # Atualizar Password
        if new_password and confirm_password:
            if new_password == confirm_password:
                hashed_password = ph.hash(new_password)
                query = "UPDATE users SET name=%s, email=%s, password=%s WHERE username=%s"
                values = (name, email, hashed_password, session['username'])
            else:
                flash("As passwords não coincidem.", "error")
                return redirect(url_for('conta'))
        else:
            query = "UPDATE users SET name=%s, email=%s WHERE username=%s"
            values = (name, email, session['username'])

        cursor.execute(query, values)
        db.commit()
        cursor.close()

        session['name'] = name
        session['email'] = email

        flash("Conta atualizada com sucesso!", "success")
        return redirect(url_for('conta'))

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
        return redirect(url_for('conta'))

    except argon2_exceptions.VerifyMismatchError as err:
        flash(f"Password atual incorreta: ", "error")
        return redirect(url_for('conta'))

    except Exception as e:
        flash(f"Erro geral: {e}", "error")
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

    
    
