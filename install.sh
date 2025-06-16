#!/bin/bash

# K1NGB0B Recon Script - Linux Installation System
# Author: mrx-arafat (K1NGB0B)
# Version: 2.1.0

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Print functions
print_success() { echo -e "${GREEN}✅${NC} $1"; }
print_error() { echo -e "${RED}❌${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠️${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ️${NC} $1"; }
print_step() { echo -e "${CYAN}→${NC} $1"; }
print_progress() { echo -e "${PURPLE}🔄${NC} $1"; }

# Check if command exists
command_exists() { command -v "$1" >/dev/null 2>&1; }

# Check if running as root
is_root() { [ "$EUID" -eq 0 ]; }

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  🎯 K1NGB0B Recon Script - Linux Installation System      ║"
    echo "║  Author: mrx-arafat (K1NGB0B)                              ║"
    echo "║  Version: 2.1.0                                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Detect Linux distribution
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

# Install Go tools
install_go_tools() {
    print_step "Installing reconnaissance tools..."

    # Ensure Go is properly configured
    if ! command_exists go; then
        print_error "Go is not installed or not in PATH!"
        exit 1
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

    # Install tools with progress indicators
    local tools=(
        "github.com/tomnomnom/assetfinder@latest:assetfinder"
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest:subfinder"
        "github.com/projectdiscovery/httpx/cmd/httpx@latest:httpx"
        "github.com/tomnomnom/anew@latest:anew"
        "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest:nuclei"
        "github.com/ffuf/ffuf@latest:ffuf"
        "github.com/tomnomnom/waybackurls@latest:waybackurls"
        "github.com/lc/gau@latest:gau"
        "github.com/sensepost/gowitness@latest:gowitness"
        "github.com/owasp-amass/amass/v4/...@master:amass"
    )

    for tool_info in "${tools[@]}"; do
        local tool_url="${tool_info%:*}"
        local tool_name="${tool_info#*:}"

        print_progress "Installing $tool_name..."
        if go install "$tool_url" 2>/dev/null; then
            print_success "$tool_name installed successfully"
        else
            print_error "Failed to install $tool_name"
            print_info "Retrying with verbose output..."
            go install -v "$tool_url"
        fi
    done

    # Add Go bin to PATH permanently
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

    if ! grep -q "go env GOPATH" "$shell_rc" 2>/dev/null; then
        if [[ "$shell_rc" == *"fish"* ]]; then
            echo 'set -gx PATH $PATH (go env GOPATH)/bin' >> "$shell_rc"
        else
            echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> "$shell_rc"
        fi
        print_info "Added Go tools to PATH in $shell_rc"
    fi

    print_success "All reconnaissance tools installed"
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

# Main installation function
main() {
    print_banner

    # Check if running as root (not recommended)
    if is_root; then
        print_warning "Running as root is not recommended!"
        print_info "Consider running as a regular user for security."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled."
            exit 0
        fi
    fi

    print_info "Checking current system..."

    # Check if already installed
    if missing_deps=$(check_all_dependencies); then
        print_success "All dependencies are already installed!"
        print_info "Running verification to ensure everything works..."
        verify_installation
        echo
        print_info "🎯 You can now run: python3 k1ngb0b_recon.py"
        exit 0
    else
        print_warning "Missing dependencies: $missing_deps"
    fi

    # Check if running on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "This installer is designed for Linux systems only!"
        print_info "Detected OS: $OSTYPE"
        print_info "Please install dependencies manually on your system."
        exit 1
    fi

    # Check for internet connectivity
    print_progress "Checking internet connectivity..."
    if ! ping -c 1 google.com >/dev/null 2>&1 && ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        print_error "No internet connection detected!"
        print_info "Internet access is required to download dependencies."
        exit 1
    fi
    print_success "Internet connectivity OK"

    print_info "Starting installation process..."
    echo

    # Install system dependencies
    install_system_deps
    echo

    # Install Python dependencies
    install_python_deps
    echo

    # Install Go tools
    install_go_tools
    echo

    # Install additional tools and setup
    install_additional_tools
    echo

    # Verify installation
    verify_installation
    echo

    print_success "🎉 Installation completed successfully!"
    echo
    print_info "🎯 Next steps:"
    print_info "1. Restart your terminal or run: source ~/.bashrc"
    print_info "2. Run the tool: python3 k1ngb0b_recon.py"
    print_info "3. Enter a domain when prompted (e.g., example.com)"
    echo
    print_info "📚 Enhanced Tool Capabilities:"
    print_info "🔍 Core Reconnaissance:"
    print_info "  • Multi-source subdomain enumeration (AssetFinder, Subfinder, Amass)"
    print_info "  • Certificate Transparency lookup"
    print_info "  • Smart wordlist-based enumeration with SecLists"
    print_info "  • HTTP probing with technology detection (httpx)"
    print_info "  • DNS analysis and port scanning"
    echo
    print_info "🔥 Advanced Analysis (k1ngb0b_after_recon.py):"
    print_info "  • Vulnerability scanning (Nuclei)"
    print_info "  • Smart directory enumeration (FFUF, Gobuster)"
    print_info "  • API endpoint discovery with context-aware wordlists"
    print_info "  • URL discovery (Waybackurls, GAU)"
    print_info "  • Parameter discovery (ParamSpider)"
    print_info "  • Screenshot capture (Gowitness)"
    echo
    print_info "🧠 Smart Features:"
    print_info "  • SecLists integration - Downloads only needed wordlists"
    print_info "  • Technology-specific testing (WordPress, APIs, etc.)"
    print_info "  • Concurrent processing with rate limiting"
    print_info "  • Comprehensive JSON reporting"
    echo
    print_success "Happy hunting with enhanced intelligence! 🔥🧠"
}

# Trap to handle script interruption
trap 'print_error "Installation interrupted!"; exit 1' INT TERM

# Run main function
main "$@"
