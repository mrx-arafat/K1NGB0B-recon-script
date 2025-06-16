#!/usr/bin/env python3
"""
K1NGB0B Advanced Recon Script - Intelligent Domain Reconnaissance Tool
Author: mrx-arafat (K1NGB0B)
Version: 3.0.0

An advanced, intelligent subdomain discovery and reconnaissance tool for bug bounty hunters and security professionals.
Features:
- Multi-source subdomain enumeration
- Intelligent filtering and validation
- Technology detection
- Port scanning integration
- Advanced reporting
- Smart rate limiting
- Concurrent processing
"""

import os
import sys
import time
import json
import asyncio
import subprocess
import threading
import concurrent.futures
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional
from urllib.parse import urlparse
import re
import socket
from datetime import datetime

try:
    import aiohttp
    import dns.resolver
    AIOHTTP_AVAILABLE = True
    DNS_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    DNS_AVAILABLE = False


# Configuration Constants
MAX_CONCURRENT_REQUESTS = 50
REQUEST_TIMEOUT = 30
DNS_TIMEOUT = 10
PORT_SCAN_TIMEOUT = 5
COMMON_PORTS = [80, 443, 8080, 8443, 3000, 8000, 9000, 9443, 8888, 8008]

# SecLists Configuration
SECLISTS_BASE_URL = "https://raw.githubusercontent.com/danielmiessler/SecLists/master"
WORDLISTS_DIR = "./wordlists"

# Smart wordlist mapping based on context
SECLISTS_WORDLISTS = {
    'subdomains': {
        'dns': f"{SECLISTS_BASE_URL}/Discovery/DNS/subdomains-top1million-5000.txt",
        'dns_short': f"{SECLISTS_BASE_URL}/Discovery/DNS/subdomains-top1million-110000.txt",
        'bitquark': f"{SECLISTS_BASE_URL}/Discovery/DNS/bitquark-subdomains-top100000.txt"
    },
    'directories': {
        'common': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/common.txt",
        'big': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/big.txt",
        'directory-list': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/directory-list-2.3-medium.txt"
    },
    'api': {
        'endpoints': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/api/api-endpoints.txt",
        'objects': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/api/objects.txt",
        'graphql': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/graphql.txt"
    },
    'files': {
        'backup': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/backup-files.txt",
        'logs': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/Logins.fuzz.txt",
        'config': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/web-config.txt"
    },
    'parameters': {
        'common': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/burp-parameter-names.txt",
        'top': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/parameter-names.txt"
    },
    'admin': {
        'panels': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/admin-panels.txt",
        'paths': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/AdminPanels.fuzz.txt"
    }
}

# Built-in fallback wordlists
FALLBACK_WORDLISTS = {
    'subdomains': ['api', 'www', 'mail', 'ftp', 'admin', 'test', 'dev', 'staging', 'beta', 'demo', 'app', 'portal', 'secure', 'vpn'],
    'directories': ['admin', 'api', 'backup', 'config', 'test', 'dev', 'staging', 'login', 'dashboard', 'panel'],
    'api': ['api', 'v1', 'v2', 'rest', 'graphql', 'endpoints', 'swagger', 'docs'],
    'files': ['backup', 'config', 'log', 'admin', 'test', 'debug']
}

