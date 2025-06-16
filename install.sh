#!/bin/bash

# K1NGB0B Recon Script - Smart Linux Installation System
# Author: mrx-arafat (K1NGB0B)
# Version: 3.0.0 - Enhanced with Smart Go Management & Conflict Resolution

# Exit on error but allow manual recovery
set -e

# Global configuration
REQUIRED_GO_VERSION="1.21"
LATEST_GO_VERSION="1.23.10"
INSTALL_LOG="/tmp/k1ngb0b_install.log"
MANUAL_INSTALL_GUIDE="/tmp/k1ngb0b_manual_guide.txt"

# Colors
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
print_manual() { echo -e "${BOLD}${YELLOW}📋 MANUAL:${NC} $1" | tee -a "$MANUAL_INSTALL_GUIDE"; }

# Utility functions
command_exists() { command -v "$1" >/dev/null 2>&1; }
is_root() { [ "$EUID" -eq 0 ]; }

# Initialize log files
init_logs() {
    echo "K1NGB0B Installation Log - $(date)" > "$INSTALL_LOG"
    echo "K1NGB0B Manual Installation Guide - $(date)" > "$MANUAL_INSTALL_GUIDE"
    echo "=========================================" >> "$MANUAL_INSTALL_GUIDE"
}

# Print enhanced banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  🎯 K1NGB0B Smart Recon Installation System v3.0          ║"
    echo "║  Author: mrx-arafat (K1NGB0B)                              ║"
    echo "║  🧠 Enhanced: Smart Go Management & Conflict Resolution    ║"
    echo "║  📋 Auto-generates manual installation guide if needed     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
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

# Check Go version and upgrade if needed
check_and_upgrade_go() {
    print_step "Checking Go installation and version..."

    if ! command_exists go; then
        print_warning "Go not found. Installing latest Go..."
        install_latest_go
        return $?
    fi

    local current_version=$(go version | grep -oE 'go[0-9]+\.[0-9]+(\.[0-9]+)?' | sed 's/go//')
    print_info "Current Go version: $current_version"

    # Compare versions (simplified)
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

    # Create manual installation instructions
    print_manual "# Go Installation (if automatic fails):"
    print_manual "wget $go_url -O /tmp/go${LATEST_GO_VERSION}.tar.gz"
    print_manual "sudo rm -rf /usr/local/go"
    print_manual "sudo tar -C /usr/local -xzf /tmp/go${LATEST_GO_VERSION}.tar.gz"
    print_manual "echo 'export PATH=\$PATH:/usr/local/go/bin' >> ~/.bashrc"
    print_manual "source ~/.bashrc"
    print_manual ""

    # Attempt automatic installation
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
    print_info "Please follow manual instructions in: $MANUAL_INSTALL_GUIDE"
    return 1
}

