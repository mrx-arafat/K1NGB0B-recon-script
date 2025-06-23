#!/bin/bash

# K1NGB0B Ultimate Recon Installation Script v3.0
# Author: mrx-arafat (K1NGB0B)
# The World's Most Comprehensive Bug Bounty Tool Installation System

set -e

# Global Configuration
REQUIRED_GO_VERSION="1.21"
LATEST_GO_VERSION="1.23.10"
INSTALL_LOG="/tmp/k1ngb0b_ultimate_install.log"
MANUAL_INSTALL_GUIDE="/tmp/k1ngb0b_ultimate_manual_guide.txt"

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Enhanced print functions
print_success() { echo -e "${GREEN}✅${NC} $1" | tee -a "$INSTALL_LOG"; }
print_error() { echo -e "${RED}❌${NC} $1" | tee -a "$INSTALL_LOG"; }
print_warning() { echo -e "${YELLOW}⚠️${NC} $1" | tee -a "$INSTALL_LOG"; }
print_info() { echo -e "${BLUE}ℹ️${NC} $1" | tee -a "$INSTALL_LOG"; }
print_step() { echo -e "${CYAN}→${NC} $1" | tee -a "$INSTALL_LOG"; }
print_progress() { echo -e "${PURPLE}🔄${NC} $1" | tee -a "$INSTALL_LOG"; }
print_phase() { echo -e "${BOLD}${CYAN}🚀 $1${NC}" | tee -a "$INSTALL_LOG"; }

# Utility functions
command_exists() { command -v "$1" >/dev/null 2>&1; }
is_root() { [ "$EUID" -eq 0 ]; }

# Initialize log files
init_logs() {
    echo "K1NGB0B Ultimate Installation Log - $(date)" > "$INSTALL_LOG"
    echo "K1NGB0B Ultimate Manual Installation Guide - $(date)" > "$MANUAL_INSTALL_GUIDE"
    echo "=========================================" >> "$MANUAL_INSTALL_GUIDE"
}

# Print enhanced banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                K1NGB0B ULTIMATE RECONNAISSANCE SUITE v3.0                   ║"
    echo "║                        Author: mrx-arafat (K1NGB0B)                         ║"
    echo "║                                                                              ║"
    echo "║  🎯 THE WORLD'S MOST COMPREHENSIVE BUG BOUNTY TOOL INSTALLER               ║"
    echo "║                                                                              ║"
    echo "║  ✨ Installing 30+ World-Class Bug Bounty Tools:                           ║"
    echo "║     • Subdomain Discovery (8 tools)                                         ║"
    echo "║     • DNS Reconnaissance (5 tools)                                          ║"
    echo "║     • Port Scanning (4 tools)                                               ║"
    echo "║     • Web Content Discovery (6 tools)                                       ║"
    echo "║     • Parameter Discovery (3 tools)                                         ║"
    echo "║     • URL Collection (4 tools)                                              ║"
    echo "║     • Vulnerability Scanning (3 tools)                                      ║"
    echo "║     • Technology Detection (3 tools)                                        ║"
    echo "║     • Visual Reconnaissance (2 tools)                                       ║"
    echo "║     • Network Analysis (3 tools)                                            ║"
    echo "║     • API Discovery (2 tools)                                               ║"
    echo "║     • JavaScript Analysis (3 tools)                                         ║"
    echo "║     • Cloud Asset Discovery (2 tools)                                       ║"
    echo "║     • OSINT & Social Engineering (3 tools)                                  ║"
    echo "║     • Git/Code Analysis (3 tools)                                           ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Enhanced system detection
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif command_exists lsb_release; then
        lsb_release -si | tr '[:upper:]' '[:lower:]'
    else
        echo "unknown"
    fi
}

