"""
K1NGB0B Configuration Module
Cross-platform configuration management with OS-aware paths.
"""

import os
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class ToolConfig:
    """Configuration for an external tool."""
    name: str
    binary: Optional[str] = None
    available: bool = False
    version: Optional[str] = None


@dataclass
class Config:
    """Main configuration class with cross-platform support."""

    # System info
    system: str = field(default_factory=lambda: platform.system().lower())
    arch: str = field(default_factory=lambda: platform.machine().lower())

    # Paths
    home_dir: Path = field(default_factory=Path.home)
    k1ngb0b_dir: Path = field(default_factory=lambda: Path.home() / '.k1ngb0b')
    wordlists_dir: Path = field(default_factory=lambda: Path.home() / '.k1ngb0b' / 'wordlists')
    config_file: Path = field(default_factory=lambda: Path.home() / '.k1ngb0b' / 'config.yaml')

    # Performance settings
    max_concurrent_requests: int = 100
    request_timeout: int = 45
    dns_timeout: int = 15
    port_scan_timeout: int = 8
    batch_size_dns: int = 150
    batch_size_http: int = 75
    rate_limit_delay: float = 0.1

    # Common ports for scanning
    common_ports: List[int] = field(default_factory=lambda: [
        80, 443, 8080, 8443, 3000, 8000, 9000, 9443,
        8888, 8008, 8081, 8082, 9001, 9002, 9090, 9091
    ])

    # SecLists base URL
    seclists_base_url: str = "https://raw.githubusercontent.com/danielmiessler/SecLists/master"

    # Tool configurations
    tools: Dict[str, ToolConfig] = field(default_factory=dict)

    # API keys (loaded from config file)
    api_keys: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize after dataclass creation."""
        self._detect_tools()
        self._load_config_file()

    @property
    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return self.system == 'darwin'

    @property
    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return self.system == 'linux'

    @property
    def shell_config_path(self) -> Path:
        """Get the appropriate shell configuration file."""
        shell = os.environ.get('SHELL', '/bin/bash')
        shell_name = Path(shell).name

        if shell_name == 'zsh':
            return self.home_dir / '.zshrc'
        elif shell_name == 'fish':
            return self.home_dir / '.config' / 'fish' / 'config.fish'
        else:
            return self.home_dir / '.bashrc'

    def _detect_tools(self) -> None:
        """Detect available security tools."""
        tool_names = [
            'subfinder', 'assetfinder', 'amass', 'httpx', 'nuclei',
            'ffuf', 'katana', 'gau', 'waybackurls', 'anew', 'naabu',
            'rustscan', 'nmap', 'masscan', 'curl', 'dig'
        ]

        for name in tool_names:
            binary = shutil.which(name)
            self.tools[name] = ToolConfig(
                name=name,
                binary=binary,
                available=binary is not None
            )

    def _load_config_file(self) -> None:
        """Load configuration from YAML file if exists."""
        if not self.config_file.exists():
            return

        if not YAML_AVAILABLE:
            return

        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f) or {}

            # Update performance settings
            if 'max_concurrent_requests' in data:
                self.max_concurrent_requests = data['max_concurrent_requests']
            if 'request_timeout' in data:
                self.request_timeout = data['request_timeout']
            if 'dns_timeout' in data:
                self.dns_timeout = data['dns_timeout']

            # Load API keys
            if 'api_keys' in data and isinstance(data['api_keys'], dict):
                self.api_keys = data['api_keys']

            # Custom wordlists directory
            if 'wordlists_dir' in data:
                self.wordlists_dir = Path(data['wordlists_dir']).expanduser()

        except Exception:
            pass  # Silently ignore config errors

    def get_tool(self, name: str) -> Optional[str]:
        """Get the binary path for a tool, or None if not available."""
        tool = self.tools.get(name)
        if tool and tool.available:
            return tool.binary
        return None

    def require_tool(self, name: str) -> str:
        """Get the binary path for a tool, raising an error if not available."""
        binary = self.get_tool(name)
        if not binary:
            raise RuntimeError(f"Required tool '{name}' not found. Run install.py to install.")
        return binary

    def get_wordlist(self, category: str, name: str) -> Optional[Path]:
        """Get path to a wordlist, checking local then downloading if needed."""
        # Check local wordlists directory first
        local_path = self.wordlists_dir / f"{name}.txt"
        if local_path.exists():
            return local_path

        # Check common system locations (Linux)
        if self.is_linux:
            system_paths = [
                Path('/usr/share/wordlists') / category / f"{name}.txt",
                Path('/usr/share/seclists') / category / f"{name}.txt",
            ]
            for path in system_paths:
                if path.exists():
                    return path

        return None

    def get_seclists_url(self, category: str, wordlist: str) -> str:
        """Get the URL for a SecLists wordlist."""
        url_map = {
            ('dns', 'subdomains-5000'): 'Discovery/DNS/subdomains-top1million-5000.txt',
            ('dns', 'subdomains-110000'): 'Discovery/DNS/subdomains-top1million-110000.txt',
            ('dns', 'bitquark'): 'Discovery/DNS/bitquark-subdomains-top100000.txt',
            ('web', 'common'): 'Discovery/Web-Content/common.txt',
            ('web', 'big'): 'Discovery/Web-Content/big.txt',
            ('web', 'directory-medium'): 'Discovery/Web-Content/directory-list-2.3-medium.txt',
            ('api', 'endpoints'): 'Discovery/Web-Content/api/api-endpoints.txt',
        }

        path = url_map.get((category, wordlist))
        if path:
            return f"{self.seclists_base_url}/{path}"
        return f"{self.seclists_base_url}/{category}/{wordlist}.txt"

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.k1ngb0b_dir.mkdir(parents=True, exist_ok=True)
        self.wordlists_dir.mkdir(parents=True, exist_ok=True)

    def get_output_structure(self, base_dir: Path) -> Dict[str, Path]:
        """Get the 10-tier output directory structure."""
        structure = {
            'raw_discovery': base_dir / '01_raw_discovery',
            'processed_data': base_dir / '02_processed_data',
            'live_analysis': base_dir / '03_live_analysis',
            'technologies': base_dir / '04_technologies',
            'vulnerabilities': base_dir / '05_vulnerabilities',
            'port_scanning': base_dir / '06_port_scanning',
            'screenshots': base_dir / '07_screenshots',
            'final_reports': base_dir / '08_final_reports',
            'advanced_discovery': base_dir / '09_advanced_discovery',
            'manual_verification': base_dir / '10_manual_verification',
        }
        return structure

    def create_output_structure(self, base_dir: Path) -> Dict[str, Path]:
        """Create the output directory structure and return paths."""
        structure = self.get_output_structure(base_dir)
        for path in structure.values():
            path.mkdir(parents=True, exist_ok=True)
        return structure

    def summary(self) -> str:
        """Get a summary of the configuration."""
        available = [name for name, tool in self.tools.items() if tool.available]
        missing = [name for name, tool in self.tools.items() if not tool.available]

        lines = [
            f"System: {self.system} ({self.arch})",
            f"macOS: {self.is_macos}",
            f"K1NGB0B Dir: {self.k1ngb0b_dir}",
            f"Wordlists: {self.wordlists_dir}",
            f"Available tools ({len(available)}): {', '.join(available[:5])}{'...' if len(available) > 5 else ''}",
            f"Missing tools ({len(missing)}): {', '.join(missing) if missing else 'None'}",
        ]
        return '\n'.join(lines)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload the configuration."""
    global _config
    _config = Config()
    return _config
