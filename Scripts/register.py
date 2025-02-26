
import requests
import urllib.parse
import getpass

def register():
    url = "http://127.0.0.1/register"
    
    print("Enter your registration details:")
    name = input("Full Name: ")
    username = input("Username: ")
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")
    
    if password != confirm_password:
        print("Error: Passwords do not match!")
        return
    
    data = {
        "name": name,
        "username": username,
        "email": email,
        "password": password,
        "confirm-password": confirm_password
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://127.0.0.1",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Referer": "http://127.0.0.1/registo.html",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i"
    }
    
    try:
        response = requests.post(url, headers=headers, data=urllib.parse.urlencode(data))
        if response.status_code == 200:
            print("Registration successful!")
        else:
            print(f"Failed to register. Status Code: {response.status_code}\nResponse: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    register()
