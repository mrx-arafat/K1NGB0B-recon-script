#!/usr/bin/env python3
"""
K1NGB0B Recon Suite - Cross-Platform Installer
Author: mrx-arafat (K1NGB0B)
Supports: macOS (Homebrew), Linux (apt, dnf, pacman)
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional, List, Tuple

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'

def print_success(msg: str) -> None:
    print(f"{Colors.GREEN}[+]{Colors.NC} {msg}")

def print_error(msg: str) -> None:
    print(f"{Colors.RED}[-]{Colors.NC} {msg}")

def print_warning(msg: str) -> None:
    print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}")

def print_info(msg: str) -> None:
    print(f"{Colors.BLUE}[*]{Colors.NC} {msg}")

def print_step(msg: str) -> None:
    print(f"{Colors.CYAN}[>]{Colors.NC} {msg}")

def print_banner() -> None:
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║  K1NGB0B Recon Suite - Cross-Platform Installer              ║
║  Author: mrx-arafat (K1NGB0B)                                ║
║  Supports: macOS (Homebrew) | Linux (apt/dnf/pacman)         ║
╚══════════════════════════════════════════════════════════════╝{Colors.NC}
""")


class SystemInfo:
    """Detect system information for cross-platform support."""

    def __init__(self):
        self.system = platform.system().lower()
        self.is_macos = self.system == 'darwin'
        self.is_linux = self.system == 'linux'
        self.arch = platform.machine().lower()
        self.home = Path.home()
        self.shell = os.environ.get('SHELL', '/bin/bash')
        self.shell_name = Path(self.shell).name

    def get_shell_config(self) -> Path:
        """Get the appropriate shell configuration file."""
        if self.shell_name == 'zsh':
            return self.home / '.zshrc'
        elif self.shell_name == 'fish':
            return self.home / '.config' / 'fish' / 'config.fish'
        else:
            return self.home / '.bashrc'

    def get_package_manager(self) -> Optional[str]:
        """Detect the system package manager."""
        if self.is_macos:
            if shutil.which('brew'):
                return 'brew'
            return None
        elif self.is_linux:
            for pm in ['apt-get', 'dnf', 'yum', 'pacman']:
                if shutil.which(pm):
                    return pm
        return None

    def get_go_binary_suffix(self) -> str:
        """Get the Go binary download suffix for this platform."""
        os_name = 'darwin' if self.is_macos else 'linux'
        arch = 'arm64' if 'arm' in self.arch or 'aarch' in self.arch else 'amd64'
        return f"{os_name}-{arch}"


