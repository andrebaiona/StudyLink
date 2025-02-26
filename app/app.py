
from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
from argon2 import PasswordHasher, exceptions as argon2_exceptions

app = Flask(__name__)

#app.secret_key = 'your_very_secret_key'


# MySQL database connection
db = mysql.connector.connect(
    host="studylink_mysql_db",  
    user="root",
    password="root",
    database="studylink"
)

# Initialize Argon2 password hasher
ph = PasswordHasher()

@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        username = username.lower()
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



@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        username = username.lower()
        cursor = db.cursor(dictionary=True)
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and ph.verify(user['password'], password):
            return f'Logged in as "{username}"', 200

        return "Invalid username or password", 401

    except argon2_exceptions.VerifyMismatchError:
        return "Invalid username or password", 401

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return f"MySQL Error: {err}", 500

    except Exception as e:
        print(f"General Error: {e}")
        return f"General Error: {e}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

