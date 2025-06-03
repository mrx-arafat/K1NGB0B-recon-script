#!/usr/bin/env python3
"""
K1NGB0B Recon Script - Simple Domain Reconnaissance Tool
Author: mrx-arafat (K1NGB0B)
Version: 2.0.0

A simple, powerful subdomain discovery tool for bug bounty hunters and security professionals.
"""

import os
import sys
import time
import json
import asyncio
import subprocess
from pathlib import Path
from typing import List, Set

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


def print_banner():
    """Print the tool banner."""
    banner = """
██╗  ██╗ ██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ██████╗ 
██║ ██╔╝███║████╗  ██║██╔════╝ ██╔══██╗██╔═████╗██╔══██╗
█████╔╝ ╚██║██╔██╗ ██║██║  ███╗██████╔╝██║██╔██║██████╔╝
██╔═██╗  ██║██║╚██╗██║██║   ██║██╔══██╗████╔╝██║██╔══██╗
██║  ██╗ ██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝██████╔╝
╚═╝  ╚═╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝ 
                                                         
    🎯 K1NGB0B Recon Script v2.0 - Domain Reconnaissance Tool
    👤 Author: mrx-arafat (K1NGB0B)
    🔗 https://github.com/mrx-arafat/k1ngb0b-recon
"""
    print(banner)


def validate_domain(domain: str) -> bool:
    """Simple domain validation."""
    if not domain or len(domain) < 3:
        return False
    
    # Remove protocol if present
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://')[1]
    
    # Basic checks
    if '.' not in domain:
        return False
    
    # Remove common invalid characters
    invalid_chars = [' ', '/', '\\', '?', '#', '@']
    for char in invalid_chars:
        if char in domain:
            return False
    
    return True


def create_directories(domain: str) -> dict:
    """Create organized directory structure for results."""
    sanitized_domain = domain.replace('.', '_')
    base_dir = Path(f"./{sanitized_domain}_results")
    
    directories = {
        'base': str(base_dir),
        'raw': str(base_dir / 'raw'),
        'processed': str(base_dir / 'processed'),
        'reports': str(base_dir / 'reports')
    }
    
    # Create directories
    for dir_path in directories.values():
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    return directories


