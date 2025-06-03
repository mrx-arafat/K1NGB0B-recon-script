# K1NGB0B Recon Script

🎯 **Simple Domain Reconnaissance Tool for Bug Bounty Hunters**

## Quick Start

1. **Install all dependencies:**
   ```bash
   chmod +x install.sh && ./install.sh
   ```

2. **Run the tool:**
   ```bash
   python k1ngb0b_recon.py
   ```

3. **Enter your target domain when prompted**

That's it! 🚀

## Features

- 🔍 **Finds subdomains** using multiple sources (assetfinder, subfinder, crt.sh)
- ✅ **Checks which are live** using httpx
- 📁 **Organizes results** in clean folders
- 📊 **Generates reports** in JSON format
- 🛡️ **Dependency checking** - Won't run without all tools installed
- 🐧 **Linux focused** - Optimized for Linux systems

## Requirements (Auto-installed)

- Python 3.8+
- Go 1.19+
- assetfinder (Go tool)
- subfinder (Go tool)
- httpx (Go tool)
- anew (Go tool)
- aiohttp (Python package)

## Example Output

```
🔍 Checking dependencies...
✅ All dependencies found!

🔍 Enter target domain (e.g., tesla.com): tesla.com
✅ Target domain: tesla.com

🎯 Starting reconnaissance for: tesla.com
🔍 Running assetfinder...
   ✅ Found 15 subdomains
🔍 Running subfinder...
   ✅ Found 23 subdomains
🔍 Checking Certificate Transparency (crt.sh)...
   ✅ Found 12 subdomains
🔍 Checking live subdomains...
   ✅ Found 8 live subdomains

📊 Results: 31 unique subdomains, 8 live
📁 Results saved to: tesla_com_results/
✅ Reconnaissance completed successfully!
```

## Author

**mrx-arafat** (K1NGB0B)