def print_banner():
    """Print the enhanced tool banner."""
    banner = """
██╗  ██╗ ██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ██████╗
██║ ██╔╝███║████╗  ██║██╔════╝ ██╔══██╗██╔═████╗██╔══██╗
█████╔╝ ╚██║██╔██╗ ██║██║  ███╗██████╔╝██║██╔██║██████╔╝
██╔═██╗  ██║██║╚██╗██║██║   ██║██╔══██╗████╔╝██║██╔══██╗
██║  ██╗ ██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝██████╔╝
╚═╝  ╚═╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝

    🎯 K1NGB0B Advanced Recon Script v3.0 - Intelligent Domain Reconnaissance
    👤 Author: mrx-arafat (K1NGB0B)
    🔗 https://github.com/mrx-arafat/k1ngb0b-recon

    🚀 Enhanced Features:
    • Multi-source subdomain enumeration
    • Intelligent filtering & validation
    • Technology detection & fingerprinting
    • Port scanning & service detection
    • Advanced concurrent processing
    • Smart rate limiting & error handling
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


def create_directories(domain: str) -> Dict[str, str]:
    """Create enhanced organized directory structure for results."""
    sanitized_domain = domain.replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(f"./{sanitized_domain}_results_{timestamp}")

    directories = {
        'base': str(base_dir),
        'raw': str(base_dir / 'raw'),
        'processed': str(base_dir / 'processed'),
        'reports': str(base_dir / 'reports'),
        'screenshots': str(base_dir / 'screenshots'),
        'ports': str(base_dir / 'ports'),
        'technologies': str(base_dir / 'technologies'),
        'vulnerabilities': str(base_dir / 'vulnerabilities')
    }

    # Create directories
    for dir_path in directories.values():
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    return directories


async def download_wordlist(url: str, filename: str) -> str:
    """Download a wordlist from SecLists if not already cached."""
    # Create wordlists directory
    os.makedirs(WORDLISTS_DIR, exist_ok=True)

    local_path = os.path.join(WORDLISTS_DIR, filename)

    # Check if already downloaded
    if os.path.exists(local_path):
        print(f"   ✅ Using cached wordlist: {filename}")
        return local_path

    if not AIOHTTP_AVAILABLE:
        print(f"   ⚠️  Cannot download wordlist (aiohttp not available): {filename}")
        return None

    try:
        print(f"   📥 Downloading wordlist: {filename}")
        timeout = aiohttp.ClientTimeout(total=120)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()

                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    # Count lines
                    line_count = len([line for line in content.split('\n') if line.strip()])
                    print(f"   ✅ Downloaded {filename} ({line_count} entries)")
                    return local_path
                else:
                    print(f"   ❌ Failed to download {filename}: HTTP {response.status}")
                    return None

    except Exception as e:
        print(f"   ❌ Error downloading {filename}: {e}")
        return None


def get_fallback_wordlist(category: str, subcategory: str = None) -> str:
    """Create a fallback wordlist file from built-in lists."""
    os.makedirs(WORDLISTS_DIR, exist_ok=True)

    filename = f"fallback_{category}_{subcategory or 'default'}.txt"
    local_path = os.path.join(WORDLISTS_DIR, filename)

    if os.path.exists(local_path):
        return local_path

    words = FALLBACK_WORDLISTS.get(category, [])

    with open(local_path, 'w') as f:
        for word in words:
            f.write(f"{word}\n")

    print(f"   ✅ Created fallback wordlist: {filename} ({len(words)} entries)")
    return local_path


async def get_smart_wordlist(category: str, subcategory: str = 'common', size: str = 'medium') -> str:
    """Intelligently get the best wordlist for the given context."""
    print(f"   🧠 Getting smart wordlist for {category}/{subcategory}")

    # Determine the best wordlist based on context
    if category in SECLISTS_WORDLISTS:
        wordlist_options = SECLISTS_WORDLISTS[category]

        # Smart selection based on subcategory and size
        if subcategory in wordlist_options:
            url = wordlist_options[subcategory]
            filename = f"{category}_{subcategory}.txt"
        elif 'common' in wordlist_options:
            url = wordlist_options['common']
            filename = f"{category}_common.txt"
        else:
            # Get first available option
            first_key = list(wordlist_options.keys())[0]
            url = wordlist_options[first_key]
            filename = f"{category}_{first_key}.txt"

        # Try to download
        wordlist_path = await download_wordlist(url, filename)

        if wordlist_path:
            return wordlist_path

    # Fallback to built-in wordlist
    print(f"   ⚠️  Using fallback wordlist for {category}")
    return get_fallback_wordlist(category, subcategory)


def detect_target_context(domain: str, technologies: Dict = None) -> Dict[str, List[str]]:
    """Detect the context of the target to determine optimal wordlists."""
    contexts = {
        'directories': ['common'],
        'files': ['backup'],
        'parameters': ['common']
    }

    # Analyze domain for hints
    domain_lower = domain.lower()

    # API detection
    if 'api' in domain_lower or (technologies and any('api' in str(tech).lower() for tech in technologies.values())):
        contexts['api'] = ['endpoints', 'objects']
        contexts['directories'].append('api')

    # Admin panel detection
    if 'admin' in domain_lower or 'panel' in domain_lower:
        contexts['admin'] = ['panels', 'paths']
        contexts['directories'].append('admin')

    # Technology-specific contexts
    if technologies:
        tech_str = str(technologies).lower()

        # WordPress
        if 'wordpress' in tech_str:
            contexts['directories'].extend(['wordpress', 'wp'])
            contexts['files'].append('wordpress')

        # GraphQL
        if 'graphql' in tech_str:
            contexts['api'] = ['graphql', 'endpoints']

        # React/Angular/Vue (SPA)
        if any(framework in tech_str for framework in ['react', 'angular', 'vue']):
            contexts['files'].append('spa')
            contexts['directories'].append('spa')

    return contexts


def is_valid_subdomain(subdomain: str, domain: str) -> bool:
    """Enhanced subdomain validation with intelligent filtering."""
    if not subdomain or not domain:
        return False

    # Remove protocol if present
    if subdomain.startswith(('http://', 'https://')):
        subdomain = urlparse(subdomain).netloc

    # Basic validation
    if not subdomain.endswith(domain) and domain not in subdomain:
        return False

    # Filter out invalid patterns
    invalid_patterns = [
        r'^\*\.',  # Wildcard subdomains
        r'\s',     # Contains spaces
        r'[<>]',   # Contains HTML brackets
        r'^\d+\.\d+\.\d+\.\d+$',  # IP addresses
        r'localhost',
        r'127\.0\.0\.1',
        r'0\.0\.0\.0'
    ]

    for pattern in invalid_patterns:
        if re.search(pattern, subdomain):
            return False

    return True


def resolve_dns(domain: str) -> Dict[str, List[str]]:
    """Resolve DNS records for a domain."""
    dns_records = {'A': [], 'AAAA': [], 'CNAME': [], 'MX': [], 'TXT': []}

    if not DNS_AVAILABLE:
        return dns_records

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = DNS_TIMEOUT

        for record_type in dns_records.keys():
            try:
                answers = resolver.resolve(domain, record_type)
                dns_records[record_type] = [str(answer) for answer in answers]
            except:
                continue

    except Exception as e:
        print(f"   ⚠️  DNS resolution failed for {domain}: {e}")

    return dns_records


async def check_port_async(host: str, port: int) -> bool:
    """Asynchronously check if a port is open."""
    try:
        future = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(future, timeout=PORT_SCAN_TIMEOUT)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False


async def scan_common_ports(host: str) -> List[int]:
    """Scan common ports on a host."""
    open_ports = []

    tasks = []
    for port in COMMON_PORTS:
        task = check_port_async(host, port)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if result is True:
            open_ports.append(COMMON_PORTS[i])

    return open_ports


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
    """Run assetfinder for subdomain discovery with enhanced filtering."""
    print("🔍 Running AssetFinder...")

    if not check_tool('assetfinder'):
        print("   ⚠️  AssetFinder not found, skipping...")
        return []

    success, output, error = run_command(['assetfinder', '-subs-only', domain])

    if success and output:
        raw_subdomains = [line.strip() for line in output.split('\n') if line.strip()]

        # Enhanced filtering
        valid_subdomains = []
        for subdomain in raw_subdomains:
            if is_valid_subdomain(subdomain, domain):
                valid_subdomains.append(subdomain.lower())

        # Save raw output
        with open(output_file, 'w') as f:
            f.write(output)

        print(f"   ✅ Found {len(raw_subdomains)} raw subdomains, {len(valid_subdomains)} valid")
        return valid_subdomains
    else:
        print(f"   ❌ Failed: {error}")
        return []


def run_subfinder(domain: str, output_file: str) -> List[str]:
    """Run Subfinder for subdomain discovery with enhanced options."""
    print("🔍 Running Subfinder...")

    if not check_tool('subfinder'):
        print("   ⚠️  Subfinder not found, skipping...")
        return []

    # Enhanced subfinder command with more sources
    command = ['subfinder', '-d', domain, '-o', output_file, '-silent', '-all']
    success, output, error = run_command(command, timeout=600)  # Longer timeout for comprehensive scan

    if success:
        try:
            with open(output_file, 'r') as f:
                raw_subdomains = [line.strip() for line in f if line.strip()]

            # Enhanced filtering
            valid_subdomains = []
            for subdomain in raw_subdomains:
                if is_valid_subdomain(subdomain, domain):
                    valid_subdomains.append(subdomain.lower())

            print(f"   ✅ Found {len(raw_subdomains)} raw subdomains, {len(valid_subdomains)} valid")
            return valid_subdomains
        except Exception as e:
            print(f"   ❌ Failed to read output file: {e}")
            return []
    else:
        print(f"   ❌ Failed: {error}")
        return []


async def run_amass(domain: str, output_file: str) -> List[str]:
    """Run Amass for comprehensive subdomain discovery."""
    print("🔍 Running Amass (if available)...")

    if not check_tool('amass'):
        print("   ⚠️  Amass not found, skipping...")
        return []

    try:
        # Run amass enum with passive mode for faster results
        command = ['amass', 'enum', '-passive', '-d', domain, '-o', output_file]
        success, output, error = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await success.communicate()

        if success.returncode == 0:
            try:
                with open(output_file, 'r') as f:
                    raw_subdomains = [line.strip() for line in f if line.strip()]

                valid_subdomains = []
                for subdomain in raw_subdomains:
                    if is_valid_subdomain(subdomain, domain):
                        valid_subdomains.append(subdomain.lower())

                print(f"   ✅ Amass found {len(raw_subdomains)} raw subdomains, {len(valid_subdomains)} valid")
                return valid_subdomains
            except Exception as e:
                print(f"   ❌ Failed to read Amass output: {e}")
                return []
        else:
            print(f"   ❌ Amass failed: {stderr.decode()}")
            return []

    except Exception as e:
        print(f"   ❌ Amass execution failed: {e}")
        return []


async def run_smart_wordlist_enumeration(domain: str, output_file: str, technologies: Dict = None) -> List[str]:
    """Run intelligent wordlist-based subdomain enumeration using SecLists."""
    print("🔍 Running smart wordlist enumeration...")

    # Get smart wordlist for subdomains
    wordlist_path = await get_smart_wordlist('subdomains', 'dns', 'medium')

    if not wordlist_path or not os.path.exists(wordlist_path):
        print("   ⚠️  No wordlist available, using fallback")
        return run_fallback_wordlist_enumeration(domain, output_file)

    subdomains = []

    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        # Generate subdomains
        for word in words[:5000]:  # Limit to first 5000 for performance
            if word and not word.startswith('.'):
                subdomain = f"{word}.{domain}"
                if is_valid_subdomain(subdomain, domain):
                    subdomains.append(subdomain.lower())

        # Add technology-specific subdomains
        if technologies:
            tech_contexts = detect_target_context(domain, technologies)
            for context_type, subcategories in tech_contexts.items():
                if context_type == 'api':
                    # Add API-specific subdomains
                    api_words = ['api', 'rest', 'graphql', 'v1', 'v2', 'v3', 'endpoints']
                    for word in api_words:
                        subdomain = f"{word}.{domain}"
                        if subdomain not in subdomains:
                            subdomains.append(subdomain)

        # Save to file
        with open(output_file, 'w') as f:
            for subdomain in subdomains:
                f.write(f"{subdomain}\n")

        print(f"   ✅ Generated {len(subdomains)} smart wordlist-based subdomains")
        return subdomains

    except Exception as e:
        print(f"   ❌ Error processing wordlist: {e}")
        return run_fallback_wordlist_enumeration(domain, output_file)


def run_fallback_wordlist_enumeration(domain: str, output_file: str) -> List[str]:
    """Fallback wordlist enumeration using built-in lists."""
    print("   🔄 Using fallback wordlist enumeration...")

    subdomains = []
    for word in FALLBACK_WORDLISTS['subdomains']:
        subdomain = f"{word}.{domain}"
        subdomains.append(subdomain)

    # Save to file
    with open(output_file, 'w') as f:
        for subdomain in subdomains:
            f.write(f"{subdomain}\n")

    print(f"   ✅ Generated {len(subdomains)} fallback wordlist-based subdomains")
    return subdomains


# Legacy function for backward compatibility
def run_wordlist_enumeration(domain: str, output_file: str) -> List[str]:
    """Legacy wordlist enumeration function."""
    return run_fallback_wordlist_enumeration(domain, output_file)


async def run_crt_sh(domain: str, output_file: str) -> List[str]:
    """Enhanced Certificate Transparency lookup with multiple sources."""
    print("🔍 Checking Certificate Transparency sources...")

    if not AIOHTTP_AVAILABLE:
        print("   ⚠️  aiohttp not installed, skipping CT lookup...")
        return []

    all_subdomains = set()

    # Multiple CT sources
    ct_sources = [
        f"https://crt.sh/?q={domain}&output=json",
        f"https://crt.sh/?q=%.{domain}&output=json"
    ]

    try:
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for url in ct_sources:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()

                            for entry in data:
                                name_value = entry.get('name_value', '')
                                for subdomain in name_value.split('\n'):
                                    subdomain = subdomain.strip().replace('*.', '')
                                    if subdomain and is_valid_subdomain(subdomain, domain):
                                        all_subdomains.add(subdomain.lower())
                        else:
                            print(f"   ⚠️  CT source failed: HTTP {response.status}")

                except Exception as e:
                    print(f"   ⚠️  CT source error: {e}")
                    continue

        subdomain_list = list(all_subdomains)

        # Save results
        with open(output_file, 'w') as f:
            for subdomain in subdomain_list:
                f.write(f"{subdomain}\n")

        print(f"   ✅ Certificate Transparency found {len(subdomain_list)} valid subdomains")
        return subdomain_list

    except Exception as e:
        print(f"   ❌ Certificate Transparency failed: {e}")
        return []


async def detect_technologies(url: str) -> Dict[str, List[str]]:
    """Detect technologies used by a website."""
    technologies = {
        'web_servers': [],
        'frameworks': [],
        'cms': [],
        'languages': [],
        'databases': [],
        'cdn': []
    }

    if not AIOHTTP_AVAILABLE:
        return technologies

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True) as response:
                headers = response.headers
                content = await response.text()

                # Analyze headers
                server = headers.get('Server', '').lower()
                if 'nginx' in server:
                    technologies['web_servers'].append('Nginx')
                elif 'apache' in server:
                    technologies['web_servers'].append('Apache')
                elif 'iis' in server:
                    technologies['web_servers'].append('IIS')

                # Check for frameworks and technologies
                x_powered_by = headers.get('X-Powered-By', '').lower()
                if 'php' in x_powered_by:
                    technologies['languages'].append('PHP')
                elif 'asp.net' in x_powered_by:
                    technologies['frameworks'].append('ASP.NET')

                # Analyze content for more technologies
                content_lower = content.lower()

                # CMS Detection
                if 'wp-content' in content_lower or 'wordpress' in content_lower:
                    technologies['cms'].append('WordPress')
                elif 'drupal' in content_lower:
                    technologies['cms'].append('Drupal')
                elif 'joomla' in content_lower:
                    technologies['cms'].append('Joomla')

                # Framework Detection
                if 'react' in content_lower:
                    technologies['frameworks'].append('React')
                elif 'angular' in content_lower:
                    technologies['frameworks'].append('Angular')
                elif 'vue' in content_lower:
                    technologies['frameworks'].append('Vue.js')

                # CDN Detection
                if 'cloudflare' in headers.get('Server', '').lower():
                    technologies['cdn'].append('Cloudflare')
                elif 'amazonaws' in headers.get('Via', '').lower():
                    technologies['cdn'].append('AWS CloudFront')

    except Exception as e:
        print(f"   ⚠️  Technology detection failed for {url}: {e}")

    return technologies


async def check_live_subdomains_advanced(subdomains: List[str], directories: Dict[str, str]) -> Dict[str, any]:
    """Advanced live subdomain checking with detailed analysis."""
    print("🔍 Performing advanced live subdomain analysis...")

    if not subdomains:
        print("   ⚠️  No subdomains to check")
        return {'live': [], 'dead': [], 'technologies': {}, 'ports': {}}

    live_subdomains = []
    dead_subdomains = []
    technologies_data = {}
    ports_data = {}

    # First, use httpx for basic live checking
    if check_tool('httpx'):
        temp_file = "temp_subdomains.txt"
        httpx_output = f"{directories['processed']}/httpx_results.txt"

        with open(temp_file, 'w') as f:
            for subdomain in subdomains:
                f.write(f"{subdomain}\n")

        # Enhanced httpx command with more options
        command = [
            'httpx', '-list', temp_file, '-o', httpx_output,
            '-silent', '-status-code', '-title', '-tech-detect',
            '-threads', '50', '-timeout', '10'
        ]

        success, output, error = run_command(command, timeout=600)

        # Clean up temp file
        try:
            os.remove(temp_file)
        except:
            pass

        if success:
            try:
                with open(httpx_output, 'r') as f:
                    for line in f:
                        if line.strip():
                            live_subdomains.append(line.strip().split()[0])
            except Exception as e:
                print(f"   ⚠️  Failed to read httpx output: {e}")

    # Advanced analysis for live subdomains
    if live_subdomains:
        print(f"   🔍 Analyzing {len(live_subdomains)} live subdomains...")

        # Limit concurrent requests to avoid overwhelming targets
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def analyze_subdomain(subdomain):
            async with semaphore:
                try:
                    # Clean URL format
                    if not subdomain.startswith(('http://', 'https://')):
                        url = f"https://{subdomain}"
                    else:
                        url = subdomain

                    # Technology detection
                    tech_data = await detect_technologies(url)
                    if any(tech_data.values()):
                        technologies_data[subdomain] = tech_data

                    # Port scanning for interesting subdomains
                    hostname = urlparse(url).netloc or subdomain
                    open_ports = await scan_common_ports(hostname)
                    if open_ports:
                        ports_data[hostname] = open_ports

                except Exception as e:
                    print(f"   ⚠️  Analysis failed for {subdomain}: {e}")

        # Run analysis concurrently
        tasks = [analyze_subdomain(sub) for sub in live_subdomains[:100]]  # Limit to first 100
        await asyncio.gather(*tasks, return_exceptions=True)

    # Determine dead subdomains
    dead_subdomains = [sub for sub in subdomains if sub not in live_subdomains]

    # Save detailed results
    results = {
        'live': live_subdomains,
        'dead': dead_subdomains,
        'technologies': technologies_data,
        'ports': ports_data
    }

    # Save technologies data
    if technologies_data:
        tech_file = f"{directories['technologies']}/detected_technologies.json"
        with open(tech_file, 'w') as f:
            json.dump(technologies_data, f, indent=2)

    # Save ports data
    if ports_data:
        ports_file = f"{directories['ports']}/open_ports.json"
        with open(ports_file, 'w') as f:
            json.dump(ports_data, f, indent=2)

    print(f"   ✅ Found {len(live_subdomains)} live subdomains")
    print(f"   🔍 Detected technologies on {len(technologies_data)} subdomains")
    print(f"   🔍 Found open ports on {len(ports_data)} hosts")

    return results


def check_live_subdomains(subdomains: List[str], output_file: str) -> List[str]:
    """Legacy function for backward compatibility."""
    print("🔍 Checking live subdomains (basic mode)...")

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
    """Run the enhanced reconnaissance process with advanced features."""
    print(f"\n🎯 Starting advanced reconnaissance for: {domain}")
    print("=" * 80)

    start_time = time.time()

    # Create enhanced directory structure
    directories = create_directories(domain)
    print(f"📁 Results will be saved to: {directories['base']}")

    # Phase 1: Subdomain Discovery
    print(f"\n🔍 Phase 1: Multi-source subdomain discovery...")

    all_subdomains = []
    source_stats = {}

    # Run AssetFinder
    assetfinder_results = run_assetfinder(domain, f"{directories['raw']}/assetfinder.txt")
    all_subdomains.extend(assetfinder_results)
    source_stats['AssetFinder'] = len(assetfinder_results)

    # Run Subfinder
    subfinder_results = run_subfinder(domain, f"{directories['raw']}/subfinder.txt")
    all_subdomains.extend(subfinder_results)
    source_stats['Subfinder'] = len(subfinder_results)

    # Run Certificate Transparency
    crt_results = await run_crt_sh(domain, f"{directories['raw']}/crt.txt")
    all_subdomains.extend(crt_results)
    source_stats['Certificate Transparency'] = len(crt_results)

    # Run Amass (if available)
    amass_results = await run_amass(domain, f"{directories['raw']}/amass.txt")
    all_subdomains.extend(amass_results)
    source_stats['Amass'] = len(amass_results)

    # Run smart wordlist enumeration
    wordlist_results = await run_smart_wordlist_enumeration(domain, f"{directories['raw']}/wordlist.txt")
    all_subdomains.extend(wordlist_results)
    source_stats['Smart Wordlist'] = len(wordlist_results)

    # Phase 2: Intelligent Filtering and Deduplication
    print(f"\n🧠 Phase 2: Intelligent filtering and deduplication...")
    unique_subdomains = deduplicate_subdomains(all_subdomains)

    # Save all unique subdomains
    unique_file = f"{directories['processed']}/all_subdomains.txt"
    with open(unique_file, 'w') as f:
        for subdomain in unique_subdomains:
            f.write(f"{subdomain}\n")

    # Phase 3: Advanced Live Analysis
    print(f"\n🔍 Phase 3: Advanced live subdomain analysis...")
    live_analysis = await check_live_subdomains_advanced(unique_subdomains, directories)

    # Phase 4: DNS Analysis
    print(f"\n🔍 Phase 4: DNS analysis for live subdomains...")
    dns_data = {}
    for subdomain in live_analysis['live'][:50]:  # Limit to first 50 for performance
        dns_records = resolve_dns(subdomain)
        if any(dns_records.values()):
            dns_data[subdomain] = dns_records

    # Save DNS data
    if dns_data:
        dns_file = f"{directories['processed']}/dns_records.json"
        with open(dns_file, 'w') as f:
            json.dump(dns_data, f, indent=2)

    # Phase 5: Generate Enhanced Report
    duration = time.time() - start_time

    enhanced_report = {
        'target_domain': domain,
        'timestamp': datetime.now().isoformat(),
        'scan_duration_seconds': round(duration, 2),
        'source_statistics': source_stats,
        'total_subdomains_found': len(all_subdomains),
        'unique_subdomains': len(unique_subdomains),
        'live_subdomains': len(live_analysis['live']),
        'dead_subdomains': len(live_analysis['dead']),
        'technologies_detected': len(live_analysis['technologies']),
        'hosts_with_open_ports': len(live_analysis['ports']),
        'dns_records_found': len(dns_data),
        'discovered_subdomains': unique_subdomains,
        'live_subdomains_list': live_analysis['live'],
        'technology_summary': live_analysis['technologies'],
        'port_summary': live_analysis['ports'],
        'dns_summary': dns_data
    }

    # Save enhanced JSON report
    with open(f"{directories['reports']}/enhanced_report.json", 'w') as f:
        json.dump(enhanced_report, f, indent=2)

    # Print enhanced results
    print(f"\n📊 Enhanced Reconnaissance Results:")
    print(f"   🎯 Target: {domain}")
    print(f"   ⏱️  Duration: {duration:.1f} seconds")
    print(f"   📈 Total found: {len(all_subdomains)} subdomains")
    print(f"   🔗 Unique: {len(unique_subdomains)} subdomains")
    print(f"   🟢 Live: {len(live_analysis['live'])} subdomains")
    print(f"   🔴 Dead: {len(live_analysis['dead'])} subdomains")
    print(f"   🛠️  Technologies: {len(live_analysis['technologies'])} detected")
    print(f"   🔌 Open ports: {len(live_analysis['ports'])} hosts")
    print(f"   🌐 DNS records: {len(dns_data)} analyzed")

    # Print source statistics
    print(f"\n📊 Source Statistics:")
    for source, count in source_stats.items():
        print(f"   • {source}: {count} subdomains")

    # Print top live subdomains with status
    if live_analysis['live']:
        print(f"\n🎯 Top Live Subdomains:")
        for i, subdomain in enumerate(live_analysis['live'][:15]):
            tech_info = ""
            if subdomain in live_analysis['technologies']:
                techs = live_analysis['technologies'][subdomain]
                tech_list = []
                for category, items in techs.items():
                    if items:
                        tech_list.extend(items)
                if tech_list:
                    tech_info = f" [{', '.join(tech_list[:3])}]"

            print(f"   🟢 {subdomain}{tech_info}")

        if len(live_analysis['live']) > 15:
            print(f"   ... and {len(live_analysis['live']) - 15} more")

    print(f"\n📁 Enhanced Results saved to:")
    print(f"   📄 All subdomains: {unique_file}")
    print(f"   🟢 Live analysis: {directories['processed']}/")
    print(f"   🛠️  Technologies: {directories['technologies']}/")
    print(f"   🔌 Port scans: {directories['ports']}/")
    print(f"   📊 Enhanced report: {directories['reports']}/enhanced_report.json")

    print(f"\n✅ Advanced reconnaissance completed successfully!")
    print(f"🚀 Ready for next phase analysis with k1ngb0b_after_recon.py")


def check_dependencies():
    """Check if all required and optional dependencies are installed."""
    missing = []
    optional_missing = []

    # Check Python packages
    if not AIOHTTP_AVAILABLE:
        missing.append("aiohttp (Python package)")

    if not DNS_AVAILABLE:
        optional_missing.append("dnspython (Python package)")

    # Check required system tools
    required_tools = {
        'assetfinder': 'AssetFinder (Go tool)',
        'subfinder': 'Subfinder (Go tool)',
        'httpx': 'httpx (Go tool)',
        'anew': 'anew (Go tool)'
    }

    # Check optional tools
    optional_tools = {
        'amass': 'Amass (Go tool)',
        'nmap': 'Nmap (Network scanner)',
        'nuclei': 'Nuclei (Vulnerability scanner)',
        'waybackurls': 'Waybackurls (Go tool)',
        'gau': 'GetAllUrls (Go tool)'
    }

    for tool, description in required_tools.items():
        success, _, _ = run_command(['which', tool])
        if not success:
            missing.append(description)

    for tool, description in optional_tools.items():
        success, _, _ = run_command(['which', tool])
        if not success:
            optional_missing.append(description)

    return missing, optional_missing


def main():
    """Enhanced main function with better dependency management."""
    print_banner()

    print("\n🎯 K1NGB0B Advanced Recon Script - Intelligent Domain Reconnaissance")
    print("=" * 80)

    # Check dependencies
    print("\n🔍 Checking dependencies...")
    missing_deps, optional_missing = check_dependencies()

    if missing_deps:
        print(f"\n❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")

        print(f"\n💡 To install all dependencies, run:")
        print(f"   chmod +x install.sh && ./install.sh")
        print(f"\n⚠️  Cannot proceed without required dependencies!")
        return 1

    print("✅ All required dependencies found!")

    if optional_missing:
        print(f"\n⚠️  Optional tools not found (enhanced features may be limited):")
        for dep in optional_missing:
            print(f"   • {dep}")
        print(f"\n💡 Install optional tools for enhanced capabilities")

    try:
        print(f"\n🎯 Target Selection:")
        domain = input("🔍 Enter target domain (e.g., tesla.com): ").strip()

        if not domain:
            print("❌ No domain provided!")
            return 1

        if not validate_domain(domain):
            print(f"❌ Invalid domain: {domain}")
            return 1

        # Remove protocol if present
        if domain.startswith(('http://', 'https://')):
            domain = domain.split('://')[1]

        print(f"✅ Target domain validated: {domain}")

        # Confirmation
        print(f"\n⚠️  About to start comprehensive reconnaissance on: {domain}")
        confirm = input("Continue? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Reconnaissance cancelled by user")
            return 0

        # Run enhanced reconnaissance
        print(f"\n🚀 Starting enhanced reconnaissance...")
        asyncio.run(run_reconnaissance(domain))

        print(f"\n🎉 Reconnaissance completed! Check the results directory.")
        print(f"💡 Next: Run 'python3 k1ngb0b_after_recon.py' for advanced analysis")

        return 0

    except KeyboardInterrupt:
        print(f"\n\n⚠️  Reconnaissance interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
