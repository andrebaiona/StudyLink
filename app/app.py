from flask import Flask, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

# MySQL database connection
db = mysql.connector.connect(
    host="studylink_mysql_db",  # Match the service name from docker-compose
    user="root",
    password="root",
    database="studylink"
)

@app.route('/register', methods=['POST'])
def register():
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)"
        values = (first_name, last_name, email, password)
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
  # Redirect back to the form

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

