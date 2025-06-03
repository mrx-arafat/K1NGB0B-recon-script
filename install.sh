#!/bin/bash

# K1NGB0B Recon Script - Intelligent Installation System
# Author: mrx-arafat
# Version: 2.0.0
# Description: Comprehensive, cross-platform installer with automatic dependency detection

set -e  # Exit on any error

# Script configuration
SCRIPT_VERSION="2.0.0"
SCRIPT_NAME="K1NGB0B Recon Script Installer"
MIN_PYTHON_VERSION="3.8"
MIN_GO_VERSION="1.19"
INSTALL_LOG="/tmp/k1ngb0b_install.log"

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'
DIM='\033[2m'

# Unicode symbols for better UX
CHECK_MARK="✓"
CROSS_MARK="✗"
ARROW="→"
GEAR="⚙"
DOWNLOAD="⬇"
INSTALL="📦"
TEST="🧪"

# Global variables
DETECTED_OS=""
DETECTED_ARCH=""
PACKAGE_MANAGER=""
PYTHON_CMD=""
PIP_CMD=""
GO_INSTALLED=false
PYTHON_INSTALLED=false
DEPENDENCIES_MISSING=()
TOOLS_MISSING=()
INSTALL_SUMMARY=()

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$INSTALL_LOG"
}

# Enhanced output functions with logging
print_header() {
    echo -e "\n${BOLD}${BLUE}$1${NC}"
    log "HEADER: $1"
}

print_status() {
    echo -e "${BLUE}${GEAR} ${NC}$1"
    log "STATUS: $1"
}

print_success() {
    echo -e "${GREEN}${CHECK_MARK} ${NC}$1"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${NC}$1"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} ${NC}$1"
    log "ERROR: $1"
}

print_info() {
    echo -e "${CYAN}ℹ ${NC}$1"
    log "INFO: $1"
}

print_step() {
    echo -e "${PURPLE}${ARROW} ${NC}$1"
    log "STEP: $1"
}

# Progress bar function
show_progress() {
    local duration=$1
    local message=$2
    local progress=0
    local bar_length=30

    echo -ne "${message}: ["
    while [ $progress -le $bar_length ]; do
        echo -ne "="
        progress=$((progress + 1))
        sleep $(echo "scale=2; $duration / $bar_length" | bc -l 2>/dev/null || echo "0.1")
    done
    echo -e "] ${GREEN}Done${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare version numbers
version_compare() {
    local version1=$1
    local version2=$2

    if [[ "$version1" == "$version2" ]]; then
        return 0
    fi

    local IFS=.
    local i ver1=($version1) ver2=($version2)

    # Fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done

    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

# System detection function
detect_system() {
    print_header "🔍 System Detection"

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        DETECTED_OS="linux"
        print_success "Detected OS: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        DETECTED_OS="macos"
        print_success "Detected OS: macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        DETECTED_OS="windows"
        print_success "Detected OS: Windows (WSL/Cygwin)"
    else
        print_warning "Unknown OS: $OSTYPE, assuming Linux"
        DETECTED_OS="linux"
    fi

    # Detect architecture
    DETECTED_ARCH=$(uname -m)
    case $DETECTED_ARCH in
        x86_64) DETECTED_ARCH="amd64" ;;
        aarch64) DETECTED_ARCH="arm64" ;;
        armv6l) DETECTED_ARCH="armv6l" ;;
        armv7l) DETECTED_ARCH="armv6l" ;;
        i386) DETECTED_ARCH="386" ;;
        *) print_warning "Unknown architecture: $DETECTED_ARCH" ;;
    esac
    print_success "Detected Architecture: $DETECTED_ARCH"

    # Detect package manager
    if command_exists apt-get; then
        PACKAGE_MANAGER="apt"
        print_success "Package Manager: APT (Debian/Ubuntu)"
    elif command_exists yum; then
        PACKAGE_MANAGER="yum"
        print_success "Package Manager: YUM (RHEL/CentOS)"
    elif command_exists dnf; then
        PACKAGE_MANAGER="dnf"
        print_success "Package Manager: DNF (Fedora)"
    elif command_exists brew; then
        PACKAGE_MANAGER="brew"
        print_success "Package Manager: Homebrew (macOS)"
    elif command_exists pacman; then
        PACKAGE_MANAGER="pacman"
        print_success "Package Manager: Pacman (Arch Linux)"
    else
        print_warning "No supported package manager found"
        PACKAGE_MANAGER="manual"
    fi

    log "System detected: OS=$DETECTED_OS, ARCH=$DETECTED_ARCH, PKG_MGR=$PACKAGE_MANAGER"
}

