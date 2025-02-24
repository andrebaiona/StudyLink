
from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
from argon2 import PasswordHasher, exceptions as argon2_exceptions

app = Flask(__name__)

# MySQL database connection
db = mysql.connector.connect(
    host="studylink_mysql_db",  # Match the service name from docker-compose
    user="root",
    password="root",
    database="studylink"
)

# Initialize Argon2 password hasher


@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password using Argon2
        hashed_password = ph.hash(password)

        cursor = db.cursor()
        query = "INSERT INTO users (name, username, email, password) VALUES (%s, %s, %s, %s)"
        values = (name, username, email, hashed_password)
        cursor.execute(query, values)
        db.commit()
        cursor.close()

        return "Registration successful!", 200

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return f"MySQL Error: {err}", 500

    except Exception as e:
        print(f"General Error: {e}")
        return f"General Error: {e}", 500




ph = PasswordHasher()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            hashed_password = user['password']
            try:
                if ph.verify(hashed_password, password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return "Login successful!", 200
                else:
                    return "Invalid username or password.", 401
            except argon2_exceptions.VerifyMismatchError:
                return "Invalid username or password.", 401
        else:
            return "User not found.", 404

    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
