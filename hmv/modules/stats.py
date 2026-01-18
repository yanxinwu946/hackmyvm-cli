import os
import csv
import sys
import requests
from datetime import datetime
from prettytable import PrettyTable
from .utils import bcolors, color_level, print_bold_header

# Constants
HMV_DIR = os.path.expanduser("~/.hmv")
ACHIEVEMENT_FILE = os.path.join(HMV_DIR, "achievements.csv")
CONSECUTIVE_FAILURES_LIMIT = 50

class AchievementModule:
    def __init__(self, session=None):
        self.session = session
        self.csv_file = ACHIEVEMENT_FILE
        self._ensure_directory()

    def _ensure_directory(self):
        if not os.path.exists(HMV_DIR):
            os.makedirs(HMV_DIR)

    def _get_last_id_from_csv(self):
        """Finds the last achievement ID in the local CSV file."""
        if not os.path.exists(self.csv_file):
            return 0
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                # Read all lines and find the last one
                lines = f.readlines()
                if len(lines) < 2: # Header + at least one row
                    return 0

                last_line = lines[-1].strip()
                if not last_line:
                    return 0

                reader = csv.reader([lines[0], last_line])
                header = next(reader)
                last_record = next(reader)

                if 'id' in header:
                    id_index = header.index('id')
                    return int(last_record[id_index])
        except (IOError, ValueError, IndexError):
            pass
        return 0

    def _save_to_csv(self, records):
        if not records: return
        file_exists = os.path.exists(self.csv_file) and os.path.getsize(self.csv_file) > 0

        # Dynamically determine fieldnames from the first record
        fieldnames = list(records[0].keys())

        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(records)
        except IOError as e:
            print(f"[!] Error saving to CSV: {e}")

    def download_data(self):
        database_url = 'https://raw.githubusercontent.com/Yanxinwu946/hmv-stats-scraper/main/data/achievements.csv'
        try:
            print(f"[*] Downloading achievement database from {database_url}...")
            response = requests.get(database_url, timeout=10)
            response.raise_for_status()

            with open(self.csv_file, 'wb') as f:
                f.write(response.content)

            print(f"[✓] Database downloaded successfully to {self.csv_file}")
            return True
        except Exception as e:
            print(f"[!] Error downloading database: {e}")
            return False

    def load_data(self):
        if not os.path.exists(self.csv_file):
            return None
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except Exception:
            return None

    def display_stats(self, update_data=False, start_id=None, vm_filter=None, user_filter=None):
        if update_data:
            success = self.download_data()
            if success:
                print(f"[*] Database updated successfully.")
            else:
                print(f"[!] Failed to update database.")
                return
        else:
            if not os.path.exists(self.csv_file):
                print("[!] No achievement data found.")
                create_data = input(f"[*] Do you want to download data now? (y/N): ").lower() == 'y'
                if create_data:
                    self.display_stats(update_data=True, start_id=start_id, vm_filter=vm_filter, user_filter=user_filter)
                return

        records = self.load_data()
        if not records:
            print("[!] Failed to retrieve achievement data.")
            return

        if vm_filter:
            records = [r for r in records if r.get('vm_title', '').lower() == vm_filter.lower()]
            if not records:
                print(f"[!] No records found for VM: '{vm_filter}'")
                return

        if user_filter:
            records = [r for r in records if r.get('nickname', '').lower() == user_filter.lower()]
            if not records:
                print(f"[!] No records found for user: '{user_filter}'")
                return

        print_bold_header("Achievement Statistics")
        print(f"[*] Data Location: {self.csv_file}")

        total = len(records)
        difficulty_stats = {}
        rank_stats = {'author': 0, 'first': 0, 'top3': 0}

        if total > 0:
            for record in records:
                difficulty = record.get('difficulty', 'unknown').lower()
                rank = record.get('rank', '')

                difficulty_stats[difficulty] = difficulty_stats.get(difficulty, 0) + 1

                if rank.isdigit():
                    rank_num = int(rank)
                    if rank_num == 1: rank_stats['author'] += 1
                    elif rank_num == 2: rank_stats['first'] += 1
                    elif 3 <= rank_num <= 4: rank_stats['top3'] += 1

        print(f"[*] Total records: {bcolors.BOLD}{total}{bcolors.ENDC}")

        print_bold_header("Difficulty Breakdown:")
        if difficulty_stats:
            for diff, count in sorted(difficulty_stats.items()):
                print(f"  {color_level(diff)}: {count}")
        else:
            print("  No difficulty data found.")

        if not vm_filter:
            print_bold_header("Rank Statistics:")
            print(f"  Author (Rank 1): {bcolors.OKGREEN}{rank_stats['author']}{bcolors.ENDC}")
            print(f"  First (Rank 2):  {bcolors.FAIL}{rank_stats['first']}{bcolors.ENDC}")
            print(f"  Top 3 (Ranks 3-4): {bcolors.WARNING}{rank_stats['top3']}{bcolors.ENDC}")

        # Determine if to show all records or recent
        show_all = False
        if vm_filter or user_filter:
            show_all = input("\n[*] Do you want to see all records? (y/N): ").lower() == 'y'

        self._display_records(records, vm_filter, user_filter, show_all)

    def _display_records(self, records, vm_filter, user_filter, show_all=False):
        table = PrettyTable(['Nickname', 'Date', 'VM Title', 'Difficulty', 'Rank', 'ID'])
        table.align = "l"

        if show_all:
            display_records = list(reversed(records))
            header = "All Achievements:"
        else:
            recent_records = records[-10:] if len(records) > 10 else records
            display_records = list(reversed(recent_records))
            header = "Recent Achievements:"

        print_bold_header(header)

        for record in display_records:
            rank_colored = record.get('rank', 'N/A')
            if rank_colored.isdigit():
                rank_num = int(rank_colored)
                if rank_num == 1: rank_colored = f"{bcolors.OKGREEN}#{rank_num}{bcolors.ENDC}"
                elif rank_num == 2: rank_colored = f"{bcolors.FAIL}#{rank_num}{bcolors.ENDC}"
                elif 3 <= rank_num <= 4: rank_colored = f"{bcolors.WARNING}#{rank_num}{bcolors.ENDC}"
                else: rank_colored = f"#{rank_num}"

            table.add_row([
                record.get('nickname', 'N/A'),
                record.get('date', 'N/A'),
                record.get('vm_title', 'N/A'),
                color_level(record.get('difficulty', 'N/A')),
                rank_colored,
                record.get('id', 'N/A')
            ])
        print(table)