# Comprehensive dependency checking
check_dependencies() {
    print_header "🔍 Dependency Analysis"

    # Check Python
    check_python

    # Check Go
    check_go

    # Check system tools
    check_system_tools

    # Check Go-based reconnaissance tools
    check_recon_tools

    # Summary of missing dependencies
    if [ ${#DEPENDENCIES_MISSING[@]} -eq 0 ] && [ ${#TOOLS_MISSING[@]} -eq 0 ]; then
        print_success "All dependencies are satisfied!"
        return 0
    else
        print_warning "Missing dependencies detected:"
        for dep in "${DEPENDENCIES_MISSING[@]}"; do
            echo -e "  ${RED}${CROSS_MARK}${NC} $dep"
        done
        for tool in "${TOOLS_MISSING[@]}"; do
            echo -e "  ${RED}${CROSS_MARK}${NC} $tool"
        done
        return 1
    fi
}

# Check Python installation and version
check_python() {
    print_step "Checking Python installation..."

    # Try different Python commands
    for cmd in python3 python python3.11 python3.10 python3.9 python3.8; do
        if command_exists "$cmd"; then
            local version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            if [[ -n "$version" ]]; then
                version_compare "$version" "$MIN_PYTHON_VERSION"
                local result=$?
                if [[ $result -eq 0 ]] || [[ $result -eq 1 ]]; then
                    PYTHON_CMD="$cmd"
                    PYTHON_INSTALLED=true
                    print_success "Python $version found ($cmd)"
                    break
                else
                    print_warning "Python $version is too old (minimum: $MIN_PYTHON_VERSION)"
                fi
            fi
        fi
    done

    if [[ "$PYTHON_INSTALLED" == false ]]; then
        print_error "Python $MIN_PYTHON_VERSION+ not found"
        DEPENDENCIES_MISSING+=("python3")
        return 1
    fi

    # Check pip
    for pip_cmd in pip3 pip; do
        if command_exists "$pip_cmd"; then
            # Verify pip works with our Python
            if $pip_cmd --version >/dev/null 2>&1; then
                PIP_CMD="$pip_cmd"
                print_success "pip found ($pip_cmd)"
                break
            fi
        fi
    done

    if [[ -z "$PIP_CMD" ]]; then
        print_error "pip not found"
        DEPENDENCIES_MISSING+=("python3-pip")
        return 1
    fi

    return 0
}

# Check Go installation and version
check_go() {
    print_step "Checking Go installation..."

    if command_exists go; then
        local version=$(go version 2>&1 | grep -oE 'go[0-9]+\.[0-9]+(\.[0-9]+)?' | sed 's/go//')
        if [[ -n "$version" ]]; then
            version_compare "$version" "$MIN_GO_VERSION"
            local result=$?
            if [[ $result -eq 0 ]] || [[ $result -eq 1 ]]; then
                GO_INSTALLED=true
                print_success "Go $version found"

                # Check GOPATH and GOBIN
                local gopath=$(go env GOPATH 2>/dev/null)
                local gobin=$(go env GOBIN 2>/dev/null)
                if [[ -n "$gopath" ]]; then
                    print_info "GOPATH: $gopath"
                    if [[ -z "$gobin" ]]; then
                        gobin="$gopath/bin"
                    fi
                    print_info "Go binaries will be installed to: $gobin"

                    # Check if Go bin is in PATH
                    if [[ ":$PATH:" != *":$gobin:"* ]]; then
                        print_warning "Go bin directory not in PATH: $gobin"
                        print_info "You may need to add it to your PATH after installation"
                    fi
                fi
                return 0
            else
                print_warning "Go $version is too old (minimum: $MIN_GO_VERSION)"
            fi
        fi
    fi

    print_error "Go $MIN_GO_VERSION+ not found"
    DEPENDENCIES_MISSING+=("golang")
    GO_INSTALLED=false
    return 1
}

# Check system tools
check_system_tools() {
    print_step "Checking system tools..."

    local tools=("curl" "wget" "git")
    local missing_tools=()

    for tool in "${tools[@]}"; do
        if command_exists "$tool"; then
            print_success "$tool found"
        else
            print_error "$tool not found"
            missing_tools+=("$tool")
        fi
    done

    if [ ${#missing_tools[@]} -gt 0 ]; then
        DEPENDENCIES_MISSING+=("${missing_tools[@]}")
        return 1
    fi

    return 0
}

# Check reconnaissance tools
check_recon_tools() {
    print_step "Checking reconnaissance tools..."

    local tools=("assetfinder" "subfinder" "httpx" "anew")
    local missing_tools=()

    for tool in "${tools[@]}"; do
        if command_exists "$tool"; then
            local version=$($tool -version 2>/dev/null || $tool --version 2>/dev/null || echo "unknown")
            print_success "$tool found ($version)"
        else
            print_error "$tool not found"
            missing_tools+=("$tool")
        fi
    done

    if [ ${#missing_tools[@]} -gt 0 ]; then
        TOOLS_MISSING+=("${missing_tools[@]}")
        return 1
    fi

    return 0
}

# Smart installation functions
install_system_dependencies() {
    if [ ${#DEPENDENCIES_MISSING[@]} -eq 0 ]; then
        return 0
    fi

    print_header "📦 Installing System Dependencies"

    case $PACKAGE_MANAGER in
        "apt")
            print_step "Updating package lists..."
            sudo apt-get update -qq

            for dep in "${DEPENDENCIES_MISSING[@]}"; do
                case $dep in
                    "python3")
                        print_step "Installing Python 3..."
                        sudo apt-get install -y python3 python3-pip python3-venv
                        ;;
                    "python3-pip")
                        print_step "Installing pip..."
                        sudo apt-get install -y python3-pip
                        ;;
                    "golang")
                        install_go_from_source
                        ;;
                    *)
                        print_step "Installing $dep..."
                        sudo apt-get install -y "$dep"
                        ;;
                esac
            done
            ;;
        "yum"|"dnf")
            local pkg_cmd="$PACKAGE_MANAGER"
            print_step "Installing dependencies with $pkg_cmd..."

            for dep in "${DEPENDENCIES_MISSING[@]}"; do
                case $dep in
                    "python3")
                        sudo $pkg_cmd install -y python3 python3-pip
                        ;;
                    "python3-pip")
                        sudo $pkg_cmd install -y python3-pip
                        ;;
                    "golang")
                        install_go_from_source
                        ;;
                    *)
                        sudo $pkg_cmd install -y "$dep"
                        ;;
                esac
            done
            ;;
        "brew")
            for dep in "${DEPENDENCIES_MISSING[@]}"; do
                case $dep in
                    "python3")
                        brew install python3
                        ;;
                    "golang")
                        brew install go
                        ;;
                    *)
                        brew install "$dep"
                        ;;
                esac
            done
            ;;
        "pacman")
            sudo pacman -Sy
            for dep in "${DEPENDENCIES_MISSING[@]}"; do
                case $dep in
                    "python3")
                        sudo pacman -S --noconfirm python python-pip
                        ;;
                    "python3-pip")
                        sudo pacman -S --noconfirm python-pip
                        ;;
                    "golang")
                        sudo pacman -S --noconfirm go
                        ;;
                    *)
                        sudo pacman -S --noconfirm "$dep"
                        ;;
                esac
            done
            ;;
        *)
            print_error "No supported package manager found. Please install dependencies manually:"
            for dep in "${DEPENDENCIES_MISSING[@]}"; do
                echo "  - $dep"
            done
            exit 1
            ;;
    esac

    INSTALL_SUMMARY+=("System dependencies")
}

