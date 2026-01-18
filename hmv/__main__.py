#!/usr/bin/env python3

import argparse
import sys
import os

def display_banner():
    """Display HMV-CLI banner"""
    banner = """
██╗  ██╗███╗   ███╗██╗   ██╗      ██████╗██╗     ██╗
██║  ██║████╗ ████║██║   ██║     ██╔════╝██║     ██║
███████║██╔████╔██║██║   ██║     ██║     ██║     ██║
██╔══██║██║╚██╔╝██║╚██╗ ██╔╝     ██║     ██║     ██║
██║  ██║██║ ╚═╝ ██║ ╚████╔╝      ╚██████╗███████╗██║
╚═╝  ╚═╝╚═╝     ╚═╝  ╚═══╝        ╚═════╝╚══════╝╚═╝
    """
    print(banner)
    print("HackMyVM CLI Toolkit")
    print("by Sublarge - https://github.com/Yanxinwu946")
    print()

# Add the project directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .modules.auth import AuthManager
from .modules.utils import format_choices, find_matching_command
from .modules.search import SearchModule
from .modules.writeup import WriteupModule
from .modules.download import DownloadModule
from .modules.flag import FlagModule
from .modules.stats import AchievementModule
from .modules.export import ExportModule

# Constantshttps://hackmyvm.eu/img/vm/slack.png
COMMANDS = ['config', 'search', 'writeup', 'download', 'flag', 'stats', 'export']
SEARCH_CHOICES = ['easy', 'medium', 'hard', 'windows', 'linux', 'size', 'hacked', 'all']
TAG_CHOICES = ['bruteforce', 'suid', 'wordpress', 'cron', 'smb', 'docker', 'sudo', 'web',
               'fileupload', 'pathhijacking', 'stego', 'binary', 'capabilities', 'cve',
               'commandinjection', 'portknocking', 'ssti', 'libraryhijack', 'sqli', 'lfi',
               'rce', 'logpoisoning', 'nfs', 'xxe']
ACHIEVEMENT_FILE = os.path.join(os.path.expanduser("~/.hmv"), "achievements.csv")

# ===================== CLI Entry Point =====================
def main():
    # Display banner
    display_banner()
    
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        input_command = sys.argv[1]
        matched_command = find_matching_command(input_command, COMMANDS)
        if matched_command:
            sys.argv[1] = matched_command
            if matched_command != input_command:
                print(f"[*] Using command '{matched_command}' (matched from '{input_command}')")

    parser = argparse.ArgumentParser(
        description="",
        prog="hmv"
    )
    
    subparsers = parser.add_subparsers(dest='command', help="Available commands")

    subparsers.add_parser("config", help="Configure HackMyVM credentials")

    search_choices = SEARCH_CHOICES
    tag_choices = TAG_CHOICES
    parser_search = subparsers.add_parser("search", help="Search or list machines")
    parser_search.add_argument("-l", "--level", choices=search_choices, help="Filter by level")
    parser_search.add_argument("-t", "--tag", choices=tag_choices, help="Filter by tag")
    parser_search.add_argument("-n", "--name", help="Search by machine name (partial match)")
    parser_search.add_argument("-f", "--filter-level", choices=['easy', 'medium', 'hard'], help="Client-side filter by difficulty level")
    parser_search.add_argument("-p", "--page", type=int, default=1, help="Page number for results (default: 1)")

    parser_writeup = subparsers.add_parser("writeup", help="Search writeups for a specific machine")
    parser_writeup.add_argument("machine_name", help="Name of the machine to search writeups for")

    parser_download = subparsers.add_parser("download", help="Download a machine ZIP file")
    parser_download.add_argument("machine_name", help="Name of the machine to download")

    parser_flag = subparsers.add_parser("flag", help="Submit a flag for a machine")
    parser_flag.add_argument("-i", "--input", required=True, help="Flag to submit")
    parser_flag.add_argument("-vm", "--vm", required=True, help="Machine name for flag submission")

    parser_stats = subparsers.add_parser("stats", help="Show achievement statistics")
    parser_stats.add_argument("-u", "--update", action='store_true', help="Update data before showing stats")
    parser_stats.add_argument("-s", "--start-id", type=int, help="Start crawling from a specific ID (overrides cache)")
    parser_stats.add_argument("-vm", "--vm", help="Filter statistics by a specific VM name")
    parser_stats.add_argument("-user", "--user", help="Filter statistics by a specific user nickname")
    parser_export = subparsers.add_parser("export", help="Export all machines as JSON or CSV")
    parser_export.add_argument("-o", "--output", help="Output file path (default: machines.json)")
    parser_export.add_argument("-f", "--format", choices=['json', 'csv'], default='json', help="Export format (default: json)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    auth_manager = AuthManager()

    if args.command == 'config':
        auth_manager.configure_credentials()
        return

    if args.command == 'export':
        session = auth_manager.get_authenticated_session()
        export_format = args.format if hasattr(args, 'format') and args.format else "json"
        if hasattr(args, 'output') and args.output:
            output_file = args.output
        else:
            output_file = "machines.csv" if export_format == "csv" else "machines.json"
        ExportModule(session).export_all_machines(output_file=output_file, format=export_format)
        return

    if args.command == 'writeup':
        writeup_module = WriteupModule(None)
        if writeup_module._needs_update():
            session = auth_manager.get_authenticated_session()
            writeup_module = WriteupModule(session)
        writeup_module.search(args.machine_name)
        return
    elif args.command == 'stats':
        data_exists = os.path.exists(ACHIEVEMENT_FILE)
        needs_update = args.update or not data_exists
        stats_module = AchievementModule(None)
        stats_module.display_stats(update_data=needs_update, start_id=args.start_id, vm_filter=args.vm, user_filter=args.user)
        return
    elif args.command == 'download':
        DownloadModule(None).download(args.machine_name)
        return
    else:
        session = auth_manager.get_authenticated_session()
        if args.command == 'search':
            SearchModule(session).list_machines(
                level=args.level, search=args.name, tag=args.tag,
                filter_level=args.filter_level, page=args.page
            )
        elif args.command == 'flag':
            FlagModule(session).submit(args.input, args.vm)

if __name__ == '__main__':
    main()
