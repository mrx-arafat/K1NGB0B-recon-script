#!/bin/bash

# K1NGB0B Recon Script - Linux Installation System
# Author: mrx-arafat
# Version: 2.0.0

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print functions
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_step() { echo -e "${BLUE}→${NC} $1"; }

# Check if command exists
command_exists() { command -v "$1" >/dev/null 2>&1; }

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  🎯 K1NGB0B Recon Script - Linux Installation System      ║"
    echo "║  Author: mrx-arafat (K1NGB0B)                              ║"
    echo "║  Version: 2.0.0                                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
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
    
    # Check reconnaissance tools
    for tool in assetfinder subfinder httpx anew; do
        if ! command_exists "$tool"; then
            missing+=("$tool")
        fi
    done
    
    # Check Python package
    if command_exists python3; then
        if ! python3 -c "import aiohttp" 2>/dev/null; then
            missing+=("aiohttp")
        fi
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
    
    if command_exists apt-get; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip curl wget git golang-go
    elif command_exists yum; then
        sudo yum install -y python3 python3-pip curl wget git golang
    elif command_exists dnf; then
        sudo dnf install -y python3 python3-pip curl wget git golang
    elif command_exists pacman; then
        sudo pacman -Sy --noconfirm python python-pip curl wget git go
    else
        print_error "Unsupported package manager. Please install manually:"
        print_info "- python3, python3-pip, curl, wget, git, golang"
        exit 1
    fi
}

# Install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    if command_exists pip3; then
        pip3 install aiohttp
    elif command_exists pip; then
        pip install aiohttp
    else
        print_error "pip not found!"
        exit 1
    fi
}

# Install Go tools
install_go_tools() {
    print_step "Installing reconnaissance tools..."
    
    # Ensure Go is properly configured
    export PATH=$PATH:/usr/local/go/bin:$(go env GOPATH)/bin
    
    # Install tools
    go install github.com/tomnomnom/assetfinder@latest
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest
    go install github.com/tomnomnom/anew@latest
    
    # Add Go bin to PATH permanently
    local shell_rc=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.bashrc"
    fi
    
    if ! grep -q "go env GOPATH" "$shell_rc" 2>/dev/null; then
        echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> "$shell_rc"
        print_info "Added Go tools to PATH in $shell_rc"
    fi
}

# Verify installation
verify_installation() {
    print_step "Verifying installation..."
    
    local failed=false
    
    # Check Python
    if ! python3 -c "import aiohttp" 2>/dev/null; then
        print_error "Python aiohttp package not found"
        failed=true
    else
        print_success "Python dependencies OK"
    fi
    
    # Check Go tools
    for tool in assetfinder subfinder httpx anew; do
        if ! command_exists "$tool"; then
            print_error "$tool not found in PATH"
            failed=true
        else
            print_success "$tool OK"
        fi
    done
    
    if [ "$failed" = true ]; then
        print_error "Installation verification failed!"
        print_info "You may need to restart your terminal or run: source ~/.bashrc"
        exit 1
    fi
}

# Main installation function
main() {
    print_banner
    
    print_info "Checking current system..."
    
    # Check if already installed
    if missing_deps=$(check_all_dependencies); then
        print_success "All dependencies are already installed!"
        print_info "You can now run: python3 k1ngb0b_recon.py"
        exit 0
    else
        print_warning "Missing dependencies: $missing_deps"
    fi
    
    # Check if running on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "This installer is designed for Linux systems only!"
        print_info "Please install dependencies manually on your system."
        exit 1
    fi
    
    print_info "Starting installation process..."
    
    # Install system dependencies
    install_system_deps
    
    # Install Python dependencies
    install_python_deps
    
    # Install Go tools
    install_go_tools
    
    # Verify installation
    verify_installation
    
    print_success "Installation completed successfully!"
    echo
    print_info "🎯 Next steps:"
    print_info "1. Restart your terminal or run: source ~/.bashrc"
    print_info "2. Run the tool: python3 k1ngb0b_recon.py"
    print_info "3. Enter a domain when prompted"
    echo
    print_success "Happy hunting! 🔥"
}

# Run main function
main "$@"