def run_command(command: List[str], timeout: int = 300) -> tuple:
    """Run a command and return output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except FileNotFoundError:
        return False, "", f"Command not found: {command[0]}"


def check_tool(tool_name: str) -> bool:
    """Check if a tool is available."""
    success, _, _ = run_command(['which', tool_name])
    return success


def run_assetfinder(domain: str, output_file: str) -> List[str]:
    """Run assetfinder for subdomain discovery."""
    print("🔍 Running assetfinder...")
    
    if not check_tool('assetfinder'):
        print("   ⚠️  assetfinder not found, skipping...")
        return []
    
    success, output, error = run_command(['assetfinder', '-subs-only', domain])
    
    if success and output:
        subdomains = [line.strip() for line in output.split('\n') if line.strip()]
        
        # Save raw output
        with open(output_file, 'w') as f:
            f.write(output)
        
        print(f"   ✅ Found {len(subdomains)} subdomains")
        return subdomains
    else:
        print(f"   ❌ Failed: {error}")
        return []


def run_subfinder(domain: str, output_file: str) -> List[str]:
    """Run subfinder for subdomain discovery."""
    print("🔍 Running subfinder...")
    
    if not check_tool('subfinder'):
        print("   ⚠️  subfinder not found, skipping...")
        return []
    
    success, output, error = run_command(['subfinder', '-d', domain, '-o', output_file])
    
    if success:
        try:
            with open(output_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
            print(f"   ✅ Found {len(subdomains)} subdomains")
            return subdomains
        except:
            print("   ❌ Failed to read output file")
            return []
    else:
        print(f"   ❌ Failed: {error}")
        return []


async def run_crt_sh(domain: str, output_file: str) -> List[str]:
    """Fetch subdomains from crt.sh (Certificate Transparency)."""
    print("🔍 Checking Certificate Transparency (crt.sh)...")

    if not AIOHTTP_AVAILABLE:
        print("   ⚠️  aiohttp not installed, skipping crt.sh...")
        return []

    try:
        url = f"https://crt.sh/?q={domain}&output=json"

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    subdomains = set()

                    for entry in data:
                        name_value = entry.get('name_value', '')
                        for subdomain in name_value.split('\n'):
                            subdomain = subdomain.strip().replace('*.', '')
                            if subdomain and domain in subdomain:
                                subdomains.add(subdomain)

                    subdomain_list = list(subdomains)

                    # Save raw output
                    with open(output_file, 'w') as f:
                        for subdomain in subdomain_list:
                            f.write(f"{subdomain}\n")

                    print(f"   ✅ Found {len(subdomain_list)} subdomains")
                    return subdomain_list
                else:
                    print(f"   ❌ Failed: HTTP {response.status}")
                    return []

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return []


def check_live_subdomains(subdomains: List[str], output_file: str) -> List[str]:
    """Check which subdomains are live using httpx."""
    print("🔍 Checking live subdomains...")
    
    if not check_tool('httpx'):
        print("   ⚠️  httpx not found, skipping live check...")
        return []
    
    if not subdomains:
        print("   ⚠️  No subdomains to check")
        return []
    
    # Create temporary input file
    temp_file = "temp_subdomains.txt"
    with open(temp_file, 'w') as f:
        for subdomain in subdomains:
            f.write(f"{subdomain}\n")
    
    success, output, error = run_command([
        'httpx', '-list', temp_file, '-o', output_file, '-silent'
    ])
    
    # Clean up temp file
    try:
        os.remove(temp_file)
    except:
        pass
    
    if success:
        try:
            with open(output_file, 'r') as f:
                live_subdomains = [line.strip() for line in f if line.strip()]
            print(f"   ✅ Found {len(live_subdomains)} live subdomains")
            return live_subdomains
        except:
            print("   ❌ Failed to read output file")
            return []
    else:
        print(f"   ❌ Failed: {error}")
        return []


def deduplicate_subdomains(subdomains: List[str]) -> List[str]:
    """Remove duplicates and clean subdomain list."""
    cleaned = set()
    
    for subdomain in subdomains:
        if not subdomain:
            continue
        
        subdomain = subdomain.strip().lower()
        
        # Remove protocol if present
        if subdomain.startswith(('http://', 'https://')):
            subdomain = subdomain.split('://')[1]
        
        # Remove port if present
        if ':' in subdomain:
            subdomain = subdomain.split(':')[0]
        
        if validate_domain(subdomain):
            cleaned.add(subdomain)
    
    return sorted(list(cleaned))


async def run_reconnaissance(domain: str):
    """Run the complete reconnaissance process."""
    print(f"\n🎯 Starting reconnaissance for: {domain}")
    print("=" * 60)
    
    start_time = time.time()
    
    # Create directory structure
    directories = create_directories(domain)
    print(f"📁 Results will be saved to: {directories['base']}")
    
    # Run subdomain discovery
    print(f"\n🔍 Starting subdomain discovery...")
    
    all_subdomains = []
    
    # Run assetfinder
    assetfinder_results = run_assetfinder(domain, f"{directories['raw']}/assetfinder.txt")
    all_subdomains.extend(assetfinder_results)
    
    # Run subfinder
    subfinder_results = run_subfinder(domain, f"{directories['raw']}/subfinder.txt")
    all_subdomains.extend(subfinder_results)
    
    # Run crt.sh
    crt_results = await run_crt_sh(domain, f"{directories['raw']}/crt.txt")
    all_subdomains.extend(crt_results)
    
    # Deduplicate and clean
    unique_subdomains = deduplicate_subdomains(all_subdomains)
    
    # Save all unique subdomains
    unique_file = f"{directories['processed']}/all_subdomains.txt"
    with open(unique_file, 'w') as f:
        for subdomain in unique_subdomains:
            f.write(f"{subdomain}\n")
    
    # Check live subdomains
    live_subdomains = check_live_subdomains(unique_subdomains, f"{directories['processed']}/live_subdomains.txt")
    
    # Generate report
    duration = time.time() - start_time
    
    report = {
        'target_domain': domain,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'scan_duration_seconds': round(duration, 2),
        'total_subdomains_found': len(all_subdomains),
        'unique_subdomains': len(unique_subdomains),
        'live_subdomains': len(live_subdomains),
        'discovered_subdomains': unique_subdomains,
        'live_subdomains_list': live_subdomains
    }
    
    # Save JSON report
    with open(f"{directories['reports']}/report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print results
    print(f"\n📊 Reconnaissance Results:")
    print(f"   🎯 Target: {domain}")
    print(f"   ⏱️  Duration: {duration:.1f} seconds")
    print(f"   📈 Total found: {len(all_subdomains)} subdomains")
    print(f"   🔗 Unique: {len(unique_subdomains)} subdomains")
    print(f"   🟢 Live: {len(live_subdomains)} subdomains")
    
    if unique_subdomains:
        print(f"\n🎯 Discovered subdomains:")
        for subdomain in unique_subdomains[:20]:  # Show first 20
            status = "🟢 LIVE" if subdomain in live_subdomains else "⚪ UNKNOWN"
            print(f"   {status} {subdomain}")
        
        if len(unique_subdomains) > 20:
            print(f"   ... and {len(unique_subdomains) - 20} more")
    
    print(f"\n📁 Results saved to:")
    print(f"   📄 All subdomains: {unique_file}")
    print(f"   🟢 Live subdomains: {directories['processed']}/live_subdomains.txt")
    print(f"   📊 JSON report: {directories['reports']}/report.json")
    
    print(f"\n✅ Reconnaissance completed successfully!")


def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []

    # Check Python packages
    if not AIOHTTP_AVAILABLE:
        missing.append("aiohttp (Python package)")

    # Check system tools
    tools = {
        'assetfinder': 'AssetFinder (Go tool)',
        'subfinder': 'Subfinder (Go tool)',
        'httpx': 'httpx (Go tool)',
        'anew': 'anew (Go tool)'
    }

    for tool, description in tools.items():
        success, _, _ = run_command(['which', tool])
        if not success:
            missing.append(description)

    return missing


def main():
    """Main function."""
    print_banner()

    print("\n🎯 K1NGB0B Recon Script - Domain Reconnaissance Tool")
    print("=" * 60)

    # Check dependencies first
    print("\n🔍 Checking dependencies...")
    missing_deps = check_dependencies()

    if missing_deps:
        print(f"\n❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")

        print(f"\n💡 To install all dependencies, run:")
        print(f"   chmod +x install.sh && ./install.sh")
        print(f"\n⚠️  Cannot proceed without all dependencies!")
        return 1

    print("✅ All dependencies found!")

    try:
        domain = input("\n🔍 Enter target domain (e.g., tesla.com): ").strip()

        if not domain:
            print("❌ No domain provided!")
            return 1

        if not validate_domain(domain):
            print(f"❌ Invalid domain: {domain}")
            return 1

        # Remove protocol if present
        if domain.startswith(('http://', 'https://')):
            domain = domain.split('://')[1]

        print(f"✅ Target domain: {domain}")

        # Run reconnaissance
        asyncio.run(run_reconnaissance(domain))
        return 0

    except KeyboardInterrupt:
        print(f"\n\n⚠️  Reconnaissance interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
