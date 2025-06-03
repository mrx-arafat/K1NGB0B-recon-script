"""
K1NGB0B Recon Script - A comprehensive domain reconnaissance tool.

Author: Arafat-X30N
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "mrx-arafat"
__email__ = "mrx.arafat@example.com"
__description__ = "A comprehensive domain reconnaissance tool for cybersecurity professionals"

from .main import main
from .subdomain_discovery import SubdomainDiscovery
from .config import Config

__all__ = ["main", "SubdomainDiscovery", "Config"]
