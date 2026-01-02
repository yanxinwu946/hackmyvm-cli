import sys
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

class bcolors:
    OKGREEN = Fore.GREEN
    WARNING = Fore.YELLOW
    FAIL = Fore.RED
    ENDC = Style.RESET_ALL
    BOLD = Style.BRIGHT

def color_level(level):
    """Returns a colored string based on the machine level."""
    level_lower = level.lower()
    if level_lower == "easy":
        return f"{bcolors.OKGREEN}{level}{bcolors.ENDC}"
    if level_lower == "medium":
        return f"{bcolors.WARNING}{level}{bcolors.ENDC}"
    if level_lower == "hard":
        return f"{bcolors.FAIL}{level}{bcolors.ENDC}"
    return level

def print_bold_header(text):
    """Prints a bold header with consistent formatting."""
    print(f"\n{bcolors.BOLD}{text}{bcolors.ENDC}")

def format_choices(choices, per_line=6):
    """Formats a list of choices for display in help messages."""
    lines = [', '.join(choices[i:i + per_line]) for i in range(0, len(choices), per_line)]
    return '\n    '.join(lines)

def find_matching_command(partial_command, available_commands):
    """Finds a matching command based on a prefix."""
    if not partial_command: return None
    matches = [cmd for cmd in available_commands if cmd.startswith(partial_command)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"[!] Ambiguous command '{partial_command}'. Possible matches: {', '.join(matches)}")
        return None
    print(f"[!] Unknown command '{partial_command}'. Available commands: {', '.join(available_commands)}")
    return None