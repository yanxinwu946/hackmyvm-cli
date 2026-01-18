import os
import csv
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from prettytable import PrettyTable
from .utils import bcolors, print_bold_header

# Constants
WRITEUP_FILE = os.path.join(os.path.expanduser("~/.hmv"), "writeups.csv")
WRITEUP_CACHE_TIMEOUT = timedelta(hours=24)

class WriteupModule:
    def __init__(self, session):
        self.session = session
        self.writeup_file = WRITEUP_FILE

    def _needs_update(self):
        if not os.path.exists(self.writeup_file):
            return True
        try:
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(self.writeup_file))
            return datetime.now() - file_mod_time > WRITEUP_CACHE_TIMEOUT
        except Exception:
            return True

    def _fetch_and_update(self):
        writeup_url = "https://hackmyvm.eu/hmv/writeupz.php"
        try:
            print("[*] Fetching writeup data from server...")
            response = self.session.get(writeup_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            writeups = []
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) < 4: continue

                try:
                    machine_link = cells[0].find('a')
                    writeup_link = cells[3].find('a')
                    if not machine_link or not writeup_link: continue

                    writeups.append({
                        'vmname': machine_link.get_text(strip=True),
                        'author': cells[1].get_text(strip=True),
                        'language': cells[2].get_text(strip=True),
                        'writeup': urljoin("https://hackmyvm.eu", writeup_link.get('href', ''))
                    })
                except (AttributeError, IndexError):
                    continue

            if not writeups:
                print("[!] No writeup data found.")
                return False

            fieldnames = ['vmname', 'author', 'language', 'writeup']
            with open(self.writeup_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(writeups)

            print(f"[+] Writeup data updated successfully. ({len(writeups)} records)")
            return True
        except requests.RequestException as e:
            print(f"[!] Error fetching writeup data: {e}")
        return False

    def _load_data(self):
        if self._needs_update():
            if not self._fetch_and_update() and not os.path.exists(self.writeup_file):
                print("[!] No writeup data available.")
                return []

        data = []
        try:
            with open(self.writeup_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
        except Exception as e:
            print(f"[!] Error reading writeup data: {e}")
        return data

    def search(self, machine_name):
        writeups = self._load_data()
        if not writeups: return

        matching_writeups = [w for w in writeups if machine_name.lower() in w.get('vmname', '').lower()]

        if not matching_writeups:
            print(f"[!] No writeups found for machine: '{machine_name}'")
            return

        writeup_table = PrettyTable(["Machine", "Author", "Language", "Writeup Link"])
        writeup_table.align = "l"

        for writeup in matching_writeups:
            language = writeup.get('language', 'N/A')
            lang_lower = (language or '').lower()
            color_map = {
                'english': bcolors.OKGREEN,
                'spanish': bcolors.WARNING,
                'chinese': bcolors.FAIL,
            }
            color = color_map.get(lang_lower)
            if color:
                language = f"{color}{language}{bcolors.ENDC}"

            writeup_table.add_row([
                writeup.get('vmname', 'N/A'),
                writeup.get('author', 'N/A'),
                language,
                writeup.get('writeup', 'N/A')
            ])

        print_bold_header(f"Found {len(matching_writeups)} writeup(s) for '{machine_name}':")
        print(writeup_table)
