import requests
from .utils import bcolors

class FlagModule:
    def __init__(self, session):
        self.session = session

    def submit(self, flag, vm):
        url = "https://hackmyvm.eu/machines/checkflag.php"
        data = {"flag": flag, "vm": vm}

        try:
            response = self.session.post(url, data, timeout=10)
            response.raise_for_status()

            if "wrong" in response.text.lower():
                print("[!] The flag is incorrect.")
            elif "correct" in response.text.lower():
                print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC} The flag is CORRECT!")
            else:
                print("[!] Unknown response from server.")
        except requests.RequestException as e:
            print(f"[!] Error submitting flag: {e}")
