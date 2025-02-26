
import requests
import urllib.parse
import getpass

def login():
    url = "http://127.0.0.1/login"
    
    print("Enter your login details:")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    
    data = {
        "username": username,
        "password": password
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
        "Referer": "http://127.0.0.1/login.html",
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
            print("Login successful!")
        else:
            print(f"Failed to login. Status Code: {response.status_code}\nResponse: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    login()