# Install Go from official source
install_go_from_source() {
    print_step "Installing Go from official source..."

    local go_version="1.21.5"
    local os_name="$DETECTED_OS"
    local arch_name="$DETECTED_ARCH"

    # Adjust OS name for Go download
    case $os_name in
        "macos") os_name="darwin" ;;
    esac

    local go_tarball="go${go_version}.${os_name}-${arch_name}.tar.gz"
    local go_url="https://golang.org/dl/${go_tarball}"
    local temp_file="/tmp/${go_tarball}"

    print_info "Downloading Go $go_version for $os_name-$arch_name..."

    if command_exists wget; then
        wget -q --show-progress "$go_url" -O "$temp_file"
    elif command_exists curl; then
        curl -L --progress-bar "$go_url" -o "$temp_file"
    else
        print_error "Neither wget nor curl found. Cannot download Go."
        exit 1
    fi

    print_step "Installing Go to /usr/local/go..."
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf "$temp_file"

    # Add Go to PATH
    local shell_rc=""
    if [[ -n "$BASH_VERSION" ]]; then
        shell_rc="$HOME/.bashrc"
    elif [[ -n "$ZSH_VERSION" ]]; then
        shell_rc="$HOME/.zshrc"
    else
        shell_rc="$HOME/.profile"
    fi

    if ! grep -q "/usr/local/go/bin" "$shell_rc" 2>/dev/null; then
        echo 'export PATH=$PATH:/usr/local/go/bin' >> "$shell_rc"
        echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> "$shell_rc"
    fi

    export PATH=$PATH:/usr/local/go/bin
    export PATH=$PATH:$(go env GOPATH 2>/dev/null)/bin

    rm "$temp_file"
    print_success "Go installed successfully"
    GO_INSTALLED=true
}

