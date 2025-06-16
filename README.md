# 🎯 K1NGB0B Professional Recon Suite

<div align="center">

```
██╗  ██╗ ██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ██████╗
██║ ██╔╝███║████╗  ██║██╔════╝ ██╔══██╗██╔═████╗██╔══██╗
█████╔╝ ╚██║██╔██╗ ██║██║  ███╗██████╔╝██║██╔██║██████╔╝
██╔═██╗  ██║██║╚██╗██║██║   ██║██╔══██╗████╔╝██║██╔══██╗
██║  ██╗ ██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝██████╔╝
╚═╝  ╚═╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝
```

**Professional-Grade Domain Reconnaissance & Vulnerability Assessment Suite**

*Designed for Bug Bounty Hunters, Penetration Testers & Security Professionals*

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/mrx-arafat/k1ngb0b-recon)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://github.com/mrx-arafat/k1ngb0b-recon)
[![VPS Ready](https://img.shields.io/badge/VPS-Ready-orange.svg)](https://github.com/mrx-arafat/k1ngb0b-recon)

</div>

## 🚀 Overview

K1NGB0B is a comprehensive, professional-grade reconnaissance suite specifically designed for bug bounty hunting and security assessments. Built with VPS deployment in mind, it features intelligent timeout management, professional error handling, and automated fallback mechanisms for stuck processes.

### 🎯 Key Features

- **🧠 Intelligent Reconnaissance**: Multi-source subdomain enumeration with smart filtering
- **⚡ Professional Timeout Management**: Advanced process monitoring with automatic recovery
- **🛡️ VPS-Optimized**: Designed for remote server deployment with resource management
- **📊 Comprehensive Reporting**: Professional JSON reports with detailed analytics
- **🔄 Smart Wordlists**: SecLists integration with context-aware wordlist selection
- **🚨 Vulnerability Scanning**: Nuclei integration with professional timeout handling
- **📸 Visual Intelligence**: Automated screenshot capture for manual review
- **🔧 Manual Fallback**: Automatic generation of manual commands for failed operations

## 🏗️ Architecture

The suite consists of two main components:

1. **`k1ngb0b_recon.py`** - Primary reconnaissance engine
2. **`k1ngb0b_recon_II.py`** - Advanced post-reconnaissance analysis

## 📦 Quick Installation

### Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/mrx-arafat/k1ngb0b-recon.git
cd k1ngb0b-recon

# Run the professional installer
chmod +x install.sh && ./install.sh
```

The installer automatically handles:
- ✅ System dependencies (Python 3.8+, Go 1.19+)
- ✅ Python packages (aiohttp, dnspython, psutil)
- ✅ Go reconnaissance tools (20+ professional tools)
- ✅ PATH configuration and environment setup
- ✅ Nuclei template updates
- ✅ Wordlist directory preparation

### Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

```bash
# Install system dependencies
sudo apt update && sudo apt install -y python3 python3-pip golang-go curl wget git

# Install Python dependencies
pip3 install --user aiohttp dnspython psutil requests

# Install Go tools
go install github.com/tomnomnom/assetfinder@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/tomnomnom/anew@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/ffuf/ffuf@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/lc/gau@latest
go install github.com/sensepost/gowitness@latest

# Update PATH
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
source ~/.bashrc

# Update Nuclei templates
nuclei -update-templates
```

</details>

## 🎯 Usage

### Phase 1: Primary Reconnaissance

```bash
python3 k1ngb0b_recon.py
```

**What it does:**
- 🔍 Multi-source subdomain enumeration (AssetFinder, Subfinder, Amass, Certificate Transparency)
- 🧠 Smart wordlist-based discovery using SecLists
- 🌐 DNS analysis and port scanning
- 🛠️ Technology detection and fingerprinting
- ✅ Live subdomain validation with httpx
- 📊 Comprehensive JSON reporting

### Phase 2: Advanced Analysis

```bash
python3 k1ngb0b_recon_II.py
```

**What it does:**
- 🚨 Professional Nuclei vulnerability scanning with timeout management
- 📁 Smart directory enumeration with context-aware wordlists
- 🔌 API endpoint discovery (REST, GraphQL, Swagger)
- 🔗 URL discovery via Wayback Machine and GAU
- 🔧 Parameter discovery with ParamSpider
- 📸 Automated screenshot capture
- 📝 Manual command generation for failed operations

## 🏆 Professional Features

### 🛡️ VPS-Optimized Design

- **Resource Management**: Intelligent concurrency limits
- **Timeout Handling**: Professional process monitoring
- **Error Recovery**: Automatic fallback mechanisms
- **Manual Commands**: Generated for stuck/failed processes

### 🧠 Smart Intelligence

- **Context-Aware Wordlists**: Technology-specific enumeration
- **SecLists Integration**: Automatic wordlist downloading
- **Technology Detection**: CMS, frameworks, and API identification
- **Rate Limiting**: Professional request throttling

### 📊 Professional Reporting

- **Comprehensive Analytics**: Detailed execution statistics
- **Vulnerability Summaries**: Severity-based categorization
- **Manual Review Guidance**: Clear next-step instructions
- **JSON Export**: Machine-readable results

## 📁 Output Structure

```
target_domain_results_20240616_143022/
├── raw/                          # Raw tool outputs
│   ├── assetfinder.txt
│   ├── subfinder.txt
│   ├── crt.txt
│   └── amass.txt
├── processed/                    # Processed results
│   ├── all_subdomains.txt
│   ├── httpx_results.txt
│   └── dns_records.json
├── technologies/                 # Technology detection
│   └── detected_technologies.json
├── ports/                        # Port scan results
│   └── open_ports.json
├── reports/                      # Professional reports
│   └── enhanced_report.json
├── advanced_analysis/            # Phase 2 results
│   ├── vulnerabilities/
│   │   ├── nuclei_results.json
│   │   └── nuclei_stats.json
│   ├── directories/
│   ├── urls/
│   ├── parameters/
│   ├── screenshots/
│   ├── manual_commands.json     # Failed operations
│   ├── manual_commands.sh       # Executable script
│   └── advanced_analysis_report.json
└── wordlists/                    # Cached SecLists
```

## 🚨 Professional Timeout Management

### Nuclei Timeout Handling

When Nuclei scans timeout or get stuck:

```bash
⏰ TIMEOUT: Nuclei vulnerability scan exceeded 30m 0s
🔄 Terminating process gracefully...
✅ Nuclei vulnerability scan terminated gracefully
⚠️  SKIPPED: Nuclei vulnerability scan due to timeout
📝 Manual command logged for later execution
```

### Manual Command Generation

Failed operations are automatically logged:

```bash
# Manual commands that timed out or failed
# Review and execute manually as needed

# Nuclei vulnerability scan
# Reason: Timeout after 1800s
nuclei -list targets.txt -json -o results.json -severity low,medium,high,critical
```

## 🎯 Bug Bounty Workflow

### 1. Initial Reconnaissance
```bash
python3 k1ngb0b_recon.py
# Enter target domain: example.com
```

### 2. Advanced Analysis
```bash
python3 k1ngb0b_recon_II.py
# Automatically finds latest results
```

### 3. Manual Review
```bash
# Review generated reports
cat example_com_results_*/reports/enhanced_report.json

# Execute manual commands if needed
chmod +x example_com_results_*/advanced_analysis/manual_commands.sh
./example_com_results_*/advanced_analysis/manual_commands.sh
```

### 4. Vulnerability Assessment
```bash
# Review Nuclei findings
jq '.vulnerabilities' example_com_results_*/advanced_analysis/advanced_analysis_report.json

# Check screenshots for manual verification
ls example_com_results_*/advanced_analysis/screenshots/
```

## 🔧 Configuration

### Environment Variables

```bash
# Customize timeouts (optional)
export NUCLEI_TIMEOUT=3600        # 1 hour for large targets
export MAX_CONCURRENT_SCANS=10    # Reduce for limited VPS
export SCREENSHOT_TIMEOUT=600     # 10 minutes for screenshots
```

### VPS Optimization

For VPS deployment, consider:

```bash
# Increase file descriptor limits
ulimit -n 65536

# Monitor resource usage
htop

# Use screen/tmux for long-running scans
screen -S recon
python3 k1ngb0b_recon.py
# Ctrl+A, D to detach
```

## 🛠️ Supported Tools

### Core Reconnaissance
- **AssetFinder** - Subdomain discovery
- **Subfinder** - Multi-source subdomain enumeration
- **Amass** - Comprehensive OSINT framework
- **httpx** - Fast HTTP probing
- **anew** - Result deduplication

### Advanced Analysis
- **Nuclei** - Vulnerability scanner
- **FFUF** - Web fuzzer
- **Gobuster** - Directory brute-forcer
- **Gowitness** - Screenshot tool
- **Waybackurls** - Wayback Machine URL extraction
- **GAU** - GetAllUrls
- **ParamSpider** - Parameter discovery

### Smart Wordlists (SecLists)
- **Subdomain wordlists** - DNS enumeration
- **Directory wordlists** - Path discovery
- **API wordlists** - Endpoint enumeration
- **Parameter wordlists** - Parameter fuzzing
- **Technology-specific** - CMS, frameworks

## 🐛 Troubleshooting

### Common Issues

**Tools not found in PATH:**
```bash
source ~/.bashrc
# or
export PATH=$PATH:$(go env GOPATH)/bin
```

**Permission denied:**
```bash
chmod +x install.sh
chmod +x k1ngb0b_recon.py
chmod +x k1ngb0b_recon_II.py
```

**Nuclei templates outdated:**
```bash
nuclei -update-templates
```

**Python import errors:**
```bash
pip3 install --user aiohttp dnspython psutil
```

### VPS-Specific Issues

**Resource limitations:**
```bash
# Reduce concurrent processes
export MAX_CONCURRENT_SCANS=5

# Monitor memory usage
free -h
```

**Network timeouts:**
```bash
# Increase timeouts for slow networks
export REQUEST_TIMEOUT=60
export DNS_TIMEOUT=30
```

## 📈 Performance Benchmarks

| Target Size | Subdomains Found | Analysis Time | Memory Usage |
|-------------|------------------|---------------|--------------|
| Small (< 50 subs) | 25-100 | 5-15 min | 200-500 MB |
| Medium (50-200 subs) | 100-500 | 15-45 min | 500 MB-1 GB |
| Large (200+ subs) | 500+ | 45+ min | 1-2 GB |

*Benchmarks on 2 CPU, 4GB RAM VPS*

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting PRs.

### Development Setup

```bash
git clone https://github.com/mrx-arafat/k1ngb0b-recon.git
cd k1ngb0b-recon
pip3 install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and authorized testing purposes only. Users are responsible for complying with applicable laws and obtaining proper authorization before testing.

## 🙏 Acknowledgments

- **ProjectDiscovery** - For excellent reconnaissance tools
- **OWASP** - For security testing methodologies
- **SecLists** - For comprehensive wordlists
- **Bug Bounty Community** - For continuous feedback and improvements

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/mrx-arafat/k1ngb0b-recon/issues)
- **Discussions**: [Feature requests](https://github.com/mrx-arafat/k1ngb0b-recon/discussions)
- **Twitter**: [@mrx_arafat](https://twitter.com/mrx_arafat)

---

<div align="center">

**Made with ❤️ by [mrx-arafat](https://github.com/mrx-arafat) (K1NGB0B)**

*Happy Bug Hunting! 🐛🎯*

</div>
