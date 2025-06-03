"""
Utility functions for K1NGB0B Recon Script.
"""

import os
import re
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Set, Optional, Dict, Any
from urllib.parse import urlparse
import validators
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class Logger:
    """Custom logger with colored output."""
    
    def __init__(self, name: str = "k1ngb0b_recon", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create console handler with colored formatter
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # Create formatter
            formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)
    
    def success(self, message: str) -> None:
        self.logger.info(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


class ColoredFormatter(logging.Formatter):
    """Colored log formatter."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.BLUE,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def validate_domain(domain: str) -> bool:
    """Validate if the given string is a valid domain."""
    if not domain:
        return False
    
    # Remove protocol if present
    if domain.startswith(('http://', 'https://')):
        domain = urlparse(domain).netloc
    
    # Basic domain validation
    return validators.domain(domain) or validators.url(f"http://{domain}")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by replacing invalid characters."""
    # Replace dots with underscores and remove invalid characters
    sanitized = re.sub(r'[^\w\-_.]', '_', filename)
    return sanitized.replace('.', '_')


def create_directory_structure(base_path: str, domain: str) -> Dict[str, str]:
    """Create organized directory structure for results."""
    sanitized_domain = sanitize_filename(domain)
    base_dir = Path(base_path) / sanitized_domain
    
    directories = {
        'base': str(base_dir),
        'raw': str(base_dir / 'raw'),
        'processed': str(base_dir / 'processed'),
        'reports': str(base_dir / 'reports'),
        'logs': str(base_dir / 'logs')
    }
    
    # Create directories
    for dir_path in directories.values():
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    return directories


def run_command(command: List[str], timeout: int = 300, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    """Run a command with timeout and error handling."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            check=False
        )
        return result
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out after {timeout} seconds: {' '.join(command)}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Command not found: {command[0]}")


def check_tool_availability(tool_name: str) -> bool:
    """Check if a tool is available in the system PATH."""
    try:
        result = subprocess.run(
            ['which', tool_name],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except:
        return False


def deduplicate_subdomains(subdomains: List[str]) -> List[str]:
    """Remove duplicates and clean subdomain list."""
    cleaned = set()
    
    for subdomain in subdomains:
        if not subdomain:
            continue
        
        # Clean the subdomain
        subdomain = subdomain.strip().lower()
        
        # Remove protocol if present
        if subdomain.startswith(('http://', 'https://')):
            subdomain = urlparse(subdomain).netloc
        
        # Remove port if present
        if ':' in subdomain:
            subdomain = subdomain.split(':')[0]
        
        # Validate and add
        if validate_domain(subdomain):
            cleaned.add(subdomain)
    
    return sorted(list(cleaned))


def read_file_lines(file_path: str) -> List[str]:
    """Read lines from a file, handling errors gracefully."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []
    except Exception as e:
        Logger().warning(f"Error reading file {file_path}: {e}")
        return []


def write_file_lines(file_path: str, lines: List[str]) -> None:
    """Write lines to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")
    except Exception as e:
        Logger().error(f"Error writing to file {file_path}: {e}")
        raise


def append_file_lines(file_path: str, lines: List[str]) -> None:
    """Append lines to a file."""
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")
    except Exception as e:
        Logger().error(f"Error appending to file {file_path}: {e}")
        raise


def save_json_report(data: Dict[str, Any], file_path: str) -> None:
    """Save data as JSON report."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        Logger().error(f"Error saving JSON report {file_path}: {e}")
        raise


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def print_banner():
    """Print the tool banner."""
    banner = f"""
{Fore.CYAN}
██╗  ██╗ ██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ██████╗ 
██║ ██╔╝███║████╗  ██║██╔════╝ ██╔══██╗██╔═████╗██╔══██╗
█████╔╝ ╚██║██╔██╗ ██║██║  ███╗██████╔╝██║██╔██║██████╔╝
██╔═██╗  ██║██║╚██╗██║██║   ██║██╔══██╗████╔╝██║██╔══██╗
██║  ██╗ ██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝██████╔╝
╚═╝  ╚═╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝ 
                                                         
    {Fore.YELLOW}Recon Script v2.0 - Domain Reconnaissance Tool{Style.RESET_ALL}
    {Fore.GREEN}Author: mrx-arafat (K1NGB0B){Style.RESET_ALL}
    {Fore.BLUE}https://github.com/mrx-arafat/k1ngb0b-recon{Style.RESET_ALL}
{Style.RESET_ALL}
"""
    print(banner)