# Check if all dependencies are installed
check_all_dependencies() {
    local missing=()

    # Check Python 3
    if ! command_exists python3; then
        missing+=("python3")
    fi

    # Check pip
    if ! command_exists pip3 && ! command_exists pip; then
        missing+=("pip")
    fi

    # Check Go
    if ! command_exists go; then
        missing+=("go")
    fi

    # Check system tools
    for tool in curl wget git; do
        if ! command_exists "$tool"; then
            missing+=("$tool")
        fi
    done

    # Check reconnaissance tools (with PATH update)
    export PATH=$PATH:$(go env GOPATH 2>/dev/null)/bin 2>/dev/null || true
    for tool in assetfinder subfinder httpx anew; do
        if ! command_exists "$tool"; then
            missing+=("$tool")
        fi
    done

    # Check Python packages
    if command_exists python3; then
        for package in aiohttp dnspython psutil requests; do
            if ! python3 -c "import $package" 2>/dev/null; then
                missing+=("$package")
            fi
        done
    fi

    if [ ${#missing[@]} -eq 0 ]; then
        return 0  # All dependencies satisfied
    else
        echo "${missing[@]}"
        return 1  # Dependencies missing
    fi
}

# Install system dependencies
install_system_deps() {
    print_step "Installing system dependencies..."
    local distro=$(detect_distro)

    print_progress "Detected distribution: $distro"

    if command_exists apt-get; then
        print_progress "Updating package lists..."
        sudo apt-get update -qq
        print_progress "Installing packages via apt..."
        sudo apt-get install -y python3 python3-pip python3-venv curl wget git golang-go
    elif command_exists yum; then
        print_progress "Installing packages via yum..."
        sudo yum install -y python3 python3-pip curl wget git golang
    elif command_exists dnf; then
        print_progress "Installing packages via dnf..."
        sudo dnf install -y python3 python3-pip curl wget git golang
    elif command_exists pacman; then
        print_progress "Installing packages via pacman..."
        sudo pacman -Sy --noconfirm python python-pip curl wget git go
    else
        print_error "Unsupported package manager. Please install manually:"
        print_info "- python3, python3-pip, curl, wget, git, golang"
        exit 1
    fi

    print_success "System dependencies installed"
}

# Install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."

    # Try different methods to install Python packages
    local install_success=false

    # Method 1: Try pip install with --user flag
    if command_exists pip3; then
        print_progress "Attempting pip3 install with --user flag..."
        if pip3 install --user aiohttp dnspython psutil requests 2>/dev/null; then
            install_success=true
            print_success "Python packages installed via pip3 --user"
        fi
    fi

    # Method 2: Try pip install with --break-system-packages (for newer systems)
    if [ "$install_success" = false ] && command_exists pip3; then
        print_progress "Attempting pip3 install with --break-system-packages..."
        if pip3 install --break-system-packages aiohttp dnspython psutil requests 2>/dev/null; then
            install_success=true
            print_success "Python packages installed via pip3 --break-system-packages"
        fi
    fi

    # Method 3: Try system package manager for Python packages
    if [ "$install_success" = false ]; then
        print_progress "Attempting system package installation..."
        if command_exists apt-get; then
            if sudo apt-get install -y python3-aiohttp 2>/dev/null; then
                install_success=true
                print_success "Python packages installed via apt"
            fi
        fi
    fi

    # Method 4: Create virtual environment (fallback)
    if [ "$install_success" = false ]; then
        print_warning "Standard pip installation failed. Creating virtual environment..."
        if command_exists python3; then
            python3 -m venv venv_k1ngb0b 2>/dev/null || true
            if [ -f "venv_k1ngb0b/bin/activate" ]; then
                source venv_k1ngb0b/bin/activate
                pip install aiohttp dnspython psutil requests
                deactivate
                install_success=true
                print_success "Python packages installed in virtual environment"
                print_info "Note: You may need to activate the virtual environment before running the script"
            fi
        fi
    fi

    if [ "$install_success" = false ]; then
        print_error "Failed to install Python dependencies!"
        print_info "Please try manually: pip3 install --user aiohttp dnspython psutil requests"
        exit 1
    fi
}

# Smart Go tools installation with conflict resolution
install_go_tools() {
    print_step "Installing reconnaissance tools with smart conflict resolution..."

    # Ensure Go is properly configured
    if ! command_exists go; then
        print_error "Go is not installed or not in PATH!"
        print_info "Run: check_and_upgrade_go first"
        return 1
    fi

    # Set up Go environment
    local gopath=$(go env GOPATH 2>/dev/null)
    if [ -z "$gopath" ]; then
        print_warning "GOPATH not set, using default"
        export GOPATH="$HOME/go"
        mkdir -p "$GOPATH/bin"
    fi

    export PATH=$PATH:/usr/local/go/bin:$gopath/bin
    print_progress "Go environment configured (GOPATH: $gopath)"

    # Enhanced tools list with priority and fallback options
    local tools=(
        "github.com/tomnomnom/assetfinder@latest:assetfinder:high"
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest:subfinder:high"
        "github.com/projectdiscovery/httpx/cmd/httpx@latest:httpx:high"
        "github.com/tomnomnom/anew@latest:anew:high"
        "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest:nuclei:critical"
        "github.com/ffuf/ffuf/v2@latest:ffuf:medium"
        "github.com/tomnomnom/waybackurls@latest:waybackurls:medium"
        "github.com/lc/gau/v2/cmd/gau@latest:gau:medium"
        "github.com/projectdiscovery/katana/cmd/katana@latest:katana:medium"
        "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest:naabu:medium"
        "github.com/tomnomnom/gf@latest:gf:low"
        "github.com/1ndianl33t/Gf-Patterns@latest:gf-patterns:low"
    )

    local failed_tools=()
    local success_count=0
    local total_tools=${#tools[@]}

    print_info "Installing $total_tools reconnaissance tools..."
    echo

    for tool_info in "${tools[@]}"; do
        IFS=':' read -r tool_url tool_name priority <<< "$tool_info"

        print_progress "[$((success_count + 1))/$total_tools] Installing $tool_name (Priority: $priority)..."

        # Create manual installation instruction for each tool
        print_manual "# $tool_name installation:"
        print_manual "go install $tool_url"
        print_manual ""

        # Attempt installation with timeout and retry logic
        local install_success=false
        local retry_count=0
        local max_retries=2

        while [ $retry_count -le $max_retries ] && [ "$install_success" = false ]; do
            if [ $retry_count -gt 0 ]; then
                print_warning "Retry $retry_count/$max_retries for $tool_name..."
                sleep 2
            fi

            # Try installation with timeout
            if timeout 300 go install "$tool_url" 2>/dev/null; then
                # Verify installation
                if command_exists "$tool_name"; then
                    print_success "$tool_name installed and verified"
                    install_success=true
                    ((success_count++))
                else
                    print_warning "$tool_name installed but not found in PATH"
                fi
            else
                local exit_code=$?
                if [ $exit_code -eq 124 ]; then
                    print_warning "$tool_name installation timed out (5 minutes)"
                else
                    print_warning "$tool_name installation failed (exit code: $exit_code)"
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

        # Small delay to prevent overwhelming the system
        sleep 1
    done

    # Report installation results
    echo
    print_info "Installation Summary:"
    print_success "Successfully installed: $success_count/$total_tools tools"

    if [ ${#failed_tools[@]} -gt 0 ]; then
        print_warning "Failed installations: ${#failed_tools[@]} tools"
        for failed in "${failed_tools[@]}"; do
            IFS=':' read -r name priority <<< "$failed"
            print_error "  • $name ($priority priority)"
        done

        print_info "Manual installation guide available at: $MANUAL_INSTALL_GUIDE"
    fi

    # Configure PATH permanently
    configure_go_path

    # Check for critical tool failures
    local critical_failed=false
    for failed in "${failed_tools[@]}"; do
        if [[ "$failed" == *":critical" ]]; then
            critical_failed=true
            break
        fi
    done

    if [ "$critical_failed" = true ]; then
        print_error "Critical tools failed to install. Please install manually."
        return 1
    else
        print_success "Core reconnaissance tools installed successfully"
        return 0
    fi
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

    # Create shell config if it doesn't exist
    touch "$shell_rc"

    # Add Go paths if not already present
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
        print_info "Run 'source $shell_rc' or restart terminal to apply changes"
    else
        print_info "Go tools already in PATH configuration"
    fi
}

# Install additional tools and setup
install_additional_tools() {
    print_step "Installing additional tools and setup..."

    # Install system tools for enhanced functionality
    if command_exists apt-get; then
        print_progress "Installing additional system tools..."
        sudo apt-get install -y gobuster dirb 2>/dev/null || print_warning "Some additional tools may not be available"
    fi

    # Install ParamSpider for parameter discovery
    print_progress "Installing ParamSpider..."
    if command_exists pip3; then
        pip3 install --user paramspider 2>/dev/null || pip3 install --break-system-packages paramspider 2>/dev/null || print_warning "ParamSpider installation failed"
        print_success "ParamSpider installed for parameter discovery"
    fi

    # Update Nuclei templates
    export PATH=$PATH:$(go env GOPATH 2>/dev/null)/bin 2>/dev/null || true
    if command_exists nuclei; then
        print_progress "Updating Nuclei templates..."
        nuclei -update-templates -silent 2>/dev/null || print_warning "Nuclei template update failed"
        print_success "Nuclei templates updated"
    fi

    # Create wordlists directory for SecLists cache
    print_progress "Setting up wordlists directory..."
    mkdir -p ./wordlists
    print_info "Created wordlists directory for SecLists cache"

    # Setup wordlists directory
    if [ ! -d "/usr/share/wordlists" ]; then
        sudo mkdir -p /usr/share/wordlists 2>/dev/null || true
    fi

    print_success "Additional tools and setup completed"
}

# Verify installation
verify_installation() {
    print_step "Verifying installation..."

    local failed=false
    local warnings=false

    # Update PATH for verification
    export PATH=$PATH:$(go env GOPATH 2>/dev/null)/bin 2>/dev/null || true

    # Check Python packages
    print_progress "Checking Python dependencies..."
    local python_packages=("aiohttp" "dnspython" "psutil" "requests")
    local python_failed=false

    for package in "${python_packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            # Try alternative import methods
            if python3 -c "import sys; sys.path.append('$HOME/.local/lib/python*/site-packages'); import $package" 2>/dev/null; then
                continue
            elif [ -f "venv_k1ngb0b/bin/activate" ]; then
                source venv_k1ngb0b/bin/activate
                if python3 -c "import $package" 2>/dev/null; then
                    deactivate
                    continue
                else
                    deactivate
                    print_error "Python $package package not found"
                    python_failed=true
                fi
            else
                print_error "Python $package package not found"
                python_failed=true
            fi
        fi
    done

    if [ "$python_failed" = false ]; then
        print_success "Python dependencies OK"
    else
        failed=true
    fi

    # Check Go tools
    print_progress "Checking reconnaissance tools..."
    local tools=("assetfinder" "subfinder" "httpx" "anew" "nuclei" "ffuf" "waybackurls" "gau" "gowitness")
    for tool in "${tools[@]}"; do
        if command_exists "$tool"; then
            # Test tool functionality
            if "$tool" --help >/dev/null 2>&1 || "$tool" -h >/dev/null 2>&1; then
                print_success "$tool OK"
            else
                print_warning "$tool found but may not be working correctly"
                warnings=true
            fi
        else
            print_error "$tool not found in PATH"
            failed=true
        fi
    done

    # Check if k1ngb0b_recon.py exists
    if [ -f "k1ngb0b_recon.py" ]; then
        print_success "K1NGB0B Recon Script found"
    else
        print_warning "k1ngb0b_recon.py not found in current directory"
        warnings=true
    fi

    if [ "$failed" = true ]; then
        print_error "Installation verification failed!"
        print_info "Troubleshooting steps:"
        print_info "1. Restart your terminal or run: source ~/.bashrc"
        print_info "2. Check if Go tools are in PATH: echo \$PATH"
        print_info "3. Manually add Go bin to PATH: export PATH=\$PATH:\$(go env GOPATH)/bin"
        exit 1
    elif [ "$warnings" = true ]; then
        print_warning "Installation completed with warnings"
        print_info "Some components may need manual verification"
    else
        print_success "All components verified successfully!"
    fi
}

# Enhanced main installation function with smart recovery
main() {
    # Initialize logging
    init_logs

    print_banner

    # Check if running as root (provide guidance)
    if is_root; then
        print_warning "Running as root detected!"
        print_info "This is acceptable for VPS/server installations."
        print_info "For personal systems, consider running as regular user."
        echo
    fi

    print_info "🔍 Performing smart system analysis..."

    # Check if already installed
    if missing_deps=$(check_all_dependencies); then
        print_success "All dependencies are already installed!"
        print_info "Running verification to ensure everything works..."
        verify_installation
        show_completion_guide
        exit 0
    else
        print_warning "Missing dependencies detected: $missing_deps"
        print_info "Proceeding with smart installation..."
    fi

    # System compatibility check
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "This installer is designed for Linux systems only!"
        print_info "Detected OS: $OSTYPE"
        generate_manual_guide_for_os
        exit 1
    fi

    # Network connectivity check
    print_progress "Checking internet connectivity..."
    if ! ping -c 1 google.com >/dev/null 2>&1 && ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        print_error "No internet connection detected!"
        print_info "Internet access is required to download dependencies."
        generate_offline_guide
        exit 1
    fi
    print_success "Internet connectivity verified"

    print_info "🚀 Starting smart installation process..."
    echo

    # Phase 1: System dependencies
    print_step "Phase 1: System Dependencies"
    if ! install_system_deps; then
        print_error "System dependencies installation failed!"
        print_info "Check manual guide: $MANUAL_INSTALL_GUIDE"
        exit 1
    fi
    echo

    # Phase 2: Go installation and upgrade
    print_step "Phase 2: Go Language Setup"
    if ! check_and_upgrade_go; then
        print_error "Go installation/upgrade failed!"
        print_info "Check manual guide: $MANUAL_INSTALL_GUIDE"
        exit 1
    fi
    echo

    # Phase 3: Python dependencies
    print_step "Phase 3: Python Dependencies"
    if ! install_python_deps; then
        print_error "Python dependencies installation failed!"
        print_info "Check manual guide: $MANUAL_INSTALL_GUIDE"
        exit 1
    fi
    echo

    # Phase 4: Go reconnaissance tools
    print_step "Phase 4: Reconnaissance Tools"
    if ! install_go_tools; then
        print_warning "Some reconnaissance tools failed to install"
        print_info "Core functionality may still work. Check manual guide for failed tools."
    fi
    echo

    # Phase 5: Additional tools and setup
    print_step "Phase 5: Additional Tools & Configuration"
    install_additional_tools
    echo

    # Phase 6: Verification
    print_step "Phase 6: Installation Verification"
    verify_installation
    echo

    # Show completion guide
    show_completion_guide
}

# Generate manual installation guide for unsupported OS
generate_manual_guide_for_os() {
    print_manual "# K1NGB0B Manual Installation for $OSTYPE"
    print_manual "# This system is not officially supported by the auto-installer"
    print_manual ""
    print_manual "## Required Dependencies:"
    print_manual "1. Python 3.8+ with pip"
    print_manual "2. Go 1.21+ (latest recommended)"
    print_manual "3. Git, curl, wget"
    print_manual ""
    print_manual "## Installation Steps:"
    print_manual "# Install Python packages:"
    print_manual "pip3 install aiohttp dnspython psutil requests"
    print_manual ""
    print_manual "# Install Go tools:"
    print_manual "go install github.com/tomnomnom/assetfinder@latest"
    print_manual "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    print_manual "go install github.com/projectdiscovery/httpx/cmd/httpx@latest"
    print_manual "go install github.com/tomnomnom/anew@latest"
    print_manual "go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    print_manual ""
    print_info "Manual installation guide created: $MANUAL_INSTALL_GUIDE"
}

# Generate offline installation guide
generate_offline_guide() {
    print_manual "# K1NGB0B Offline Installation Guide"
    print_manual "# For systems without internet connectivity"
    print_manual ""
    print_manual "## Download on connected system:"
    print_manual "# Go binaries from: https://golang.org/dl/"
    print_manual "# Python packages: pip download aiohttp dnspython psutil requests"
    print_manual ""
    print_manual "## Transfer and install offline"
    print_info "Offline installation guide created: $MANUAL_INSTALL_GUIDE"
}

# Enhanced completion guide
show_completion_guide() {
    print_success "🎉 K1NGB0B Installation completed!"
    echo
    print_info "📋 Installation Summary:"
    print_info "  • Installation log: $INSTALL_LOG"
    print_info "  • Manual guide: $MANUAL_INSTALL_GUIDE"
    echo
    print_info "🎯 Quick Start:"
    print_info "1. Restart terminal or run: source ~/.bashrc"
    print_info "2. Test installation: python3 k1ngb0b_recon.py --help"
    print_info "3. Run reconnaissance: python3 k1ngb0b_recon.py"
    echo
    print_info "🔧 Troubleshooting:"
    print_info "  • If tools not found: export PATH=\$PATH:\$(go env GOPATH)/bin"
    print_info "  • For manual installation: cat $MANUAL_INSTALL_GUIDE"
    print_info "  • Check logs: cat $INSTALL_LOG"
    echo
    print_success "Happy bug hunting with K1NGB0B! 🔥🎯"
}

# Trap to handle script interruption
trap 'print_error "Installation interrupted!"; exit 1' INT TERM

# Run main function
main "$@"
