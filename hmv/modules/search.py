import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from prettytable import PrettyTable
from .utils import bcolors, color_level

class SearchModule:
    def __init__(self, session):
        self.session = session
        self.machines_url = "https://hackmyvm.eu/machines/"
        self.color_map = {'#28a745': 'easy', '#ffc107': 'medium', '#dc3545': 'hard'}

    def _get_total_pages(self, search=None, tag=None):
        try:
            params = {}
            if search: params['v'] = search
            if tag: params['t'] = tag

            response = self.session.get(self.machines_url, params=params, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            page_element = soup.select_one("nav ul li:nth-last-child(2) a")
            if not page_element or not page_element.text or '»' in page_element.text:
                page_element = soup.select_one("nav ul li:nth-last-child(3) a")
            if page_element and '/' in page_element.text:
                return int(page_element.text.split('/')[1])
        except (requests.RequestException, ValueError, IndexError):
            pass
        return 1

    def list_machines(self, level=None, search=None, tag=None, filter_level=None, page=1):
        params = {'p': page}
        if level:
            params['l'] = level
            page_range = 1
        else:
            page_range = self._get_total_pages(search=search, tag=tag)
            if search: params['v'] = search
            if tag: params['t'] = tag

        if page < 1 or page > page_range:
            print(f"[!] Invalid page number. Must be between 1 and {page_range}.")
            sys.exit(1)

        try:
            response = self.session.get(self.machines_url, params=params, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.select("table.mt-1.table.table-striped.table-dark tbody tr")

            machines_tab = PrettyTable(["Name", "Level", "Status", "Creator", "Link"])
            machines_tab.align = "l"

            found_machines = []
            for row in rows:
                try:
                    name = row.find('h4', class_='vmname').get_text(strip=True)
                    color_style = row.find('div', style=lambda s: s and 'border-top' in s)['style']
                    color = color_style.split('solid')[-1].strip().rstrip(';')
                    level_found = self.color_map.get(color.lower(), 'unknown')

                    if filter_level and level_found.lower() != filter_level.lower():
                        continue

                    status_tag = row.find('span', class_='badge')
                    status_text = status_tag.get_text(strip=True) if status_tag else "?"
                    creator = row.find_all('td')[1].get_text(strip=True)

                    link_elem = row.find('a', href=lambda href: href and "machine.php" in href)
                    link = urljoin("https://hackmyvm.eu/machines/", link_elem['href']) if link_elem else 'N/A'

                    level_colored = color_level(level_found)
                    status_colored = f"{bcolors.WARNING}{status_text}{bcolors.ENDC}" if "TO HACK" in status_text else f"{bcolors.OKGREEN}{status_text}{bcolors.ENDC}"

                    found_machines.append([name, level_colored, status_colored, creator, link])
                except (AttributeError, IndexError, KeyError):
                    continue

            if not found_machines:
                print("[!] No machines found matching the criteria.")
                return

            for machine in found_machines:
                machines_tab.add_row(machine)

            print(machines_tab)

            if not level and page_range > 1:
                print(f"\n[*] Page {page} of {page_range}")

        except requests.RequestException as e:
            print(f"[!] Error fetching machines: {e}")
            sys.exit(1)
