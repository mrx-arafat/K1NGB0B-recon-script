# K1NGB0B Recon Script - Intelligent Installer Guide

## Overview

The K1NGB0B Recon Script comes with a comprehensive, intelligent installation system that automatically detects and installs all required dependencies. This installer is designed to be foolproof and work across different operating systems and configurations.

## Features

### 🔍 **Automatic Dependency Detection**
- **Python 3.8+** with version checking
- **Go 1.19+** with proper GOPATH configuration
- **System tools** (curl, wget, git)
- **Reconnaissance tools** (assetfinder, subfinder, httpx, anew)
- **Python packages** from requirements.txt

### 🚀 **Smart Installation**
- **Cross-platform support** (Linux, macOS, Windows WSL)
- **Package manager detection** (apt, yum, dnf, brew, pacman)
- **Automatic Go installation** from official sources
- **Python package management** with pip
- **Error handling and recovery**

### 🎯 **User Experience**
- **Colored output** with progress indicators
- **Detailed logging** for troubleshooting
- **Permission checking** and sudo handling
- **Installation verification** and testing
- **Comprehensive summary** and next steps

## Quick Start

### One-Command Installation
```bash
chmod +x install.sh && ./install.sh
```

That's it! The installer will:
1. 🔍 Detect your system and current dependencies
2. 📦 Install missing components automatically
3. ✅ Verify everything works correctly
4. 📋 Show you what was installed and next steps

## Detailed Usage

### Running the Installer
```bash
# Make executable and run
chmod +x install.sh
./install.sh

# Or run directly with bash
bash install.sh
```

### What the Installer Does

#### 1. **System Detection**
```
🔍 System Detection
✓ Detected OS: Linux
✓ Detected Architecture: amd64
✓ Package Manager: APT (Debian/Ubuntu)
```

#### 2. **Dependency Analysis**
```
🔍 Dependency Analysis
→ Checking Python installation...
✓ Python 3.9.2 found (python3)
✓ pip found (pip3)
→ Checking Go installation...
✗ Go 1.19+ not found
→ Checking system tools...
✓ curl found
✓ wget found
✓ git found
→ Checking reconnaissance tools...
✗ assetfinder not found
✗ subfinder not found
✗ httpx not found
✗ anew not found
```

#### 3. **Installation Process**
```
📦 Installing System Dependencies
→ Installing Go from official source...
ℹ Downloading Go 1.21.5 for linux-amd64...
→ Installing Go to /usr/local/go...
✓ Go installed successfully

🐍 Installing Python Dependencies
→ Installing Python packages...
✓ Python dependencies installed

🔧 Installing Reconnaissance Tools
→ Installing assetfinder...
→ Installing subfinder...
→ Installing httpx...
→ Installing anew...
✓ Reconnaissance tools installed
```

#### 4. **Verification**
```
🧪 Verifying Installation
→ Re-checking Python...
✓ Python 3.9.2 found (python3)
→ Re-checking Go...
✓ Go 1.21.5 found
→ Re-checking system tools...
✓ All system tools found
→ Re-checking reconnaissance tools...
✓ All reconnaissance tools found
→ Testing Python imports...
✓ Python imports working
→ Testing K1NGB0B Recon Script...
✓ K1NGB0B Recon Script is working
✓ All verifications passed!
```

## Supported Systems

### Operating Systems
- **Linux** (Ubuntu, Debian, CentOS, RHEL, Fedora, Arch)
- **macOS** (with Homebrew)
- **Windows** (WSL/Cygwin)

### Package Managers
- **APT** (Debian/Ubuntu)
- **YUM** (RHEL/CentOS)
- **DNF** (Fedora)
- **Homebrew** (macOS)
- **Pacman** (Arch Linux)

### Architectures
- **x86_64** (amd64)
- **ARM64** (aarch64)
- **ARMv6/v7** (Raspberry Pi)
- **i386** (32-bit)

## Troubleshooting

### Common Issues

#### "Permission denied" Error
```bash
# Solution: Make the script executable
chmod +x install.sh
./install.sh
```

#### "sudo: command not found"
```bash
# On systems without sudo, run as root
su -
./install.sh
```

#### Go Installation Fails
```bash
# Manual Go installation
wget https://golang.org/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

#### Python Dependencies Fail
```bash
# Update pip and try again
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

#### Tools Not Found After Installation
```bash
# Add Go bin to PATH
export PATH=$PATH:$(go env GOPATH)/bin
# Or restart your terminal
```

### Debug Mode

For detailed troubleshooting, check the installation log:
```bash
# View the installation log
cat /tmp/k1ngb0b_install.log

# Run with verbose output
bash -x install.sh
```

### Manual Installation

If the automatic installer fails, you can install components manually:

#### 1. Install Python 3.8+
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS
brew install python3
```

#### 2. Install Go 1.19+
```bash
# Download and install Go
wget https://golang.org/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Install System Tools
```bash
# Ubuntu/Debian
sudo apt-get install curl wget git

# CentOS/RHEL
sudo yum install curl wget git
```

#### 4. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

#### 5. Install Go Tools
```bash
go install github.com/tomnomnom/assetfinder@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/tomnomnom/anew@latest
```

## Advanced Options

### Environment Variables

You can customize the installation by setting environment variables:

```bash
# Custom Go version
export GO_VERSION="1.21.5"

# Custom installation directory
export INSTALL_DIR="/opt/k1ngb0b"

# Skip certain components
export SKIP_GO_INSTALL="true"
export SKIP_PYTHON_DEPS="true"

./install.sh
```

### Offline Installation

For systems without internet access:

1. Download all required files on a connected system
2. Transfer to the target system
3. Run the installer with local files

## Security Considerations

### What the Installer Does
- Downloads Go from official golang.org
- Installs packages using system package managers
- Downloads Go tools from official GitHub repositories
- Only modifies user's shell configuration files

### What the Installer Doesn't Do
- Modify system-wide configurations unnecessarily
- Install untrusted software
- Send data to external servers
- Modify existing installations destructively

### Running as Root
The installer will warn if run as root and ask for confirmation. It's recommended to run as a regular user with sudo access.

## Support

If you encounter issues with the installer:

1. **Check the log**: `/tmp/k1ngb0b_install.log`
2. **Run with debug**: `bash -x install.sh`
3. **Try manual installation** (see above)
4. **Report issues**: Create an issue on GitHub with:
   - Your operating system and version
   - The installation log
   - Error messages

---

**Author**: mrx-arafat (K1NGB0B)  
**Version**: 2.0.0  
**Last Updated**: 2024