# Check and upgrade Go
check_and_upgrade_go() {
    print_step "Checking Go installation and version..."

    if ! command_exists go; then
        print_warning "Go not found. Installing latest Go..."
        install_latest_go
        return $?
    fi

    local current_version=$(go version | grep -oE 'go[0-9]+\.[0-9]+(\.[0-9]+)?' | sed 's/go//')
    print_info "Current Go version: $current_version"

    if [ "$(printf '%s\n' "$REQUIRED_GO_VERSION" "$current_version" | sort -V | head -n1)" = "$REQUIRED_GO_VERSION" ]; then
        print_success "Go version $current_version meets requirements (>= $REQUIRED_GO_VERSION)"
        return 0
    else
        print_warning "Go version $current_version is too old. Upgrading to $LATEST_GO_VERSION..."
        install_latest_go
        return $?
    fi
}

# Install latest Go version
install_latest_go() {
    print_progress "Installing Go $LATEST_GO_VERSION..."

    local arch=$(uname -m)
    case $arch in
        x86_64) arch="amd64" ;;
        aarch64) arch="arm64" ;;
        armv7l) arch="armv6l" ;;
        *) print_error "Unsupported architecture: $arch"; return 1 ;;
    esac

    local go_url="https://golang.org/dl/go${LATEST_GO_VERSION}.linux-${arch}.tar.gz"
    local temp_dir="/tmp/go_install"

    if mkdir -p "$temp_dir" && cd "$temp_dir"; then
        if wget -q "$go_url" -O "go${LATEST_GO_VERSION}.tar.gz"; then
            if sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf "go${LATEST_GO_VERSION}.tar.gz"; then
                export PATH=$PATH:/usr/local/go/bin
                echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
                print_success "Go $LATEST_GO_VERSION installed successfully"
                cd - >/dev/null
                rm -rf "$temp_dir"
                return 0
            fi
        fi
    fi

    print_error "Automatic Go installation failed!"
    return 1
}

# Install system dependencies
install_system_deps() {
    print_phase "Installing System Dependencies"
    local distro=$(detect_distro)

    print_progress "Detected distribution: $distro"

    if command_exists apt-get; then
        print_progress "Updating package lists..."
        sudo apt-get update -qq
        print_progress "Installing packages via apt..."
        sudo apt-get install -y python3 python3-pip python3-venv curl wget git golang-go \
            build-essential libssl-dev libffi-dev python3-dev \
            nmap masscan dnsutils whois jq unzip zip \
            chromium-browser xvfb
    elif command_exists yum; then
        print_progress "Installing packages via yum..."
        sudo yum install -y python3 python3-pip curl wget git golang \
            gcc openssl-devel libffi-devel python3-devel \
            nmap masscan bind-utils whois jq unzip zip
    elif command_exists dnf; then
        print_progress "Installing packages via dnf..."
        sudo dnf install -y python3 python3-pip curl wget git golang \
            gcc openssl-devel libffi-devel python3-devel \
            nmap masscan bind-utils whois jq unzip zip
    elif command_exists pacman; then
        print_progress "Installing packages via pacman..."
        sudo pacman -Sy --noconfirm python python-pip curl wget git go \
            gcc openssl libffi jq unzip zip nmap masscan
    else
        print_error "Unsupported package manager!"
        return 1
    fi

    print_success "System dependencies installed"
}

# Install Python dependencies
install_python_deps() {
    print_phase "Installing Python Dependencies"

    local install_success=false

    # Method 1: Try pip install with --user flag
    if command_exists pip3; then
        print_progress "Attempting pip3 install with --user flag..."
        if pip3 install --user aiohttp dnspython psutil requests beautifulsoup4 lxml 2>/dev/null; then
            install_success=true
            print_success "Python packages installed via pip3 --user"
        fi
    fi

    # Method 2: Try pip install with --break-system-packages
    if [ "$install_success" = false ] && command_exists pip3; then
        print_progress "Attempting pip3 install with --break-system-packages..."
        if pip3 install --break-system-packages aiohttp dnspython psutil requests beautifulsoup4 lxml 2>/dev/null; then
            install_success=true
            print_success "Python packages installed via pip3 --break-system-packages"
        fi
    fi

    if [ "$install_success" = false ]; then
        print_error "Failed to install Python dependencies!"
        return 1
    fi
}

