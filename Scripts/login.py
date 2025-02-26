import requests
import urllib.parse
import getpass

# Define ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"

def login():
    url = "http://127.0.0.1/login"
    
    print(f"{BOLD}{YELLOW}🔐 Login Portal{RESET}")
    username = input(f"{BOLD}👤 Username: {RESET}")
    password = getpass.getpass(f"{BOLD}🔑 Password: {RESET}")
    
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
        print(f"{YELLOW}🔄 Attempting to log in...{RESET}")
        response = requests.post(url, headers=headers, data=urllib.parse.urlencode(data))
        
        if response.status_code == 200:
            print(f"{GREEN}✅ Login successful!{RESET}")
        else:
            print(f"{RED}❌ Failed to login. Status Code: {response.status_code}{RESET}")
            print(f"{RED}📜 Response: {response.text}{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}⚠️ Error: {e}{RESET}")

if __name__ == "__main__":
    login()