class ToolInstaller:
    """Handle installation of security tools."""

    GO_TOOLS = {
        'subfinder': 'github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest',
        'httpx': 'github.com/projectdiscovery/httpx/cmd/httpx@latest',
        'nuclei': 'github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest',
        'naabu': 'github.com/projectdiscovery/naabu/v2/cmd/naabu@latest',
        'katana': 'github.com/projectdiscovery/katana/cmd/katana@latest',
        'assetfinder': 'github.com/tomnomnom/assetfinder@latest',
        'anew': 'github.com/tomnomnom/anew@latest',
        'waybackurls': 'github.com/tomnomnom/waybackurls@latest',
        'gau': 'github.com/lc/gau/v2/cmd/gau@latest',
        'ffuf': 'github.com/ffuf/ffuf/v2@latest',
    }

    BREW_TOOLS = ['go', 'python3', 'rustscan']

    APT_TOOLS = ['python3', 'python3-pip', 'python3-venv', 'git', 'curl', 'wget']

    def __init__(self, sys_info: SystemInfo):
        self.sys_info = sys_info
        self.k1ngb0b_dir = sys_info.home / '.k1ngb0b'
        self.wordlists_dir = self.k1ngb0b_dir / 'wordlists'
        self.config_file = self.k1ngb0b_dir / 'config.yaml'

    def run_command(self, cmd: List[str], check: bool = True, capture: bool = False) -> Tuple[int, str]:
        """Run a shell command and return (returncode, output)."""
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture,
                text=True
            )
            return result.returncode, result.stdout if capture else ''
        except subprocess.CalledProcessError as e:
            return e.returncode, str(e)
        except Exception as e:
            return 1, str(e)

    def setup_directories(self) -> bool:
        """Create K1NGB0B directories."""
        print_step("Setting up K1NGB0B directories...")
        try:
            self.k1ngb0b_dir.mkdir(parents=True, exist_ok=True)
            self.wordlists_dir.mkdir(parents=True, exist_ok=True)
            print_success(f"Created {self.k1ngb0b_dir}")
            return True
        except Exception as e:
            print_error(f"Failed to create directories: {e}")
            return False

    def install_homebrew(self) -> bool:
        """Install Homebrew on macOS if not present."""
        if not self.sys_info.is_macos:
            return True
        if shutil.which('brew'):
            print_success("Homebrew already installed")
            return True

        print_step("Installing Homebrew...")
        cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        code, _ = self.run_command(['bash', '-c', cmd], check=False)
        if code != 0:
            print_error("Failed to install Homebrew. Please install manually:")
            print_info("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False
        return True

    def install_system_packages(self) -> bool:
        """Install system packages using the detected package manager."""
        pm = self.sys_info.get_package_manager()
        if not pm:
            print_error("No supported package manager found")
            return False

        print_step(f"Installing system packages using {pm}...")

        if pm == 'brew':
            for tool in self.BREW_TOOLS:
                print_info(f"  Installing {tool}...")
                code, _ = self.run_command(['brew', 'install', tool], check=False)
                if code != 0:
                    print_warning(f"  Could not install {tool} via brew")
        elif pm == 'apt-get':
            self.run_command(['sudo', 'apt-get', 'update'], check=False)
            for tool in self.APT_TOOLS:
                print_info(f"  Installing {tool}...")
                self.run_command(['sudo', 'apt-get', 'install', '-y', tool], check=False)
        elif pm in ['dnf', 'yum']:
            for tool in self.APT_TOOLS:
                print_info(f"  Installing {tool}...")
                self.run_command(['sudo', pm, 'install', '-y', tool], check=False)
        elif pm == 'pacman':
            for tool in ['python', 'python-pip', 'git', 'curl', 'wget']:
                print_info(f"  Installing {tool}...")
                self.run_command(['sudo', 'pacman', '-S', '--noconfirm', tool], check=False)

        return True

    def install_go(self) -> bool:
        """Install Go if not present."""
        if shutil.which('go'):
            code, output = self.run_command(['go', 'version'], capture=True)
            if code == 0:
                print_success(f"Go already installed: {output.strip()}")
                return True

        print_step("Installing Go...")

        if self.sys_info.is_macos and shutil.which('brew'):
            code, _ = self.run_command(['brew', 'install', 'go'], check=False)
            if code == 0:
                print_success("Go installed via Homebrew")
                return True

        # Manual Go installation
        go_version = "1.23.10"
        suffix = self.sys_info.get_go_binary_suffix()
        url = f"https://go.dev/dl/go{go_version}.{suffix}.tar.gz"

        print_info(f"Downloading Go {go_version}...")
        self.run_command(['curl', '-LO', url], check=False)

        tarball = f"go{go_version}.{suffix}.tar.gz"
        if Path(tarball).exists():
            self.run_command(['sudo', 'rm', '-rf', '/usr/local/go'], check=False)
            self.run_command(['sudo', 'tar', '-C', '/usr/local', '-xzf', tarball], check=False)
            Path(tarball).unlink()
            self._add_to_path('/usr/local/go/bin')
            print_success("Go installed successfully")
            return True

        print_error("Failed to install Go")
        return False

    def install_go_tools(self) -> bool:
        """Install Go-based security tools."""
        print_step("Installing Go security tools...")

        go_bin = shutil.which('go')
        if not go_bin:
            print_error("Go not found. Cannot install Go tools.")
            return False

        # Ensure GOPATH/bin is in PATH
        gopath = os.environ.get('GOPATH', str(self.sys_info.home / 'go'))
        gobin = Path(gopath) / 'bin'
        gobin.mkdir(parents=True, exist_ok=True)

        os.environ['PATH'] = f"{gobin}:{os.environ.get('PATH', '')}"

        failed_tools = []
        for tool, package in self.GO_TOOLS.items():
            if shutil.which(tool):
                print_success(f"  {tool} already installed")
                continue

            print_info(f"  Installing {tool}...")
            code, _ = self.run_command(['go', 'install', '-v', package], check=False)
            if code != 0:
                failed_tools.append(tool)
                print_warning(f"  Failed to install {tool}")
            else:
                print_success(f"  {tool} installed")

        if failed_tools:
            print_warning(f"Some tools failed to install: {', '.join(failed_tools)}")

        # Add GOPATH/bin to shell config
        self._add_to_path(str(gobin))

        return True

    def install_rustscan(self) -> bool:
        """Install RustScan."""
        if shutil.which('rustscan'):
            print_success("RustScan already installed")
            return True

        print_step("Installing RustScan...")

        if self.sys_info.is_macos and shutil.which('brew'):
            code, _ = self.run_command(['brew', 'install', 'rustscan'], check=False)
            if code == 0:
                print_success("RustScan installed via Homebrew")
                return True

        # Try cargo if available
        if shutil.which('cargo'):
            code, _ = self.run_command(['cargo', 'install', 'rustscan'], check=False)
            if code == 0:
                print_success("RustScan installed via cargo")
                return True

        print_warning("RustScan not installed. Install manually:")
        if self.sys_info.is_macos:
            print_info("  brew install rustscan")
        else:
            print_info("  cargo install rustscan")
            print_info("  OR download from: https://github.com/RustScan/RustScan/releases")

        return False

    def install_python_deps(self) -> bool:
        """Install Python dependencies."""
        print_step("Installing Python dependencies...")

        script_dir = Path(__file__).parent.resolve()
        requirements = script_dir / 'requirements.txt'

        if not requirements.exists():
            print_warning("requirements.txt not found, skipping Python deps")
            return True

        # Try pip install
        pip_cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(requirements)]

        # Try without --break-system-packages first
        code, _ = self.run_command(pip_cmd, check=False)
        if code != 0:
            # Try with --break-system-packages for PEP 668 systems
            pip_cmd.append('--break-system-packages')
            code, _ = self.run_command(pip_cmd, check=False)

        if code != 0:
            # Suggest using venv
            print_warning("pip install failed. Try using a virtual environment:")
            print_info(f"  python3 -m venv {self.k1ngb0b_dir}/venv")
            print_info(f"  source {self.k1ngb0b_dir}/venv/bin/activate")
            print_info(f"  pip install -r {requirements}")
            return False

        print_success("Python dependencies installed")
        return True

    def download_wordlists(self) -> bool:
        """Download essential wordlists."""
        print_step("Setting up wordlists...")

        wordlists = {
            'subdomains-top5000.txt':
                'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt',
            'common.txt':
                'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt',
        }

        for filename, url in wordlists.items():
            target = self.wordlists_dir / filename
            if target.exists():
                print_success(f"  {filename} already exists")
                continue

            print_info(f"  Downloading {filename}...")
            code, _ = self.run_command(
                ['curl', '-sL', '-o', str(target), url],
                check=False
            )
            if code == 0:
                print_success(f"  {filename} downloaded")
            else:
                print_warning(f"  Failed to download {filename}")

        return True

    def create_default_config(self) -> bool:
        """Create default configuration file."""
        if self.config_file.exists():
            print_success("Config file already exists")
            return True

        print_step("Creating default configuration...")

        config_content = """# K1NGB0B Recon Suite Configuration
# Edit this file to customize your settings

# Performance settings
max_concurrent_requests: 100
request_timeout: 45
dns_timeout: 15

# Wordlists directory
wordlists_dir: ~/.k1ngb0b/wordlists

# API Keys (optional - tools will also check their own configs)
# api_keys:
#   shodan: ""
#   censys_id: ""
#   censys_secret: ""
#   virustotal: ""

# Output settings
output_dir: ./results
create_timestamps: true
"""

        try:
            self.config_file.write_text(config_content)
            print_success(f"Config created at {self.config_file}")
            return True
        except Exception as e:
            print_error(f"Failed to create config: {e}")
            return False

    def _add_to_path(self, path: str) -> None:
        """Add a path to the shell configuration."""
        shell_config = self.sys_info.get_shell_config()

        export_line = f'export PATH="{path}:$PATH"'

        if shell_config.name == 'config.fish':
            export_line = f'set -gx PATH {path} $PATH'

        try:
            if shell_config.exists():
                content = shell_config.read_text()
                if path in content:
                    return  # Already added

            with open(shell_config, 'a') as f:
                f.write(f'\n# Added by K1NGB0B installer\n{export_line}\n')

            print_info(f"Added {path} to {shell_config}")
        except Exception as e:
            print_warning(f"Could not update {shell_config}: {e}")
            print_info(f"Manually add: {export_line}")

    def verify_installation(self) -> None:
        """Verify all tools are installed."""
        print("\n" + "=" * 60)
        print_step("Verifying installation...")
        print("=" * 60)

        tools = list(self.GO_TOOLS.keys()) + ['go', 'rustscan', 'python3']

        installed = []
        missing = []

        for tool in tools:
            if shutil.which(tool):
                installed.append(tool)
            else:
                missing.append(tool)

        print(f"\n{Colors.GREEN}Installed ({len(installed)}):{Colors.NC}")
        for tool in installed:
            print(f"  {Colors.GREEN}[+]{Colors.NC} {tool}")

        if missing:
            print(f"\n{Colors.YELLOW}Missing ({len(missing)}):{Colors.NC}")
            for tool in missing:
                print(f"  {Colors.YELLOW}[-]{Colors.NC} {tool}")
            print_warning("\nSome tools are missing. You may need to:")
            print_info("  1. Restart your terminal to reload PATH")
            print_info("  2. Run the installer again")
            print_info("  3. Install missing tools manually")
        else:
            print_success("\nAll tools installed successfully!")


