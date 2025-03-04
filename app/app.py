
from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector
from argon2 import PasswordHasher, exceptions as argon2_exceptions

app = Flask(__name__)

app.secret_key = 'your_very_secret_key'


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

    # If not in page_map, serve the HTML file normally
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
        name = request.form['name']
        username = request.form['username'].lower()  # Normalize username
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash("As passwords não coincidem.", "error")
            return redirect(url_for('registo_page'))  

        # Hash the password using Argon2
        hashed_password = ph.hash(password)

        cursor = db.cursor()
        query = "INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)"
        values = (name, username, email, hashed_password)
        cursor.execute(query, values)
        db.commit()
        cursor.close()

        flash("Registo bem-sucedido! Agora pode fazer login.", "success")
        return redirect(url_for('login_page'))  # Redirect to login page with success message

    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry error
            flash("Erro: Nome de utilizador já existe!", "error")
        else:
            flash(f"Erro na base de dados: {err}", "error")
        return redirect(url_for('registo_page'))

    except Exception as e:
        flash(f"Erro geral: {e}", "error")
        return redirect(url_for('registo_page'))


@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        username = username.lower()  # Normalize username
        
        cursor = db.cursor(dictionary=True)
        query = "SELECT username, password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()

        # Check if user exists and verify password
        if user and ph.verify(user['password'], password):
            session['username'] = user['username']
            flash("Login bem-sucedido! Estamos a iniciar a sua sessão...", "success") 
            return redirect(url_for('login_page'))  # This will trigger the animation

        flash("Nome de utilizador ou password inválidos.", "error")
        return render_template('login.html')

    except argon2_exceptions.VerifyMismatchError:
        flash("Nome de utilizador ou password inválidos.", "error")
        return render_template('login.html')

    except mysql.connector.Error as err:
        flash(f"Erro na base de dados: {err}", "error")
        return render_template('login.html')

    except Exception as e:
        flash(f"Erro geral: {e}", "error")
        return render_template('login.html')

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
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        cursor = db.cursor(dictionary=True)

        # Buscar o utilizador
        query = "SELECT password, email FROM users WHERE username = %s"
        cursor.execute(query, (session['username'],))
        user = cursor.fetchone()

        if not user:
            flash("Erro: Utilizador não encontrado.", "error")
            return redirect(url_for('conta'))

        # Verificar se a password atual está correta
        if not ph.verify(user['password'], password):
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

    except argon2_exceptions.VerifyMismatchError:
        flash("Password atual incorreta.", "error")
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
        nome = request.form['nome']
        email = request.form['email']
        mensagem = request.form['mensagem']

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

    
    
