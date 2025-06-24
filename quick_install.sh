#!/bin/bash

# Quick installer for K1NGB0B Domain Discovery tools
# Simplified version for WSL/Linux environments

echo "🔥 K1NGB0B Quick Tool Installer"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅${NC} $1"; }
print_error() { echo -e "${RED}❌${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠️${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ️${NC} $1"; }

# Check if command exists
command_exists() { command -v "$1" >/dev/null 2>&1; }

# Install Go if not present
install_go() {
    if ! command_exists go; then
        print_info "Installing Go..."
        wget -q https://golang.org/dl/go1.23.10.linux-amd64.tar.gz -O /tmp/go.tar.gz
        sudo rm -rf /usr/local/go
        sudo tar -C /usr/local -xzf /tmp/go.tar.gz
        export PATH=$PATH:/usr/local/go/bin
        echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
        print_success "Go installed"
    else
        print_success "Go already installed"
    fi
}

# Install Rust if not present
install_rust() {
    if ! command_exists cargo; then
        print_info "Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env
        export PATH=$PATH:~/.cargo/bin
        echo 'export PATH=$PATH:~/.cargo/bin' >> ~/.bashrc
        print_success "Rust installed"
    else
        print_success "Rust already installed"
    fi
}

# Install Python packages
install_python_deps() {
    print_info "Installing Python dependencies..."
    pip3 install --user aiohttp dnspython psutil requests 2>/dev/null || \
    pip3 install --break-system-packages aiohttp dnspython psutil requests 2>/dev/null || \
    print_warning "Python packages installation failed"
    print_success "Python dependencies installed"
}

# Install Go tools
install_go_tools() {
    print_info "Installing Go reconnaissance tools..."
    
    # Set up Go environment
    export PATH=$PATH:/usr/local/go/bin:$(go env GOPATH)/bin
    
    # Core tools
    tools=(
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        "github.com/tomnomnom/assetfinder@latest"
        "github.com/owasp-amass/amass/v4/cmd/amass@latest"
        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
        "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
        "github.com/projectdiscovery/katana/cmd/katana@latest"
        "github.com/lc/gau/v2/cmd/gau@latest"
        "github.com/tomnomnom/waybackurls@latest"
        "github.com/ffuf/ffuf/v2@latest"
        "github.com/sensepost/gowitness@latest"
    )
    
    for tool in "${tools[@]}"; do
        tool_name=$(basename "$tool" | cut -d'@' -f1)
        print_info "Installing $tool_name..."
        if go install "$tool" 2>/dev/null; then
            print_success "$tool_name installed"
        else
            print_error "$tool_name failed"
        fi
    done
}

# Install RustScan
install_rustscan() {
    print_info "Installing RustScan..."
    if command_exists cargo; then
        if cargo install rustscan 2>/dev/null; then
            print_success "RustScan installed"
        else
            print_error "RustScan installation failed"
        fi
    else
        print_error "Cargo not found - install Rust first"
    fi
}

# Update PATH
update_path() {
    print_info "Updating PATH configuration..."
    
    # Add Go bin to PATH
    if ! grep -q "go env GOPATH" ~/.bashrc 2>/dev/null; then
        echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
    fi
    
    # Add Cargo bin to PATH
    if ! grep -q ".cargo/bin" ~/.bashrc 2>/dev/null; then
        echo 'export PATH=$PATH:~/.cargo/bin' >> ~/.bashrc
    fi
    
    # Export for current session
    export PATH=$PATH:/usr/local/go/bin:$(go env GOPATH 2>/dev/null)/bin:~/.cargo/bin
    
    print_success "PATH updated"
}

# Main installation
main() {
    print_info "Starting quick installation..."
    
    # Update package lists
    if command_exists apt-get; then
        print_info "Updating package lists..."
        sudo apt-get update -qq
        sudo apt-get install -y python3 python3-pip curl wget git
    fi
    
    # Install dependencies
    install_go
    install_rust
    install_python_deps
    
    # Install tools
    install_go_tools
    install_rustscan
    
    # Update PATH
    update_path
    
    print_success "Quick installation completed!"
    print_info "Please run: source ~/.bashrc"
    print_info "Or restart your terminal to apply PATH changes"
    
    echo ""
    print_info "Test the installation:"
    print_info "python3 domain_discovery.py --help"
}

# Run main function
main "$@"
