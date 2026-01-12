# K1NGB0B Recon Suite v3.0.0

<div align="center">

```
██╗  ██╗ ██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ██████╗
██║ ██╔╝███║████╗  ██║██╔════╝ ██╔══██╗██╔═████╗██╔══██╗
█████╔╝ ╚██║██╔██╗ ██║██║  ███╗██████╔╝██║██╔██║██████╔╝
██╔═██╗  ██║██║╚██╗██║██║   ██║██╔══██╗████╔╝██║██╔══██╗
██║  ██╗ ██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝██████╔╝
╚═╝  ╚═╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝
```

**Professional Reconnaissance Toolkit for Bug Bounty & Security Assessments**

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/mrx-arafat/k1ngb0b-recon)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/mrx-arafat/k1ngb0b-recon)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

</div>

---

## Overview

K1NGB0B Recon Suite is a professional reconnaissance toolkit designed for bug bounty hunters and security researchers. It provides a unified command-line interface to perform subdomain discovery, HTTP probing, port scanning, vulnerability assessment, and content discovery.

### Features

- **Subdomain Discovery** - Multi-source passive and active subdomain enumeration
- **HTTP Probing** - Fast detection of live hosts with status codes and titles
- **Port Scanning** - High-speed port discovery using RustScan/Nmap
- **Vulnerability Scanning** - Nuclei integration for automated vulnerability detection
- **Content Discovery** - Directory and file fuzzing with FFUF
- **Full Pipeline** - Complete reconnaissance workflow in a single command

---

## Installation

### Requirements

- **Operating System**: macOS or Linux
- **Python**: 3.8 or higher
- **Go**: 1.21 or higher (for Go-based tools)
- **Homebrew** (macOS) or apt/dnf/pacman (Linux)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/mrx-arafat/k1ngb0b-recon.git
cd k1ngb0b-recon

# Run the installer
python3 install.py
```

The installer will automatically:
1. Detect your operating system (macOS/Linux)
2. Install system dependencies via package manager
3. Install Go if not present
4. Install all Go-based security tools
5. Configure PATH for your shell
6. Create default configuration and wordlists

### Manual Installation (macOS)

If you prefer manual installation:

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install go python3 nmap rustscan

# Install Go tools
export PATH="$PATH:$(go env GOPATH)/bin"

go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/tomnomnom/assetfinder@latest
go install github.com/tomnomnom/anew@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/ffuf/ffuf/v2@latest
go install github.com/owasp-amass/amass/v4/...@master

# Add Go bin to PATH permanently
echo 'export PATH="$PATH:$(go env GOPATH)/bin"' >> ~/.zshrc
source ~/.zshrc

# Install Python dependencies
pip3 install aiohttp dnspython psutil requests
```

### Verify Installation

```bash
python3 -m k1ngb0b check
```

Expected output:
```
╔══════════════════════════════════════════════════════════════╗
║  K1NGB0B Recon Suite v3.0.0                                  ║
║  Professional Reconnaissance Toolkit                          ║
║  Author: mrx-arafat (K1NGB0B)                                ║
╚══════════════════════════════════════════════════════════════╝

============================================================
Tool Status
============================================================

Available (13):
  [+] subfinder v2.11.0
  [+] httpx v1.7.4
  [+] nuclei v3.6.2
  [+] naabu v2.3.7
  [+] katana v1.4.0
  [+] assetfinder
  [+] anew
  [+] waybackurls
  [+] gau v2.2.4
  [+] ffuf v2.1.0
  [+] amass v4.2.0
  [+] rustscan v2.3.0
  [+] nmap v7.98
```

---

## Usage

K1NGB0B provides a modular command-line interface. All commands follow the pattern:

```bash
python3 -m k1ngb0b <command> [options]
```

### Available Commands

| Command | Description |
|---------|-------------|
| `discover` | Subdomain discovery |
| `probe` | HTTP probing for live hosts |
| `ports` | Port scanning |
| `vuln` | Vulnerability scanning |
| `content` | Content/directory discovery |
| `full` | Full reconnaissance pipeline |
| `check` | Check tool installation status |

---

## Command Reference

### 1. Subdomain Discovery

Discover subdomains using multiple passive sources (crt.sh, CertSpotter, HackerTarget, etc.).

```bash
python3 -m k1ngb0b discover <domain> [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `-o, --output` | Output directory (default: `<domain>_recon`) |
| `-t, --timeout` | Timeout per source in seconds |
| `--passive-only` | Only use passive discovery |
| `--active-only` | Only use active discovery |
| `--permutations` | Generate subdomain permutations |

**Example:**
```bash
python3 -m k1ngb0b discover hackerone.com -o ./output --passive-only
```

**Output:**
```
============================================================
Subdomain Discovery: hackerone.com
============================================================