# Install Python dependencies
install_python_dependencies() {
    if [[ "$PYTHON_INSTALLED" == false ]] || [[ -z "$PIP_CMD" ]]; then
        print_warning "Python or pip not available, skipping Python dependencies"
        return 1
    fi

    print_header "🐍 Installing Python Dependencies"

    if [[ ! -f "requirements.txt" ]]; then
        print_error "requirements.txt not found in current directory"
        return 1
    fi

    print_step "Installing Python packages..."

    # Upgrade pip first
    $PIP_CMD install --upgrade pip

    # Install requirements with progress
    $PIP_CMD install -r requirements.txt --progress-bar on

    print_success "Python dependencies installed"
    INSTALL_SUMMARY+=("Python packages")
    return 0
}

# Install Go-based reconnaissance tools
install_go_tools() {
    if [[ "$GO_INSTALLED" == false ]]; then
        print_warning "Go not available, skipping Go tools"
        return 1
    fi

    if [ ${#TOOLS_MISSING[@]} -eq 0 ]; then
        return 0
    fi

    print_header "🔧 Installing Reconnaissance Tools"

    # Ensure GOPATH/bin is in PATH
    local gopath=$(go env GOPATH 2>/dev/null)
    if [[ -n "$gopath" ]]; then
        export PATH=$PATH:$gopath/bin
    fi

    # Install each missing tool
    for tool in "${TOOLS_MISSING[@]}"; do
        case $tool in
            "assetfinder")
                print_step "Installing assetfinder..."
                go install github.com/tomnomnom/assetfinder@latest
                ;;
            "subfinder")
                print_step "Installing subfinder..."
                go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
                ;;
            "httpx")
                print_step "Installing httpx..."
                go install github.com/projectdiscovery/httpx/cmd/httpx@latest
                ;;
            "anew")
                print_step "Installing anew..."
                go install github.com/tomnomnom/anew@latest
                ;;
            *)
                print_warning "Unknown tool: $tool"
                ;;
        esac
    done

    print_success "Reconnaissance tools installed"
    INSTALL_SUMMARY+=("Go reconnaissance tools")
    return 0
}

# Verify installation
verify_installation() {
    print_header "🧪 Verifying Installation"

    local verification_failed=false

    # Re-check dependencies after installation
    print_step "Re-checking Python..."
    if ! check_python; then
        verification_failed=true
    fi

    print_step "Re-checking Go..."
    if ! check_go; then
        verification_failed=true
    fi

    print_step "Re-checking system tools..."
    if ! check_system_tools; then
        verification_failed=true
    fi

    print_step "Re-checking reconnaissance tools..."
    if ! check_recon_tools; then
        verification_failed=true
    fi

    # Test Python imports
    print_step "Testing Python imports..."
    if [[ -n "$PYTHON_CMD" ]]; then
        if ! $PYTHON_CMD -c "import click, requests, aiohttp, yaml, tqdm, colorama" 2>/dev/null; then
            print_error "Python dependencies verification failed"
            verification_failed=true
        else
            print_success "Python imports working"
        fi
    fi

    # Test the main application
    print_step "Testing K1NGB0B Recon Script..."
    if [[ -n "$PYTHON_CMD" ]] && [[ -f "src/k1ngb0b_recon/__main__.py" ]]; then
        if $PYTHON_CMD -m k1ngb0b_recon --help >/dev/null 2>&1; then
            print_success "K1NGB0B Recon Script is working"
        else
            print_warning "K1NGB0B Recon Script test failed (this might be normal if not in project directory)"
        fi
    fi

    if [[ "$verification_failed" == true ]]; then
        print_error "Installation verification failed"
        return 1
    else
        print_success "All verifications passed!"
        return 0
    fi
}

