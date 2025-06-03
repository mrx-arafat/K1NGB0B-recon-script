# K1NGB0B Recon Script

A simple and efficient domain reconnaissance tool designed for bug bounty hunters and security researchers.

## Installation

Run the automated installer to set up all dependencies:

```bash
chmod +x install.sh && ./install.sh
```

The installer will automatically handle:
- System package installation (Python, Go, curl, wget, git)
- Python dependencies (aiohttp)
- Go reconnaissance tools (assetfinder, subfinder, httpx, anew)
- PATH configuration

## Usage

1. **Run the script:**
   ```bash
   python3 k1ngb0b_recon.py
   ```

2. **Enter target domain when prompted:**
   ```
   Enter target domain: example.com
   ```

3. **Wait for results** - The tool will automatically:
   - Find subdomains using multiple sources
   - Check which subdomains are live
   - Save organized results to a folder

## Features

- **Multi-source subdomain enumeration** using assetfinder, subfinder, and Certificate Transparency
- **Live subdomain detection** with httpx probing
- **Asynchronous processing** for improved speed
- **Automatic result organization** in timestamped folders
- **JSON report generation** for easy parsing
- **Dependency verification** ensures all tools are available before running
- **Linux-optimized** with support for major distributions

## Output Structure

```
target_domain_results/
├── all_subdomains.txt      # All discovered subdomains
├── live_subdomains.txt     # Live/responsive subdomains
└── recon_report.json       # Detailed JSON report
```

## Requirements

**Automatically installed by the setup script:**

- Python 3.8 or higher
- Go 1.19 or higher
- assetfinder (subdomain discovery)
- subfinder (subdomain discovery)
- httpx (HTTP probing)
- anew (result deduplication)
- aiohttp (Python HTTP library)

## Supported Systems

- Ubuntu/Debian (apt)
- CentOS/RHEL (yum)
- Fedora (dnf)
- Arch Linux (pacman)

## Example Session

```
$ python3 k1ngb0b_recon.py

K1NGB0B Recon Script v2.0
Author: mrx-arafat

Checking dependencies...
All dependencies found!

Enter target domain: tesla.com
Target domain: tesla.com

Starting reconnaissance for: tesla.com
Running assetfinder...
   Found 15 subdomains
Running subfinder...
   Found 23 subdomains
Checking Certificate Transparency...
   Found 12 subdomains
Checking live subdomains...
   Found 8 live subdomains

Results: 31 unique subdomains, 8 live
Results saved to: tesla_com_results/
Reconnaissance completed successfully!
```

## Troubleshooting

**If tools are not found in PATH:**
```bash
source ~/.bashrc
# or restart your terminal
```

**Manual dependency installation:**
```bash
# Install Go tools manually
go install github.com/tomnomnom/assetfinder@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/tomnomnom/anew@latest

# Install Python dependencies
pip3 install --user aiohttp
```

## Author

**mrx-arafat** (K1NGB0B)
