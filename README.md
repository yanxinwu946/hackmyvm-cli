# HackMyVM CLI Toolkit

A powerful Python command-line interface for interacting with the [HackMyVM](https://hackmyvm.eu) platform. This tool enables cybersecurity practitioners to efficiently search, download, and manage virtual machines with persistent authentication and comprehensive filtering capabilities.

<img width="1429" height="846" alt="image" src="https://github.com/user-attachments/assets/b9933337-b3fc-4a91-a103-8276d6fa1b3d" />
<img width="1583" height="758" alt="image" src="https://github.com/user-attachments/assets/04b4c37e-cdbc-4357-aacf-b7877eb2d9cb" />
<img width="1227" height="1262" alt="image" src="https://github.com/user-attachments/assets/e2eef2fd-6dda-412b-9f06-45d27684e3f4" />

## ✨ Features

- **🔍 Advanced Machine Search**
  - Multiple filter options: difficulty, category, tags, and machine names
  - Color-coded difficulty levels for quick identification
  - Pagination support for large result sets
  - Real-time search with partial name matching

- **🎯 Difficulty Level Filtering** with visual indicators:
  - 🟢 **Easy** → Green highlighting
  - 🟡 **Medium** → Yellow highlighting
  - 🔴 **Hard** → Red highlighting

- **📂 Category & Tag Filtering**
  - Categories: `windows`, `linux`, `size`, `hacked`, `all`
  - 25+ specialized tags: `web`, `docker`, `suid`, `sqli`, `cve`, etc.

- **⚡ Efficient Operations**
  - Flag submission for completed challenges
  - Direct machine downloads as ZIP files
  - Writeup search functionality
  - Achievement statistics tracking
  - Export all machines as JSON/CSV
  - Persistent session management

- **🔐 Secure Authentication**
  - Local credential storage
  - Automatic session persistence
  - No repeated login requirements

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Active HackMyVM account

### Installation

```bash
pipx install git+https://github.com/Yanxinwu946/hackmyvm-cli
# or
uv tool install git+https://github.com/Yanxinwu946/hackmyvm-cli
```

### Direct Execution

If you prefer not to install the package, you can run it directly from source:

```bash
git clone https://github.com/Yanxinwu946/hackmyvm-cli
cd hackmyvm-cli
python -m hmv
```

### Initial Configuration
Configure your HackMyVM credentials (required for first use):
```bash
hmv config
```
*This creates `~/.hmv/config.json` with your credentials stored locally.*

### Start Exploring
```bash
hmv search
```

## 📖 Usage Guide

### 🔧 Configuration
Configure your HackMyVM credentials (first-time setup):
```bash
hmv config
```

### 🔍 Machine Search & Discovery

#### Basic Operations
```bash
# List all available machines (first page)
hmv search

# Search by machine name (partial matching)
hmv search -n todd
hmv search -n aria

# Filter by difficulty level
hmv search -l easy
hmv search -l medium
hmv search -l hard
```

#### Advanced Filtering
```bash
# Filter by specialized tags
hmv search -t web
hmv search -t docker
hmv search -t sqli

# Combine filters
hmv search -t web -f hard

# Browse by categories
hmv search -l windows
hmv search -l linux
```

**Best Practices**:
- Combine `-t` and `-f` for precise filtering.
- Use `-p` for basic searches or with `-f` for navigation through large result sets.

**Available Tags**:
`bruteforce` • `suid` • `wordpress` • `cron` • `smb` • `docker` • `sudo` • `web` • `fileupload` • `pathhijacking` • `stego` • `binary` • `capabilities` • `cve` • `commandinjection` • `portknocking` • `ssti` • `libraryhijack` • `sqli` • `lfi` • `rce` • `logpoisoning` • `nfs` • `xxe`

### 📝 Writeup Discovery
Search for community writeups and walkthroughs:
```bash
hmv writeup Todd
hmv writeup "machine name"
```

### 🚩 Flag Submission
Submit flags for completed challenges:
```bash
hmv flag -i "flag{your_captured_flag}" -vm MachineName
```

**Note**: Ensure the flag format is correct to avoid submission errors.

### ⬇️ Machine Downloads
Download virtual machines for local setup:
```bash
hmv download Soul
hmv download TryHarder
```

### 📊 Achievement Statistics
Track and analyze overall statistics:
```bash
# View achievement statistics
hmv stats

# Update data from server
hmv stats -u

# Filter by specific VM or user
hmv stats -vm Todd
hmv stats -user Sublarge
```

### 📦 Export All Machines
Export comprehensive machine data for analysis or backup:
```bash
# Export as JSON (default)
hmv export
hmv export -o machines.json

# Export as CSV
hmv export -f csv
hmv export -f csv -o my_machines.csv
```

**Exported Data Includes**:
- Machine ID, name, and difficulty level
- Platform information (Linux/Windows)
- Author details and file size
- Machine status (Active/Retired)
- Direct URLs for images, downloads, and machine pages

### 📚 Help & Documentation
```bash
hmv -h                  # Main help
hmv search --help       # Search options
hmv flag --help         # Flag submission help
hmv stats --help        # Statistics options
hmv export --help       # Export options
hmv download --help     # Download help
hmv writeup --help      # Writeup search help
```

## ⚙️ Configuration & Files

### Configuration Files
- **`~/.hmv/config.json`** - Stores your HackMyVM credentials
- **`~/.hmv/session.pkl`** - Maintains active session data
- **`~/.hmv/writeups.csv`** - Cached writeup database (auto-updated)
- **`~/.hmv/achievements.csv`** - Achievement statistics data

### Pagination Behavior
- **Basic search** (`hmv search`): Returns paginated results (use `-p` for navigation)
- **Filtered searches** (`-l`, `-n`, `-t`): Return all matching results (pagination not applicable)
- **Client-side filtering** (`-f`): Works with pagination for refined browsing

### Security Notes
- Credentials are stored locally in JSON format
- Session data persists until manual credential update
- **Never share configuration files** containing your credentials

## 🔄 Updating & Maintenance

### Updating the Tool
To update to the latest version:

#### With pipx
```bash
pipx upgrade hmv-cli
# or force reinstall
pipx install --force git+https://github.com/Yanxinwu946/hackmyvm-cli
```

#### With uv
```bash
uv tool upgrade hmv-cli
# or force reinstall
uv tool install --force git+https://github.com/Yanxinwu946/hackmyvm-cli
```

### Uninstallation
```bash
# Uninstall the tool
pipx uninstall hmv-cli      # If installed with pipx
uv tool uninstall hmv-cli   # If installed with uv

# Clear configuration and cache
rm -rf ~/.hmv/
```

## ❓ FAQ

**Q: How do I reset my configuration?**  
A: Run `hmv config` again to update your credentials.

**Q: Can I use this tool offline?**  
A: No, it requires an internet connection to fetch data from HackMyVM.

**Q: What if I forget my password?**  
A: Reset it on the [HackMyVM website](https://hackmyvm.eu).

**Q: Is my data secure?**  
A: Credentials are stored locally. Never share your `~/.hmv/config.json` file.

**Q: How do I export all machines for analysis?**  
A: Use `hmv export -f csv` to get a CSV file or `hmv export` for JSON format.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

Thanks to the [HackMyVM](https://hackmyvm.eu) community for providing an excellent platform for cybersecurity practice and learning.