# Print installation summary
print_installation_summary() {
    print_header "📋 Installation Summary"

    if [ ${#INSTALL_SUMMARY[@]} -eq 0 ]; then
        print_info "No new components were installed (everything was already present)"
    else
        print_info "Successfully installed:"
        for item in "${INSTALL_SUMMARY[@]}"; do
            echo -e "  ${GREEN}${CHECK_MARK}${NC} $item"
        done
    fi

    # Show next steps
    print_header "🚀 Next Steps"
    echo -e "${CYAN}1.${NC} Restart your terminal or run: ${YELLOW}source ~/.bashrc${NC}"
    echo -e "${CYAN}2.${NC} Test the installation: ${YELLOW}python -m k1ngb0b_recon --help${NC}"
    echo -e "${CYAN}3.${NC} Run your first scan: ${YELLOW}python -m k1ngb0b_recon example.com${NC}"

    # Show useful paths
    if [[ -n "$PYTHON_CMD" ]]; then
        echo -e "${CYAN}Python:${NC} $PYTHON_CMD"
    fi
    if [[ "$GO_INSTALLED" == true ]]; then
        local gopath=$(go env GOPATH 2>/dev/null)
        if [[ -n "$gopath" ]]; then
            echo -e "${CYAN}Go tools:${NC} $gopath/bin"
        fi
    fi

    print_success "Installation completed successfully!"
}

# Error handling and cleanup
cleanup_on_error() {
    local exit_code=$?
    print_error "Installation failed with exit code $exit_code"

    if [[ -f "$INSTALL_LOG" ]]; then
        print_info "Check the installation log: $INSTALL_LOG"
        echo -e "\n${DIM}Last 10 lines of log:${NC}"
        tail -10 "$INSTALL_LOG" 2>/dev/null || true
    fi

    print_info "You can try running the installer again or install dependencies manually"
    exit $exit_code
}

# Check for required permissions
check_permissions() {
    print_step "Checking permissions..."

    # Check if we can write to common directories
    local test_dirs=("/usr/local" "/tmp")
    local need_sudo=false

    for dir in "${test_dirs[@]}"; do
        if [[ ! -w "$dir" ]] && [[ "$dir" == "/usr/local" ]]; then
            need_sudo=true
            break
        fi
    done

    if [[ "$need_sudo" == true ]]; then
        print_warning "Some operations may require sudo privileges"
        print_info "You may be prompted for your password during installation"
    fi

    # Check if running as root (not recommended)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root is not recommended for security reasons"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled by user"
            exit 0
        fi
    fi
}

# Main installation function
main() {
    # Set up error handling
    trap cleanup_on_error ERR

    # Initialize log
    echo "K1NGB0B Recon Script Installation Started at $(date)" > "$INSTALL_LOG"

    # Print banner
    echo
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║${NC}  ${WHITE}🎯 K1NGB0B Recon Script - Intelligent Installer v$SCRIPT_VERSION${NC}  ${BOLD}${BLUE}║${NC}"
    echo -e "${BOLD}${BLUE}║${NC}  ${CYAN}Author: mrx-arafat (K1NGB0B)${NC}                              ${BOLD}${BLUE}║${NC}"
    echo -e "${BOLD}${BLUE}║${NC}  ${DIM}Comprehensive, cross-platform dependency installer${NC}      ${BOLD}${BLUE}║${NC}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo

    # Check permissions and setup
    check_permissions

    # Detect system
    detect_system

    # Check all dependencies
    print_header "🔍 Analyzing Current System"
    if check_dependencies; then
        print_success "All dependencies are already satisfied!"
        print_info "Your system is ready to use K1NGB0B Recon Script"

        # Still run verification to show what's available
        verify_installation
        print_installation_summary
        return 0
    fi

    # Ask user for confirmation before installing
    echo
    print_warning "Missing dependencies detected. Installation required."
    print_info "The installer will automatically install missing components."
    echo
    read -p "$(echo -e ${YELLOW}Continue with installation? [Y/n]:${NC} )" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installation cancelled by user"
        exit 0
    fi

    # Install missing dependencies
    local install_failed=false

    # Install system dependencies
    if ! install_system_dependencies; then
        install_failed=true
    fi

    # Re-detect Python and Go after system installation
    if [[ "$PYTHON_INSTALLED" == false ]]; then
        check_python
    fi
    if [[ "$GO_INSTALLED" == false ]]; then
        check_go
    fi

    # Install Python dependencies
    if ! install_python_dependencies; then
        print_warning "Python dependencies installation failed or skipped"
    fi

    # Install Go tools
    if ! install_go_tools; then
        print_warning "Go tools installation failed or skipped"
    fi

    # Final verification
    print_header "🔍 Final Verification"
    if ! verify_installation; then
        print_error "Installation verification failed"
        install_failed=true
    fi

    # Show results
    if [[ "$install_failed" == true ]]; then
        print_error "Installation completed with some errors"
        print_info "Check the log file: $INSTALL_LOG"
        print_info "You may need to install some dependencies manually"
        exit 1
    else
        print_installation_summary
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
