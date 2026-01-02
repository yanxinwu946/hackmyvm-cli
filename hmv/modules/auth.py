import os
import json
import pickle
import sys
import requests
from datetime import datetime
from .utils import bcolors

class AuthManager:
    def __init__(self):
        self.HMV_DIR = os.path.expanduser("~/.hmv")
        self.CONFIG_FILE = os.path.join(self.HMV_DIR, "config.json")
        self.SESSION_FILE = os.path.join(self.HMV_DIR, "session.pkl")
        self.login_url = "https://hackmyvm.eu/login/auth.php"
        self.machines_url = "https://hackmyvm.eu/machines/"
        
        self._ensure_hmv_directory()

    def _ensure_hmv_directory(self):
        if not os.path.exists(self.HMV_DIR):
            os.makedirs(self.HMV_DIR)
            print(f"[*] Created configuration directory: {self.HMV_DIR}")

    def _load_config(self):
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except json.JSONDecodeError:
            print("[!] Error reading config file. Please re-run 'config'.")
        return None

    def _save_config(self, username, password):
        config = {"username": username, "password": password}
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("[+] Configuration saved successfully.")
        except Exception as e:
            print(f"[!] Error saving config: {e}")
            sys.exit(1)

    def _save_session(self, session):
        try:
            with open(self.SESSION_FILE, 'wb') as f:
                pickle.dump({"session": session, "timestamp": datetime.now()}, f)
            print("[+] Session saved.")
        except Exception as e:
            print(f"[!] Error saving session: {e}")

    def _load_session(self):
        try:
            if os.path.exists(self.SESSION_FILE):
                with open(self.SESSION_FILE, 'rb') as f:
                    data = pickle.load(f)
                return data["session"]
        except Exception as e:
            print(f"[!] Error loading session: {e}")
        return None
        
    def configure_credentials(self):
        print(f"{bcolors.BOLD}[*] Configuring HackMyVM credentials...{bcolors.ENDC}")
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        if not username or not password:
            print("[!] Username and password cannot be empty.")
            sys.exit(1)
        self._save_config(username, password)
        if os.path.exists(self.SESSION_FILE):
            os.remove(self.SESSION_FILE)
            print("[+] Cleared previous session.")

    def get_authenticated_session(self):
        config = self._load_config()
        if not config:
            print("[!] No configuration found. Please run 'config' command first.")
            sys.exit(1)
        
        session = self._load_session()
        if session:
            try:
                response = session.get(self.machines_url, timeout=10)
                if "Logout" in response.text:
                    print("[+] Using saved session.")
                    return session
            except requests.RequestException:
                print("[!] Saved session invalid, re-authenticating...")

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        data = {"admin": config["username"], "password_usuario": config["password"]}
        try:
            response = session.post(self.login_url, data, allow_redirects=True, timeout=10)
            response.raise_for_status()
            if "Logout" in response.text:
                print("[+] Login successful.")
                self._save_session(session)
                return session
            print("[!] Login failed: Invalid credentials.")
        except requests.RequestException as e:
            print(f"[!] Login error: {e}")
        
        sys.exit(1)