[*] Running passive discovery...
[*] Starting passive discovery for hackerone.com
[*]   Querying crt.sh...
[*]   Querying CertSpotter...
[*]   Querying subdomain.center...
[*]   Querying HackerTarget...
[*]   Querying ThreatCrowd...
[*]   Querying RapidDNS...
[+] Passive discovery complete: 34 subdomains found
[+] Passive discovery: 34 subdomains
[*] Saved 34 subdomains to ./output/02_processed_data/all_subdomains.txt
[+] Total unique subdomains: 34
[*] Results saved to: ./output
```

---

### 2. HTTP Probing

Probe discovered subdomains for live HTTP services.

```bash
python3 -m k1ngb0b probe [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `-d, --domain` | Single domain to probe |
| `-l, --list` | File with list of targets |
| `-o, --output` | Output file |
| `-t, --timeout` | Request timeout in seconds |
| `--threads` | Number of concurrent threads |

**Example:**
```bash
python3 -m k1ngb0b probe -l subdomains.txt -o live_hosts.txt --threads 10
```

**Output:**
```
============================================================
HTTP Probing
============================================================

[*] Probing 34 targets for live HTTP services...
[+] Probing complete: 6 live, 28 dead
[+] Live hosts: 6
  [200] https://api.hackerone.com - HackerOne API
  [200] https://www.hackerone.com - HackerOne | Global leader in offensive security
  [200] https://docs.hackerone.com - HackerOne Help Center
  [200] https://hackerone.com - HackerOne | Global leader in offensive security
  [302] https://support.hackerone.com
  [404] https://mta-sts.forwarding.hackerone.com - Page not found
[*] Saved to live_hosts.txt
```

---

### 3. Port Scanning

Fast port discovery using RustScan or Nmap.

```bash
python3 -m k1ngb0b ports [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `-t, --target` | Single target (IP or domain) |
| `-l, --list` | File with list of targets |
| `-p, --ports` | Specific ports to scan (comma-separated) |
| `-o, --output` | Output file |
| `--timeout` | Total timeout in seconds |

**Example:**
```bash
python3 -m k1ngb0b ports -t hackerone.com -p 80,443,8080,8443 -o ports.txt
```

**Output:**
```
============================================================
Port Scanning
============================================================

[*] Starting port scan on 1 targets...
[*] Using RustScan for fast port discovery
[+] Port scan complete: 4 open ports found
[+] 104.18.36.214: [80, 443, 8443, 8080]
[*] Saved to ports.txt
```

**Port scan results (JSON):**
```json
{
  "total_hosts": 1,
  "total_open_ports": 4,
  "duration": 0.02,
  "hosts": {
    "104.18.36.214": {
      "ports": [80, 443, 8443, 8080],
      "services": {}
    }
  }
}
```

---

### 4. Vulnerability Scanning

Scan targets for vulnerabilities using Nuclei.

```bash
python3 -m k1ngb0b vuln [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `-t, --target` | Single target URL |
| `-l, --list` | File with list of URLs |
| `-s, --severity` | Severity filter (info,low,medium,high,critical) |
| `-o, --output` | Output file |
| `--timeout` | Total timeout in seconds |

**Example:**
```bash
python3 -m k1ngb0b vuln -t https://hackerone.com -s medium,high,critical -o vulns.txt
```

**Output:**
```
============================================================
Vulnerability Scanning
============================================================

[*] Starting vulnerability scan on 1 targets...
[*] Severity filter: medium, high, critical
[+] Vulnerability scan complete: 0 findings
[*] Saved to vulns.txt
```

---

### 5. Content Discovery

Discover hidden directories and files using FFUF.

```bash
python3 -m k1ngb0b content [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `-t, --target` | Target URL (required) |
| `-w, --wordlist` | Custom wordlist file |
| `-e, --extensions` | File extensions (comma-separated) |
| `-o, --output` | Output file |
| `--timeout` | Total timeout in seconds |

**Example:**
```bash
python3 -m k1ngb0b content -t https://example.com -e php,html,js -o content.txt
```

---

### 6. Full Reconnaissance Pipeline

Run the complete reconnaissance workflow in a single command.

```bash
python3 -m k1ngb0b full <domain> [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `-o, --output` | Output directory |
| `--skip-ports` | Skip port scanning |
| `--skip-vuln` | Skip vulnerability scanning |

**Example:**
```bash
python3 -m k1ngb0b full hackerone.com -o ./full_recon
```

This runs:
1. Subdomain discovery
2. HTTP probing
3. Port scanning
4. Vulnerability scanning
5. Generates comprehensive report

---

## Real-World Example: Reconnaissance on hackerone.com

Here's a complete walkthrough of running K1NGB0B on `hackerone.com`:

### Step 1: Subdomain Discovery

```bash
mkdir -p /tmp/k1ngb0b_test
python3 -m k1ngb0b discover hackerone.com -o /tmp/k1ngb0b_test --passive-only
```

**Results:** 34 unique subdomains discovered including:
- `api.hackerone.com`
- `www.hackerone.com`
- `docs.hackerone.com`
- `support.hackerone.com`
- `events.hackerone.com`
- `go.hackerone.com`
- And 28 more...

### Step 2: HTTP Probing

```bash
python3 -m k1ngb0b probe -l /tmp/k1ngb0b_test/02_processed_data/all_subdomains.txt \
    -o /tmp/k1ngb0b_test/live_hosts.txt --threads 10
```

**Results:** 6 live hosts identified:
| Status | Host | Title |
|--------|------|-------|
| 200 | https://api.hackerone.com | HackerOne API |
| 200 | https://www.hackerone.com | HackerOne Global Leader |
| 200 | https://docs.hackerone.com | HackerOne Help Center |
| 200 | https://hackerone.com | HackerOne Global Leader |
| 302 | https://support.hackerone.com | Redirect |
| 404 | https://mta-sts.forwarding.hackerone.com | GitHub Pages |

### Step 3: Port Scanning

```bash
python3 -m k1ngb0b ports -t hackerone.com -p 80,443,8080,8443 \
    -o /tmp/k1ngb0b_test/ports.txt
```

**Results:** 4 open ports on `104.18.36.214`:
- Port 80 (HTTP)
- Port 443 (HTTPS)
- Port 8080 (HTTP Alternate)
- Port 8443 (HTTPS Alternate)

### Step 4: Vulnerability Scanning

```bash
python3 -m k1ngb0b vuln -t https://hackerone.com -s info,low \
    -o /tmp/k1ngb0b_test/vulns.txt
```

**Results:** No vulnerabilities found (expected on a hardened bug bounty platform).

---

## Output Directory Structure

K1NGB0B organizes results in a structured directory:

```
target_recon/
├── 01_raw_discovery/          # Raw tool outputs
├── 02_processed_data/         # Cleaned and deduplicated data
│   └── all_subdomains.txt     # All discovered subdomains
├── 03_live_analysis/          # Live host analysis
├── 04_technologies/           # Technology fingerprinting
├── 05_vulnerabilities/        # Vulnerability scan results
├── 06_port_scanning/          # Port scan results
├── 07_screenshots/            # Visual evidence
├── 08_final_reports/          # Summary reports
├── 09_advanced_discovery/     # Advanced discovery results
└── 10_manual_verification/    # Manual review checklists
```

---

## Installed Tools

K1NGB0B integrates with the following security tools:

| Tool | Version | Purpose |
|------|---------|---------|
| subfinder | v2.11.0 | Subdomain enumeration |
| httpx | v1.7.4 | HTTP probing and fingerprinting |
| nuclei | v3.6.2 | Vulnerability scanning |
| naabu | v2.3.7 | Port scanning |
| katana | v1.4.0 | Web crawling |
| assetfinder | latest | Subdomain discovery |
| anew | latest | Deduplication |
| waybackurls | latest | Wayback Machine URL extraction |
| gau | v2.2.4 | URL collection |
| ffuf | v2.1.0 | Web fuzzing |
| amass | v4.2.0 | Attack surface mapping |
| rustscan | v2.3.0 | Fast port scanning |
| nmap | v7.98 | Network scanning |

---

## Configuration

K1NGB0B stores configuration and wordlists in `~/.k1ngb0b/`:

```
~/.k1ngb0b/
├── config.json           # Default configuration
└── wordlists/
    └── common.txt        # Default wordlist for content discovery
```

### Environment Variables

```bash
# Custom timeout settings
export K1NGB0B_TIMEOUT=120

# Nuclei template path
export NUCLEI_TEMPLATES=~/.nuclei-templates

# Maximum concurrent threads
export K1NGB0B_THREADS=50
```

---

## Troubleshooting

### Tools not found in PATH

```bash
# Add Go bin to PATH
export PATH="$PATH:$(go env GOPATH)/bin"

# Make permanent
echo 'export PATH="$PATH:$(go env GOPATH)/bin"' >> ~/.zshrc
source ~/.zshrc
```

### Permission denied

```bash
# Make scripts executable
chmod +x install.py
```

### Python module not found

```bash
# Install dependencies
pip3 install aiohttp dnspython psutil requests
```

### RustScan not found (macOS)

```bash
brew install rustscan
```

### Nuclei templates outdated

```bash
nuclei -update-templates
```

---

## Legal Disclaimer

This tool is intended for authorized security testing and bug bounty research only. Users are responsible for:

- Obtaining proper authorization before testing
- Complying with all applicable laws and regulations
- Respecting bug bounty program scope and rules
- Using the tool ethically and responsibly

**Never use this tool on systems you don't own or have explicit permission to test.**

---

## Author

**mrx-arafat (K1NGB0B)**

- GitHub: [@mrx-arafat](https://github.com/mrx-arafat)
- Twitter: [@easinxarafat](https://twitter.com/easinxarafat)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [ProjectDiscovery](https://projectdiscovery.io/) - For excellent reconnaissance tools
- [OWASP](https://owasp.org/) - For security testing methodologies
- [SecLists](https://github.com/danielmiessler/SecLists) - For comprehensive wordlists
- The bug bounty community for continuous feedback

---

<div align="center">

**K1NGB0B Recon Suite v3.0.0**

*Professional Reconnaissance Made Simple*

</div>
