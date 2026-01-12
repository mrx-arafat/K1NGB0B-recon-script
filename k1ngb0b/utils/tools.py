"""
Tool availability and version checking utilities.
"""

import shutil
import subprocess
import re
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from pathlib import Path


@dataclass
class ToolInfo:
    """Information about an installed tool."""
    name: str
    binary: Optional[str]
    available: bool
    version: Optional[str] = None
    install_hint: Optional[str] = None


# Installation hints for common tools
INSTALL_HINTS = {
    'subfinder': 'go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest',
    'httpx': 'go install github.com/projectdiscovery/httpx/cmd/httpx@latest',
    'nuclei': 'go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest',
    'naabu': 'go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest',
    'katana': 'go install github.com/projectdiscovery/katana/cmd/katana@latest',
    'assetfinder': 'go install github.com/tomnomnom/assetfinder@latest',
    'anew': 'go install github.com/tomnomnom/anew@latest',
    'waybackurls': 'go install github.com/tomnomnom/waybackurls@latest',
    'gau': 'go install github.com/lc/gau/v2/cmd/gau@latest',
    'ffuf': 'go install github.com/ffuf/ffuf/v2@latest',
    'amass': 'go install github.com/owasp-amass/amass/v4/...@latest',
    'rustscan': 'brew install rustscan  # macOS\ncargo install rustscan  # Linux',
    'nmap': 'brew install nmap  # macOS\nsudo apt install nmap  # Linux',
}

# Version extraction patterns for common tools
VERSION_PATTERNS = {
    'subfinder': r'v?(\d+\.\d+\.\d+)',
    'httpx': r'v?(\d+\.\d+\.\d+)',
    'nuclei': r'v?(\d+\.\d+\.\d+)',
    'naabu': r'v?(\d+\.\d+\.\d+)',
    'ffuf': r'v?(\d+\.\d+\.\d+)',
    'rustscan': r'(\d+\.\d+\.\d+)',
    'nmap': r'(\d+\.\d+)',
    'go': r'go(\d+\.\d+(?:\.\d+)?)',
}


def check_tool(name: str) -> ToolInfo:
    """Check if a tool is available and get its version."""
    binary = shutil.which(name)

    if not binary:
        return ToolInfo(
            name=name,
            binary=None,
            available=False,
            install_hint=INSTALL_HINTS.get(name)
        )

    # Try to get version
    version = None
    try:
        # Try common version flags
        for flag in ['-version', '--version', '-v', 'version']:
            try:
                result = subprocess.run(
                    [binary, flag],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                output = result.stdout + result.stderr

                # Try to extract version number
                pattern = VERSION_PATTERNS.get(name, r'v?(\d+\.\d+(?:\.\d+)?)')
                match = re.search(pattern, output)
                if match:
                    version = match.group(1)
                    break
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue
    except Exception:
        pass

    return ToolInfo(
        name=name,
        binary=binary,
        available=True,
        version=version,
        install_hint=INSTALL_HINTS.get(name)
    )


def check_tools(names: List[str]) -> Dict[str, ToolInfo]:
    """Check multiple tools at once."""
    return {name: check_tool(name) for name in names}


def get_available_tools(names: List[str]) -> List[str]:
    """Get list of available tools from the given names."""
    return [name for name in names if shutil.which(name)]


def get_missing_tools(names: List[str]) -> List[str]:
    """Get list of missing tools from the given names."""
    return [name for name in names if not shutil.which(name)]


def require_tools(names: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if all required tools are available.
    Returns (all_available, list_of_missing_tools).
    """
    missing = get_missing_tools(names)
    return len(missing) == 0, missing


def print_tool_status(names: Optional[List[str]] = None) -> None:
    """Print status of all tools with colors."""
    from .colors import Colors, print_success, print_warning, print_header

    if names is None:
        names = list(INSTALL_HINTS.keys())

    print_header("Tool Status")

    available = []
    missing = []

    for name in names:
        info = check_tool(name)
        if info.available:
            available.append(info)
        else:
            missing.append(info)

    if available:
        print(f"{Colors.GREEN}Available ({len(available)}):{Colors.NC}")
        for info in available:
            version_str = f" v{info.version}" if info.version else ""
            print(f"  {Colors.GREEN}[+]{Colors.NC} {info.name}{version_str}")

    if missing:
        print(f"\n{Colors.YELLOW}Missing ({len(missing)}):{Colors.NC}")
        for info in missing:
            print(f"  {Colors.YELLOW}[-]{Colors.NC} {info.name}")
            if info.install_hint:
                print(f"      {Colors.DIM}Install: {info.install_hint.split(chr(10))[0]}{Colors.NC}")


# Essential tools for each stage
DISCOVERY_TOOLS = ['subfinder', 'assetfinder', 'amass', 'httpx']
SCANNING_TOOLS = ['nuclei', 'ffuf', 'naabu', 'rustscan']
UTILITY_TOOLS = ['anew', 'waybackurls', 'gau', 'katana']

ALL_TOOLS = DISCOVERY_TOOLS + SCANNING_TOOLS + UTILITY_TOOLS


def check_discovery_tools() -> Tuple[bool, List[str]]:
    """Check if discovery tools are available."""
    return require_tools(DISCOVERY_TOOLS)


def check_scanning_tools() -> Tuple[bool, List[str]]:
    """Check if scanning tools are available."""
    return require_tools(SCANNING_TOOLS)


def check_all_tools() -> Tuple[bool, List[str]]:
    """Check if all tools are available."""
    return require_tools(ALL_TOOLS)
