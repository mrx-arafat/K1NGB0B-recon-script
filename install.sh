#!/bin/bash

# K1NGB0B Recon Script - One-Click Installation
# Author: mrx-arafat

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Go if not present
install_go() {
    if ! command_exists go; then
        print_status "Go not found. Installing Go..."
        
        # Detect OS and architecture
        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        
        case $ARCH in
            x86_64) ARCH="amd64" ;;
            aarch64) ARCH="arm64" ;;
            armv6l) ARCH="armv6l" ;;
            armv7l) ARCH="armv6l" ;;
            *) print_error "Unsupported architecture: $ARCH"; exit 1 ;;
        esac
        
        GO_VERSION="1.21.5"
        GO_TARBALL="go${GO_VERSION}.${OS}-${ARCH}.tar.gz"
        GO_URL="https://golang.org/dl/${GO_TARBALL}"
        
        # Download and install Go
        wget -q "$GO_URL" -O "/tmp/${GO_TARBALL}"
        sudo tar -C /usr/local -xzf "/tmp/${GO_TARBALL}"
        
        # Add Go to PATH
        echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
        echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
        export PATH=$PATH:/usr/local/go/bin
        export PATH=$PATH:$(go env GOPATH)/bin
        
        rm "/tmp/${GO_TARBALL}"
        print_success "Go installed successfully"
    else
        print_success "Go is already installed"
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Check if pip is available
    if ! command_exists pip && ! command_exists pip3; then
        print_error "pip not found. Please install Python and pip first."
        exit 1
    fi
    
    # Use pip3 if available, otherwise pip
    PIP_CMD="pip"
    if command_exists pip3; then
        PIP_CMD="pip3"
    fi
    
    # Install dependencies
    $PIP_CMD install -r requirements.txt
    print_success "Python dependencies installed"
}

# Function to install Go tools
install_go_tools() {
    print_status "Installing Go-based reconnaissance tools..."
    
    # Ensure GOPATH/bin is in PATH
    export PATH=$PATH:$(go env GOPATH)/bin
    
    # Install tools
    print_status "Installing assetfinder..."
    go install github.com/tomnomnom/assetfinder@latest
    
    print_status "Installing subfinder..."
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    
    print_status "Installing httpx..."
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest
    
    print_status "Installing anew..."
    go install github.com/tomnomnom/anew@latest
    
    print_success "Go tools installed successfully"
}

# Function to setup project structure
setup_project() {
    print_status "Setting up project structure..."
    
    # Create necessary directories
    mkdir -p src/k1ngb0b_recon
    mkdir -p scripts
    mkdir -p tests
    mkdir -p config
    mkdir -p templates
    
    # Make scripts executable
    chmod +x scripts/*.sh 2>/dev/null || true
    
    print_success "Project structure created"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check Python dependencies
    python3 -c "import click, requests, aiohttp, yaml, tqdm, colorama" 2>/dev/null || {
        print_error "Python dependencies verification failed"
        exit 1
    }
    
    # Check Go tools
    for tool in assetfinder subfinder httpx anew; do
        if ! command_exists "$tool"; then
            print_error "$tool not found in PATH"
            exit 1
        fi
    done
    
    print_success "All tools verified successfully"
}

# Main installation function
main() {
    echo "=================================================="
    echo "  K1NGB0B Recon Script - Installation Script"
    echo "  Author: mrx-arafat"
    echo "=================================================="
    echo
    
    # Check if running as root (not recommended)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root is not recommended"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Update package lists (for apt-based systems)
    if command_exists apt-get; then
        print_status "Updating package lists..."
        sudo apt-get update -qq
    fi
    
    # Install system dependencies
    print_status "Installing system dependencies..."
    if command_exists apt-get; then
        sudo apt-get install -y curl wget git python3 python3-pip
    elif command_exists yum; then
        sudo yum install -y curl wget git python3 python3-pip
    elif command_exists brew; then
        brew install curl wget git python3
    else
        print_warning "Package manager not detected. Please ensure curl, wget, git, and python3 are installed."
    fi
    
    # Install Go
    install_go
    
    # Install Python dependencies
    install_python_deps
    
    # Install Go tools
    install_go_tools
    
    # Setup project structure
    setup_project
    
    # Verify installation
    verify_installation
    
    echo
    print_success "Installation completed successfully!"
    echo
    echo "=================================================="
    echo "  Usage:"
    echo "  python3 -m k1ngb0b_recon <target_domain>"
    echo "=================================================="
    echo
    print_status "Please restart your terminal or run 'source ~/.bashrc' to update PATH"
}

# Run main function
main "$@"