# Install Go-based reconnaissance tools
install_go_tools() {
    print_phase "Installing Go-Based Reconnaissance Tools (20+ Tools)"

    if ! command_exists go; then
        print_error "Go is not installed!"
        return 1
    fi

    local gopath=$(go env GOPATH 2>/dev/null)
    if [ -z "$gopath" ]; then
        export GOPATH="$HOME/go"
        mkdir -p "$GOPATH/bin"
    fi

    export PATH=$PATH:/usr/local/go/bin:$gopath/bin

    # Comprehensive list of Go-based tools
    local tools=(
        # Subdomain Discovery
        "github.com/tomnomnom/assetfinder@latest:assetfinder:critical"
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest:subfinder:critical"
        "github.com/OWASP/Amass/v4/cmd/amass@latest:amass:high"
        "github.com/projectdiscovery/chaos-client/cmd/chaos@latest:chaos:medium"
        "github.com/Findomain/Findomain@latest:findomain:medium"
        "github.com/Cgboal/SonarSearch/cmd/crobat@latest:crobat:low"
        "github.com/incogbyte/shosubgo@latest:shosubgo:low"

        # DNS Reconnaissance
        "github.com/blechschmidt/massdns@latest:massdns:critical"
        "github.com/d3mondev/puredns/v2@latest:puredns:critical"
        "github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest:shuffledns:high"
        "github.com/projectdiscovery/dnsx/cmd/dnsx@latest:dnsx:high"

        # Port Scanning
        "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest:naabu:critical"
        "github.com/RustScan/RustScan@latest:rustscan:low"

        # Web Content Discovery
        "github.com/ffuf/ffuf/v2@latest:ffuf:critical"
        "github.com/OJ/gobuster/v3@latest:gobuster:high"
        "github.com/epi052/feroxbuster@latest:feroxbuster:high"

        # Parameter Discovery
        "github.com/s0md3v/Arjun@latest:arjun:critical"
        "github.com/devanshbatham/ParamSpider@latest:paramspider:high"
        "github.com/Sh1Yo/x8@latest:x8:medium"

        # URL Collection
        "github.com/tomnomnom/waybackurls@latest:waybackurls:critical"
        "github.com/lc/gau/v2/cmd/gau@latest:gau:critical"
        "github.com/projectdiscovery/katana/cmd/katana@latest:katana:high"
        "github.com/hakluke/hakrawler@latest:hakrawler:medium"

        # Vulnerability Scanning
        "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest:nuclei:critical"
        "github.com/jaeles-project/jaeles@latest:jaeles:medium"
        "github.com/hahwul/dalfox/v2@latest:dalfox:medium"

        # Technology Detection
        "github.com/projectdiscovery/httpx/cmd/httpx@latest:httpx:critical"

        # Visual Reconnaissance
        "github.com/sensepost/gowitness@latest:gowitness:high"

        # Network Analysis
        "github.com/projectdiscovery/mapcidr/cmd/mapcidr@latest:mapcidr:medium"
        "github.com/projectdiscovery/asnmap/cmd/asnmap@latest:asnmap:medium"

        # API Discovery
        "github.com/assetnote/kiterunner@latest:kiterunner:high"

        # JavaScript Analysis
        "github.com/GerbenJavado/LinkFinder@latest:linkfinder:high"
        "github.com/m4ll0k/SecretFinder@latest:secretfinder:medium"

        # Cloud Asset Discovery
        "github.com/initstring/cloud_enum@latest:cloud_enum:high"
        "github.com/sa7mon/S3Scanner@latest:s3scanner:medium"

        # Utility Tools
        "github.com/tomnomnom/anew@latest:anew:high"
        "github.com/tomnomnom/gf@latest:gf:medium"
        "github.com/1ndianl33t/Gf-Patterns@latest:gf-patterns:low"
        "github.com/tomnomnom/unfurl@latest:unfurl:medium"
        "github.com/tomnomnom/httprobe@latest:httprobe:medium"
        "github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest:interactsh-client:medium"
    )

    local failed_tools=()
    local success_count=0
    local total_tools=${#tools[@]}

    print_info "Installing $total_tools Go-based reconnaissance tools..."
    echo

    for tool_info in "${tools[@]}"; do
        IFS=':' read -r tool_url tool_name priority <<< "$tool_info"

        print_progress "[$((success_count + 1))/$total_tools] Installing $tool_name (Priority: $priority)..."

        local install_success=false
        local retry_count=0
        local max_retries=2

        while [ $retry_count -le $max_retries ] && [ "$install_success" = false ]; do
            if [ $retry_count -gt 0 ]; then
                print_warning "Retry $retry_count/$max_retries for $tool_name..."
                sleep 2
            fi

            if timeout 300 go install "$tool_url" 2>/dev/null; then
                if command_exists "$tool_name"; then
                    print_success "$tool_name installed and verified"
                    install_success=true
                    ((success_count++))
                fi
            fi

            ((retry_count++))
        done

        if [ "$install_success" = false ]; then
            failed_tools+=("$tool_name:$priority")
            if [ "$priority" = "critical" ]; then
                print_error "CRITICAL tool $tool_name failed to install!"
            fi
        fi

        sleep 1
    done

    echo
    print_info "Go Tools Installation Summary:"
    print_success "Successfully installed: $success_count/$total_tools tools"

    if [ ${#failed_tools[@]} -gt 0 ]; then
        print_warning "Failed installations: ${#failed_tools[@]} tools"
        for failed in "${failed_tools[@]}"; do
            IFS=':' read -r name priority <<< "$failed"
            print_error "  • $name ($priority priority)"
        done
    fi

    configure_go_path
}

# Install Python-based tools
install_python_tools() {
    print_phase "Installing Python-Based Reconnaissance Tools"

    local python_tools=(
        "sublist3r"
        "dnsrecon"
        "dirsearch"
        "theharvester"
        "sherlock-project"
        "holehe"
        "gitleaks"
        "truffleHog"
    )

    for tool in "${python_tools[@]}"; do
        print_progress "Installing $tool..."
        if pip3 install --user "$tool" 2>/dev/null || pip3 install --break-system-packages "$tool" 2>/dev/null; then
            print_success "$tool installed"
        else
            print_warning "$tool installation failed"
        fi
    done
}

# Install additional tools via package managers
install_additional_tools() {
    print_phase "Installing Additional Reconnaissance Tools"

    if command_exists apt-get; then
        print_progress "Installing additional tools via apt..."
        sudo apt-get install -y nikto dirb wfuzz sqlmap whatweb 2>/dev/null || true
    elif command_exists yum; then
        print_progress "Installing additional tools via yum..."
        sudo yum install -y nikto 2>/dev/null || true
    elif command_exists dnf; then
        print_progress "Installing additional tools via dnf..."
        sudo dnf install -y nikto 2>/dev/null || true
    fi

    # Install Aquatone
    print_progress "Installing Aquatone..."
    if [ ! -f "/usr/local/bin/aquatone" ]; then
        wget -q https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip -O /tmp/aquatone.zip
        unzip -q /tmp/aquatone.zip -d /tmp/
        sudo mv /tmp/aquatone /usr/local/bin/
        sudo chmod +x /usr/local/bin/aquatone
        rm -f /tmp/aquatone.zip
        print_success "Aquatone installed"
    fi

    print_success "Additional tools installation completed"
}

# Configure Go PATH permanently
configure_go_path() {
    print_progress "Configuring Go tools PATH..."

    local shell_rc=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
    elif [[ "$SHELL" == *"fish"* ]]; then
        shell_rc="$HOME/.config/fish/config.fish"
    else
        shell_rc="$HOME/.bashrc"
    fi

    touch "$shell_rc"

    local go_path_added=false
    if ! grep -q "go env GOPATH" "$shell_rc" 2>/dev/null; then
        if [[ "$shell_rc" == *"fish"* ]]; then
            echo 'set -gx PATH $PATH (go env GOPATH)/bin' >> "$shell_rc"
        else
            echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> "$shell_rc"
        fi
        go_path_added=true
    fi

    if ! grep -q "/usr/local/go/bin" "$shell_rc" 2>/dev/null; then
        if [[ "$shell_rc" == *"fish"* ]]; then
            echo 'set -gx PATH $PATH /usr/local/go/bin' >> "$shell_rc"
        else
            echo 'export PATH=$PATH:/usr/local/go/bin' >> "$shell_rc"
        fi
        go_path_added=true
    fi

    if [ "$go_path_added" = true ]; then
        print_success "Go tools added to PATH in $shell_rc"
    fi
}

# Setup wordlists and configurations
setup_wordlists() {
    print_phase "Setting Up Wordlists and Configurations"

    # Create wordlists directory
    mkdir -p ./wordlists

    # Download SecLists
    if [ ! -d "./wordlists/SecLists" ]; then
        print_progress "Downloading SecLists..."
        git clone --depth 1 https://github.com/danielmiessler/SecLists.git ./wordlists/SecLists 2>/dev/null || true
        print_success "SecLists downloaded"
    fi

    # Download common wordlists
    print_progress "Downloading additional wordlists..."
    
    # Subdomain wordlists
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt -O ./wordlists/subdomains-5k.txt 2>/dev/null || true
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/bitquark-subdomains-top100000.txt -O ./wordlists/subdomains-100k.txt 2>/dev/null || true
    
    # Directory wordlists
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O ./wordlists/directories-common.txt 2>/dev/null || true
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/big.txt -O ./wordlists/directories-big.txt 2>/dev/null || true

    print_success "Wordlists setup completed"
}

# Verify installation
verify_installation() {
    print_phase "Verifying Installation"

    local critical_tools=(
        "subfinder" "assetfinder" "httpx" "nuclei" "ffuf" 
        "waybackurls" "gau" "naabu" "massdns" "puredns"
    )

    local installed_count=0
    local total_critical=${#critical_tools[@]}

    for tool in "${critical_tools[@]}"; do
        if command_exists "$tool"; then
            print_success "$tool is available"
            ((installed_count++))
        else
            print_error "$tool is NOT available"
        fi
    done

    echo
    print_info "Installation Verification Summary:"
    print_success "Critical tools installed: $installed_count/$total_critical"

    if [ $installed_count -eq $total_critical ]; then
        print_success "🎉 All critical tools installed successfully!"
        return 0
    else
        print_warning "Some critical tools are missing. Please check the installation log."
        return 1
    fi
}

# Main installation function
main() {
    init_logs
    print_banner

    print_info "Starting K1NGB0B Ultimate Reconnaissance Suite installation..."
    print_info "This will install 30+ world-class bug bounty tools"
    print_info "Installation log: $INSTALL_LOG"
    echo

    # Check if running as root
    if is_root; then
        print_warning "Running as root. Some tools may not work properly."
    fi

    # Installation phases
    install_system_deps || { print_error "System dependencies installation failed"; exit 1; }
    check_and_upgrade_go || { print_error "Go installation failed"; exit 1; }
    install_python_deps || { print_error "Python dependencies installation failed"; exit 1; }
    install_go_tools || { print_warning "Some Go tools installation failed"; }
    install_python_tools || { print_warning "Some Python tools installation failed"; }
    install_additional_tools || { print_warning "Some additional tools installation failed"; }
    setup_wordlists || { print_warning "Wordlists setup failed"; }

    echo
    verify_installation

    echo
    print_success "🎯 K1NGB0B Ultimate Reconnaissance Suite installation completed!"
    print_info "You can now run: python3 k1ngb0b_ultimate_recon.py -d example.com"
    print_info "For help: python3 k1ngb0b_ultimate_recon.py --help"
    print_info "Installation log saved to: $INSTALL_LOG"
    
    echo
    print_info "Please restart your terminal or run: source ~/.bashrc"
}

# Handle Ctrl+C
trap 'echo -e "\n${RED}Installation interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"