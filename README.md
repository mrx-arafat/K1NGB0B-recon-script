# 🎯 K1NGB0B Recon Script

> **The Ultimate Domain Reconnaissance Tool for Bug Bounty Hunters & Security Professionals**

Discover subdomains like a pro! This powerful tool automates the entire subdomain discovery process using multiple sources and provides live verification - all with a single command.

## ⚡ Quick Start (TL;DR)

**Want to get started immediately? Here's all you need:**

```bash
# 1. Install everything (one command!)
chmod +x install.sh && ./install.sh

# 2. Run your first scan
python -m k1ngb0b_recon example.com

# 3. Check your results
ls example_com/processed/live_subdomains.txt
```

**That's it!** 🎉 You now have all the live subdomains for your target.

---

## 🚀 What Does This Tool Do?

**In Simple Terms**: Give it a domain (like `example.com`) and it will find ALL the subdomains (like `api.example.com`, `admin.example.com`, etc.) automatically!

### 🎯 Perfect For:
- 🔍 **Bug Bounty Hunters** - Find hidden attack surfaces
- 🛡️ **Security Professionals** - Audit your organization's domains
- 🔬 **Penetration Testers** - Comprehensive reconnaissance
- 📊 **Security Researchers** - Domain analysis and mapping

## ✨ Key Features

### 🔍 **Smart Multi-Source Discovery**
- **AssetFinder** - Fast subdomain enumeration
- **Subfinder** - Passive subdomain discovery
- **Certificate Transparency** - SSL certificate logs
- **Wayback Machine** - Historical subdomain data
- **Manual Input** - Add your own findings

### ⚡ **Advanced Capabilities**
- **Live Verification** - Check which subdomains are actually active
- **Lightning Fast** - Concurrent processing for speed
- **Smart Organization** - Clean, organized results
- **Progress Tracking** - See exactly what's happening
- **Professional Reports** - JSON and text output formats

## 📥 Installation

### 🚀 Super Easy Installation (Recommended)

**Just run this one command and you're ready to go!**

```bash
chmod +x install.sh && ./install.sh
```

That's it! The script will automatically:
- ✅ Install Python dependencies
- ✅ Install all required tools (assetfinder, subfinder, httpx, anew)
- ✅ Set up everything for you

### 🛠️ Manual Installation (If you prefer to do it yourself)

**Step 1: Get the code**
```bash
git clone https://github.com/mrx-arafat/K1NGB0B-recon-script.git
cd K1NGB0B-recon-script
```

**Step 2: Install Python stuff**
```bash
pip install -r requirements.txt
```

**Step 3: Install the reconnaissance tools**
```bash
# Install Go tools (you need Go installed first)
go install github.com/tomnomnom/assetfinder@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/tomnomnom/anew@latest
```

---

## 🎮 How to Use

### 🎯 Basic Usage (Most Common)

**Find all subdomains for a domain:**
```bash
python -m k1ngb0b_recon example.com
```

**That's it!** The tool will:
1. 🔍 Find subdomains from multiple sources
2. ✅ Check which ones are live/active
3. 📁 Save everything in organized folders
4. 📊 Generate a nice report

### 🔧 Advanced Options

**Save results to a specific folder:**
```bash
python -m k1ngb0b_recon example.com --output /path/to/my/results
```

**Skip the live checking (faster, but less info):**
```bash
python -m k1ngb0b_recon example.com --no-live
```

**See detailed progress (verbose mode):**
```bash
python -m k1ngb0b_recon example.com --verbose
```

**Use a custom configuration file:**
```bash
python -m k1ngb0b_recon example.com --config my-config.yaml
```

### 📋 Real Examples

```bash
# Scan Tesla's domain
python -m k1ngb0b_recon tesla.com

# Scan with verbose output to see what's happening
python -m k1ngb0b_recon bugcrowd.com --verbose

# Scan and save to a specific directory
python -m k1ngb0b_recon hackerone.com --output ./my-recon-results
```

---

## 📊 What You Get

When you run the tool, here's what happens and what you get:

### 🔄 **During the Scan**
```
🎯 K1NGB0B Recon Script v2.0
Starting reconnaissance for example.com...
✓ Running assetfinder... (Found 45 subdomains)
✓ Running subfinder... (Found 67 subdomains)
✓ Fetching from Certificate Transparency... (Found 23 subdomains)
✓ Checking Wayback Machine... (Found 12 subdomains)
✓ Checking live subdomains... (32 are active)
📊 Reconnaissance completed in 2.3 minutes
```

### 📁 **Results You Get**
After the scan, you'll have a neat folder structure like this:

