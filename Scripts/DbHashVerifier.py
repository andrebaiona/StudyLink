
import mysql.connector
from argon2 import PasswordHasher, exceptions
from getpass import getpass  

# Define ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"

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

        print(f"{YELLOW}🕵 Fetching user from database...{RESET}")
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            stored_hash = result['password']
            print(f"{BLUE}🔎 -  User '{BOLD}{username}{RESET}{BLUE}' found ✔️{RESET}")
            print(f"{BOLD}🔐 Hash from DB: {RESET}{stored_hash}")

            # Verify the provided password against the stored hash
            try:
                if ph.verify(stored_hash, input_password):
                    print(f"{GREEN}✅ - Correct Password.{RESET}")
                    return True
            except exceptions.VerifyMismatchError:
                print(f"{RED}❌ - Incorrect password.{RESET}")
            except exceptions.VerificationError as e:
                print(f"{RED}⚠️  - Verification failed: {str(e)}{RESET}")
        else:
            print(f"{RED}❌ Username not found in the database.{RESET}")

    except mysql.connector.Error as err:
        print(f"{RED}❗ Database error: {err}{RESET}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print(f"{YELLOW}🔒 - Database connection closed.{RESET}")

    return False


if __name__ == "__main__":
    username_input = input("Enter username: ").lower()
    password_input = getpass("Enter password : ")  
    verify_user_password(username_input, password_input)
