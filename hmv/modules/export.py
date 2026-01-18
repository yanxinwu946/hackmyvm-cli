import json
import sys
import requests
from bs4 import BeautifulSoup
import re
import csv


class ExportModule:
    def __init__(self, session):
        self.session = session
        self.machines_url = "https://hackmyvm.eu/machines/?l=all"
        self.color_map = {'#28a745': 'easy', '#ffc107': 'medium', '#dc3545': 'hard'}

    def _extract_difficulty_from_style(self, style_str):
        """Extract difficulty from style attribute"""
        if not style_str:
            return 'unknown'
        
        color_match = re.search(r'border-top:\s*\d+px\s+solid\s+([#\w]+)', style_str)
        if color_match:
            color = color_match.group(1)
            return self.color_map.get(color.lower(), 'unknown')
        return 'unknown'

    def _extract_platform_from_imgs(self, td_elem):
        """Extract platform from image title"""
        if not td_elem:
            return '?'
        
        imgs = td_elem.find_all('img')
        if len(imgs) >= 2:
            platform_title = imgs[1].get('title', '?')
            if 'Linux' in platform_title:
                return 'Linux'
            elif 'Windows' in platform_title:
                return 'Windows'
            return platform_title
        return '?'

    def export_all_machines(self, output_file="machines.json", format="json"):
        """Export all machines from ?l=all page to JSON or CSV format"""
        try:
            print(f"[*] Fetching machines from {self.machines_url}...")

            all_machines = []

            try:
                response = self.session.get(self.machines_url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                rows = soup.find_all('tr')
                
                for row in rows:
                    try:
                        first_td = row.find('td')
                        if not first_td:
                            continue
                        
                        vmname_h4 = first_td.find('h4', class_='vmname')
                        if not vmname_h4:
                            continue
                        
                        name_link = vmname_h4.find('a')
                        if not name_link:
                            continue
                        
                        name = name_link.get_text(strip=True)
                        
                        difficulty_div = first_td.find('div', style=lambda s: s and 'border-top' in s)
                        if difficulty_div:
                            difficulty = self._extract_difficulty_from_style(difficulty_div.get('style', ''))
                        else:
                            difficulty = 'unknown'
                        
                        platform = self._extract_platform_from_imgs(first_td)
                        
                        status_span = first_td.find('span', class_='badge')
                        status = status_span.get_text(strip=True) if status_span else "?"
                        
                        tds = row.find_all('td')
                        author = "?"
                        size = "?"
                        
                        if len(tds) > 1:
                            creator_link = tds[1].find('a', class_='creator')
                            if creator_link:
                                author = creator_link.get_text(strip=True)
                        
                        if len(tds) > 2:
                            size_p = tds[2].find('p', class_='size')
                            if size_p:
                                size = size_p.get_text(strip=True)
                        
                        machine_name_lower = name.lower().replace(' ', '_')
                        image_url = f"https://hackmyvm.eu/img/vm/{machine_name_lower}.png"
                        machine_url = f"https://hackmyvm.eu/machines/machine.php?vm={name}"
                        download_url = f"https://downloads.hackmyvm.eu/{machine_name_lower}.zip"
                        
                        machine_data = {
                            "image": image_url,
                            "machine_url": machine_url,
                            "download_url": download_url,
                            "name": name,
                            "difficulty": difficulty,
                            "author": author,
                            "platform": platform,
                            "size": size,
                            "status": status
                        }
                        
                        all_machines.append(machine_data)
                    except (AttributeError, IndexError, KeyError) as e:
                        continue

            except requests.RequestException as e:
                print(f"\n[!] Error fetching machines: {e}")
                sys.exit(1)

            if not all_machines:
                print("[!] No machines found on the page.")
                return

            print(f"\n[+] Successfully exported {len(all_machines)} machines.")

            total = len(all_machines)
            for idx, machine in enumerate(all_machines):
                machine_copy = {"id": total - idx}
                machine_copy.update(machine)
                all_machines[idx] = machine_copy

            if format.lower() == "csv":
                self._export_to_csv(all_machines, output_file)
            else:
                self._export_to_json(all_machines, output_file)

        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            sys.exit(1)

    def _export_to_json(self, machines, output_file):
        """Export machines to JSON"""
        export_data = {
            "total_machines": len(machines),
            "machines": machines
        }

        json_output = json.dumps(export_data, indent=2, ensure_ascii=False)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"[+] Data exported to {output_file}")
        except IOError as e:
            print(f"[!] Error writing to file {output_file}: {e}")
            sys.exit(1)

    def _export_to_csv(self, machines, output_file):
        """Export machines to CSV"""
        try:
            fieldnames = ['id', 'image', 'machine_url', 'download_url', 'name', 'difficulty', 'author', 'platform', 'size', 'status']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(machines)
            
            print(f"[+] Data exported to {output_file}")
        except IOError as e:
            print(f"[!] Error writing to file {output_file}: {e}")
            sys.exit(1)
