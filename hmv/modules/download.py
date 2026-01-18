import sys
import requests
from .utils import bcolors

class DownloadModule:
    def __init__(self, session=None):
        pass

    def download(self, machine_name):
        filename = f"{machine_name.lower()}.zip"
        url = f"https://downloads.hackmyvm.eu/{filename}"

        try:
            print(f"{bcolors.BOLD}[*] Starting download of {filename}...{bcolors.ENDC}")
            response = requests.get(url, stream=True, timeout=10, allow_redirects=False)
            
            if response.status_code in (301, 302):
                redirect_url = response.headers.get('Location')
                print(f"{bcolors.WARNING}[!] Redirect ({response.status_code}) to: {redirect_url}{bcolors.ENDC}")
                return
            
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded_size = 0

            with open(filename, "wb") as f:
                for chunk in response.iter_content(block_size):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress = downloaded_size / total_size if total_size else 0
                    sys.stdout.write(f"\r{bcolors.OKGREEN}[+]{bcolors.ENDC} Progress: [{int(progress * 20) * '#'}{(20 - int(progress * 20)) * '-'}] {progress:.1%}")
                    sys.stdout.flush()
            print("\n")
            print(f"{bcolors.OKGREEN}[✓]{bcolors.ENDC} {machine_name} downloaded successfully.")
        except requests.exceptions.HTTPError:
            print(f"\n{bcolors.FAIL}[!]{bcolors.ENDC} Machine '{machine_name}' not found.")
        except requests.RequestException as e:
            print(f"\n{bcolors.FAIL}[!]{bcolors.ENDC} Download error: {e}")
