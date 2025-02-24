
import mysql.connector
from argon2 import PasswordHasher, exceptions
from getpass import getpass  


ph = PasswordHasher()


db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'database': 'studylink'
}

def verify_user_password(username, input_password):
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

       
        print("🔍 Fetching user from database...")
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            stored_hash = result['password']
            print(f"✅ User found. Hash from DB: {stored_hash}")

            # Verify the provided password against the stored hash
            try:
                if ph.verify(stored_hash, input_password):
                    print("🎉 Password is correct.")
                    return True
            except exceptions.VerifyMismatchError:
                print("❌ Incorrect password.")
            except exceptions.VerificationError as e:
                print(f"⚠️ Verification failed: {str(e)}")
        else:
            print("❌ Username not found in the database.")

    except mysql.connector.Error as err:
        print(f"❗ Database error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 Database connection closed.")

    return False


if __name__ == "__main__":
    username_input = input("Enter username: ")
    password_input = getpass("Enter password securely: ")  
    verify_user_password(username_input, password_input)