def main():
    print_banner()

    sys_info = SystemInfo()
    print_info(f"Detected OS: {sys_info.system} ({sys_info.arch})")
    print_info(f"Shell: {sys_info.shell_name}")
    print_info(f"Package manager: {sys_info.get_package_manager() or 'Not detected'}")
    print()

    installer = ToolInstaller(sys_info)

    # Run installation steps
    steps = [
        ("Setting up directories", installer.setup_directories),
        ("Installing system packages", installer.install_system_packages),
        ("Installing Go", installer.install_go),
        ("Installing Go tools", installer.install_go_tools),
        ("Installing RustScan", installer.install_rustscan),
        ("Installing Python dependencies", installer.install_python_deps),
        ("Downloading wordlists", installer.download_wordlists),
        ("Creating configuration", installer.create_default_config),
    ]

    print("=" * 60)
    for step_name, step_func in steps:
        print(f"\n{Colors.BOLD}>> {step_name}{Colors.NC}")
        step_func()

    # Verify installation
    installer.verify_installation()

    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║  Installation Complete!                                       ║
║                                                               ║
║  Next steps:                                                  ║
║  1. Restart your terminal or run: source {str(sys_info.get_shell_config()).ljust(20)}║
║  2. Run: python3 k1ngb0b_recon.py example.com                 ║
║                                                               ║
║  Configuration: ~/.k1ngb0b/config.yaml                        ║
║  Wordlists: ~/.k1ngb0b/wordlists/                             ║
╚══════════════════════════════════════════════════════════════╝{Colors.NC}
""")


if __name__ == '__main__':
    main()
