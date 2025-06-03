#!/usr/bin/env python3
"""
Example usage of K1NGB0B Recon Script.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from k1ngb0b_recon.config import Config
from k1ngb0b_recon.main import ReconApp
from k1ngb0b_recon.utils import print_banner, validate_domain


async def example_recon(domain: str):
    """Example reconnaissance function."""
    
    # Print banner
    print_banner()
    
    # Validate domain
    if not validate_domain(domain):
        print(f"Error: Invalid domain '{domain}'")
        return
    
    # Create configuration
    config = Config()
    config.verbose = True
    
    # Create and run reconnaissance app
    app = ReconApp(domain, config, "./results")
    results = await app.run_reconnaissance(run_live_check=True)
    
    print(f"\nReconnaissance completed!")
    print(f"Status: {results['status']}")
    print(f"Total subdomains found: {results['subdomains']['total_discovered']}")
    print(f"Live subdomains: {results['subdomains']['total_live']}")
    print(f"Results saved to: {app.directories['base']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python example.py <domain>")
        sys.exit(1)
    
    domain = sys.argv[1]
    asyncio.run(example_recon(domain))