```
example_com/                    # Main results folder
├── raw/                        # Raw data from each tool
│   ├── assetfinder.txt        # Subdomains from AssetFinder
│   ├── subfinder.txt          # Subdomains from Subfinder
│   ├── crt.txt                # Subdomains from SSL certificates
│   ├── wayback.txt            # Subdomains from Wayback Machine
│   └── manual.txt             # Any manual subdomains you added
├── processed/                  # Clean, organized results
│   ├── all_subdomains.txt     # All unique subdomains found
│   ├── unique_subdomains.txt  # Deduplicated list
│   └── live_subdomains.txt    # Only the active/live ones ⭐
├── reports/                    # Professional reports
│   ├── summary.json           # Machine-readable summary
│   ├── summary.txt            # Human-readable report
│   └── recon_report.html      # Pretty HTML report (coming soon)
└── logs/                       # Detailed logs
    └── recon.log              # What happened during the scan
```

### 🎯 **Key Files to Check**
- **`live_subdomains.txt`** ← This is the gold! Active subdomains you can test
- **`summary.txt`** ← Quick overview of what was found
- **`all_subdomains.txt`** ← Complete list of all discovered subdomains

---

## Project Structure

```
K1NGB0B-recon-script/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup configuration
├── config.yaml                  # Default configuration file
├── install.sh                   # One-click installation script
├── example.py                   # Usage example
├── domain_discovery.sh          # Original bash script (legacy)
├── .gitignore                   # Git ignore rules
├── src/
│   └── k1ngb0b_recon/          # Main package
│       ├── __init__.py
│       ├── __main__.py          # Module entry point
│       ├── main.py              # Main application logic
│       ├── config.py            # Configuration management
│       ├── subdomain_discovery.py  # Core discovery logic
│       └── utils.py             # Utility functions
├── scripts/
│   └── quick_install.sh         # Quick installation script
└── tests/
    ├── __init__.py
    └── test_utils.py            # Unit tests
```

## Output Structure

```
target_domain/
├── raw/
│   ├── assetfinder.txt
│   ├── subfinder.txt
│   ├── crt.txt
│   ├── wayback.txt
│   └── manual.txt
├── processed/
│   ├── all_subdomains.txt
│   ├── unique_subdomains.txt
│   └── live_subdomains.txt
├── reports/
│   ├── summary.json
│   ├── summary.txt
│   └── recon_report.html
└── logs/
    └── recon.log
```

## Configuration

Create a `config.yaml` file to customize the tool behavior:

```yaml
# Tool configurations
tools:
  assetfinder:
    enabled: true
    timeout: 300
  subfinder:
    enabled: true
    timeout: 300
    config_file: ~/.config/subfinder/config.yaml
  crt_sh:
    enabled: true
    timeout: 60
  wayback:
    enabled: true
    timeout: 120

# Output settings
output:
  create_reports: true
  save_raw_data: true
  compress_results: false

# HTTP settings
http:
  timeout: 10
  retries: 3
  threads: 50
```

## ❓ Troubleshooting

### 🚨 Common Issues & Solutions

**Problem: "No module named 'click'"**
```bash
# Solution: Install Python dependencies
pip install -r requirements.txt
```

**Problem: "assetfinder: command not found"**
```bash
# Solution: Install Go tools or run the installer
./install.sh
# OR manually install Go tools
go install github.com/tomnomnom/assetfinder@latest
```

**Problem: "Permission denied" when running install.sh**
```bash
# Solution: Make the script executable
chmod +x install.sh
./install.sh
```

**Problem: Tool runs but finds very few subdomains**
- ✅ Check your internet connection
- ✅ Try running with `--verbose` to see what's happening
- ✅ Some domains simply have fewer subdomains
- ✅ Make sure all tools are properly installed

**Problem: "Go not found"**
- Install Go from https://golang.org/dl/
- Or use the auto-installer: `./install.sh`

### 💡 Pro Tips

- **Run with `--verbose`** to see detailed progress
- **Check the `logs/` folder** if something goes wrong
- **Use `--no-live`** for faster scans (skips live verification)
- **The `live_subdomains.txt` file** is usually what you want for testing

---

## 📋 Requirements

### System Requirements
- 🐍 **Python 3.8+** (most systems have this)
- 🔧 **Go 1.19+** (for the reconnaissance tools)
- 🌐 **Internet connection** (obviously!)
- 💾 **~100MB free space** (for tools and results)

### What Gets Installed
**Python packages:**
- requests, aiohttp (for web requests)
- click (for the command-line interface)
- pyyaml (for configuration files)
- tqdm, colorama (for pretty progress bars)
- jinja2 (for reports)

**Reconnaissance tools:**
- assetfinder (subdomain discovery)
- subfinder (passive subdomain enumeration)
- httpx (live subdomain verification)
- anew (deduplication)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is intended for authorized security testing and educational purposes only. Users are responsible for ensuring they have proper authorization before scanning any domains or systems.

## Credits

- **Author**: mrx-arafat (K1NGB0B)
- **Tools Used**: AssetFinder, Subfinder, httpx, anew
- **Special Thanks**: ProjectDiscovery team, TomNomNom

## Support

If you find this tool useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing to the project

---

**Happy Hunting! 🎯**
