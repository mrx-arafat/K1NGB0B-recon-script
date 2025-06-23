#!/usr/bin/env python3
"""
K1NGB0B After Recon Script - Advanced Post-Reconnaissance Analysis
Author: mrx-arafat (K1NGB0B)
Version: 1.0.0

Advanced post-reconnaissance analysis tool for deeper security assessment.
Features:
- Vulnerability scanning with Nuclei
- Directory/file enumeration
- Parameter discovery
- Technology-specific testing
- Screenshot capture
- Advanced reporting
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import signal
import threading
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import glob
import psutil

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# Professional Configuration for VPS Deployment
MAX_CONCURRENT_SCANS = 15  # Optimized for VPS
SCAN_TIMEOUT = 600  # 10 minutes
NUCLEI_TIMEOUT = 1800  # 30 minutes for comprehensive scans
SCREENSHOT_TIMEOUT = 300  # 5 minutes
REQUEST_TIMEOUT = 30
PROCESS_CHECK_INTERVAL = 30  # Check stuck processes every 30 seconds

# SecLists Configuration
SECLISTS_BASE_URL = "https://raw.githubusercontent.com/danielmiessler/SecLists/master"
WORDLISTS_DIR = "./wordlists"

# Smart wordlist mapping for post-recon analysis
SECLISTS_WORDLISTS = {
    'directories': {
        'common': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/common.txt",
        'big': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/big.txt",
        'medium': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/directory-list-2.3-medium.txt",
        'small': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/directory-list-2.3-small.txt"
    },
    'api': {
        'endpoints': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/api/api-endpoints.txt",
        'objects': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/api/objects.txt",
        'graphql': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/graphql.txt",
        'swagger': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/swagger.txt"
    },
    'files': {
        'backup': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/backup-files.txt",
        'logs': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/Logins.fuzz.txt",
        'config': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/web-config.txt",
        'sensitive': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/sensitive-files.txt"
    },
    'parameters': {
        'common': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/burp-parameter-names.txt",
        'top': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/parameter-names.txt"
    },
    'admin': {
        'panels': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/admin-panels.txt",
        'paths': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/AdminPanels.fuzz.txt"
    },
    'cms': {
        'wordpress': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/CMS/wordpress.fuzz.txt",
        'drupal': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/CMS/drupal.txt",
        'joomla': f"{SECLISTS_BASE_URL}/Discovery/Web-Content/CMS/joomla.txt"
    }
}

class ProfessionalTimeoutManager:
    """Professional timeout and process management for VPS deployment."""

    def __init__(self):
        self.active_processes = {}
        self.timeout_count = 0
        self.skip_count = 0
        self.manual_commands = []
        self.start_time = time.time()

    def run_with_timeout(self, command: List[str], timeout: int, description: str) -> Tuple[bool, str, str]:
        """Run command with professional timeout handling and process management."""
        try:
            print(f"   🔄 {description}...")

            # Create process with process group for better control
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )

            self.active_processes[description] = {
                'process': process,
                'start_time': time.time(),
                'command': command
            }

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                success = process.returncode == 0

                if success:
                    print(f"   ✅ {description} completed successfully")
                else:
                    print(f"   ⚠️  {description} completed with warnings")

                return success, stdout, stderr

            except subprocess.TimeoutExpired:
                self.timeout_count += 1
                print(f"   ⏰ TIMEOUT: {description} exceeded {timeout//60}m {timeout%60}s")
                print(f"   🔄 Terminating process gracefully...")

                # Professional process termination
                self._terminate_process_group(process, description)

                # Log for manual execution
                manual_cmd = ' '.join(command)
                self.manual_commands.append({
                    'description': description,
                    'command': manual_cmd,
                    'reason': f'Timeout after {timeout}s'
                })

                print(f"   ⚠️  SKIPPED: {description} due to timeout")
                print(f"   📝 Manual command logged for later execution")

                return False, "", f"Timeout after {timeout}s"

        except Exception as e:
            self.skip_count += 1
            print(f"   ❌ ERROR: {description} failed: {e}")

            manual_cmd = ' '.join(command)
            self.manual_commands.append({
                'description': description,
                'command': manual_cmd,
                'reason': str(e)
            })

            print(f"   📝 Manual command logged for later execution")
            return False, "", str(e)

        finally:
            if description in self.active_processes:
                del self.active_processes[description]

    def _terminate_process_group(self, process, description: str):
        """Professionally terminate process group."""
        try:
            if os.name != 'nt':
                # Unix-like systems
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            else:
                # Windows
                process.terminate()

            # Wait for graceful termination
            try:
                process.wait(timeout=10)
                print(f"   ✅ {description} terminated gracefully")
            except subprocess.TimeoutExpired:
                print(f"   💀 Force killing {description}...")
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                else:
                    process.kill()
                process.wait()

        except Exception as e:
            print(f"   ⚠️  Error terminating {description}: {e}")

    def get_summary(self) -> Dict:
        """Get execution summary for reporting."""
        total_time = time.time() - self.start_time
        return {
            'total_execution_time': round(total_time, 2),
            'timeouts': self.timeout_count,
            'skipped': self.skip_count,
            'manual_commands': self.manual_commands,
            'active_processes': len(self.active_processes)
        }

    def save_manual_commands(self, output_dir: str):
        """Save manual commands for later execution."""
        if not self.manual_commands:
            return

        manual_file = os.path.join(output_dir, "manual_commands.json")
        script_file = os.path.join(output_dir, "manual_commands.sh")

        # Save JSON format
        with open(manual_file, 'w') as f:
            json.dump(self.manual_commands, f, indent=2)

        # Save shell script format
        with open(script_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Manual commands that timed out or failed\n")
            f.write("# Review and execute manually as needed\n\n")

            for cmd_info in self.manual_commands:
                f.write(f"# {cmd_info['description']}\n")
                f.write(f"# Reason: {cmd_info['reason']}\n")
                f.write(f"{cmd_info['command']}\n\n")

        os.chmod(script_file, 0o755)
        print(f"   📝 Manual commands saved to {script_file}")


def print_banner():
    """Print the after-recon banner."""
    banner = """
██╗  ██╗ ██╗███╗   ██╗ ██████╗ ██████╗  ██████╗ ██████╗ 
██║ ██╔╝███║████╗  ██║██╔════╝ ██╔══██╗██╔═████╗██╔══██╗
█████╔╝ ╚██║██╔██╗ ██║██║  ███╗██████╔╝██║██╔██║██████╔╝
██╔═██╗  ██║██║╚██╗██║██║   ██║██╔══██╗████╔╝██║██╔══██╗
██║  ██╗ ██║██║ ╚████║╚██████╔╝██████╔╝╚██████╔╝██████╔╝
╚═╝  ╚═╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝ 
                                                         
    🔥 K1NGB0B After Recon v1.0 - Advanced Post-Reconnaissance Analysis
    👤 Author: mrx-arafat (K1NGB0B)
    🔗 https://github.com/mrx-arafat/k1ngb0b-recon
    
    🚀 Advanced Features:
    • Vulnerability scanning with Nuclei
    • Directory & file enumeration
    • Parameter discovery & fuzzing
    • Technology-specific testing
    • Screenshot capture
    • Advanced security analysis
"""
    print(banner)


def find_latest_results() -> Optional[str]:
    """Find the latest reconnaissance results directory."""
    pattern = "./*_results_*"
    result_dirs = glob.glob(pattern)
    
    if not result_dirs:
        return None
    
    # Sort by modification time, get the latest
    latest_dir = max(result_dirs, key=os.path.getmtime)
    return latest_dir


def load_recon_data(results_dir: str) -> Dict:
    """Load reconnaissance data from the results directory."""
    enhanced_report_path = os.path.join(results_dir, "reports", "enhanced_report.json")
    
    if not os.path.exists(enhanced_report_path):
        # Try legacy report
        legacy_report_path = os.path.join(results_dir, "reports", "report.json")
        if os.path.exists(legacy_report_path):
            with open(legacy_report_path, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError("No reconnaissance report found")
    
    with open(enhanced_report_path, 'r') as f:
        return json.load(f)


def check_tool(tool_name: str) -> bool:
    """Check if a tool is available."""
    try:
        result = subprocess.run(['which', tool_name], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


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


async def get_smart_wordlist(category: str, subcategory: str = 'common') -> str:
    """Get the best wordlist for the given context."""
    print(f"   🧠 Getting smart wordlist for {category}/{subcategory}")

    if category in SECLISTS_WORDLISTS:
        wordlist_options = SECLISTS_WORDLISTS[category]

        # Smart selection based on subcategory
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

    print(f"   ⚠️  No wordlist available for {category}/{subcategory}")
    return None


def detect_target_technologies(recon_data: Dict) -> Dict[str, List[str]]:
    """Detect technologies from reconnaissance data to choose optimal wordlists."""
    technologies = recon_data.get('technology_summary', {})
    contexts = {
        'directories': ['common'],
        'files': ['backup'],
        'parameters': ['common']
    }

    if not technologies:
        return contexts

    # Analyze technologies for context
    tech_str = str(technologies).lower()

    # API detection
    if any(keyword in tech_str for keyword in ['api', 'rest', 'graphql', 'swagger']):
        contexts['api'] = ['endpoints', 'objects']
        if 'graphql' in tech_str:
            contexts['api'].append('graphql')

    # CMS detection
    if 'wordpress' in tech_str:
        contexts['cms'] = ['wordpress']
        contexts['directories'].append('wordpress')
    elif 'drupal' in tech_str:
        contexts['cms'] = ['drupal']
    elif 'joomla' in tech_str:
        contexts['cms'] = ['joomla']

    # Admin panel detection
    if any(keyword in tech_str for keyword in ['admin', 'panel', 'dashboard']):
        contexts['admin'] = ['panels', 'paths']

    return contexts


def run_command(command: List[str], timeout: int = SCAN_TIMEOUT) -> tuple:
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


async def run_professional_nuclei_scan(targets: List[str], output_dir: str, timeout_manager: ProfessionalTimeoutManager) -> Dict:
    """Professional Nuclei vulnerability scanning with intelligent timeout management."""
    print("🚨 Running professional Nuclei vulnerability scan...")

    if not check_tool('nuclei'):
        print("   ⚠️  Nuclei not found - SKIPPED")
        print("   📝 Manual installation: go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest")
        print("   📝 Then run: nuclei -update-templates")
        return {}

    if not targets:
        print("   ⚠️  No targets provided for scanning")
        return {}

    # Create target file with smart formatting
    target_file = os.path.join(output_dir, "nuclei_targets.txt")
    with open(target_file, 'w') as f:
        for target in targets:
            if not target.startswith(('http://', 'https://')):
                f.write(f"https://{target}\n")
                f.write(f"http://{target}\n")
            else:
                f.write(f"{target}\n")

    # Professional Nuclei configuration
    output_file = os.path.join(output_dir, "nuclei_results.json")
    stats_file = os.path.join(output_dir, "nuclei_stats.json")

    command = [
        'nuclei', '-list', target_file, '-json', '-o', output_file,
        '-severity', 'low,medium,high,critical', '-silent',
        '-rate-limit', '50',  # Professional rate limiting
        '-timeout', '10',     # Per-request timeout
        '-retries', '2',      # Retry failed requests
        '-stats',             # Enable statistics
        '-stats-json',        # JSON statistics
        '-stats-interval', '30',  # Stats every 30 seconds
        '-update-templates',  # Ensure latest templates
        '-no-color'          # Clean output for parsing
    ]

    print(f"   🔍 Professional scan of {len(targets)} targets")
    print(f"   ⏰ Maximum timeout: {NUCLEI_TIMEOUT//60} minutes")
    print(f"   🛡️  Rate limit: 50 requests/second")
    print(f"   🔄 Retries: 2 per failed request")

    success, output, error = timeout_manager.run_with_timeout(
        command, NUCLEI_TIMEOUT, "Nuclei vulnerability scan"
    )

    results = {}
    vulnerability_count = 0

    if success and os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            vuln = json.loads(line.strip())
                            host = vuln.get('host', 'unknown')
                            if host not in results:
                                results[host] = []
                            results[host].append(vuln)
                            vulnerability_count += 1
                        except json.JSONDecodeError:
                            continue

            print(f"   ✅ Found {vulnerability_count} vulnerabilities on {len(results)} hosts")

            # Generate vulnerability summary
            severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            for host_vulns in results.values():
                for vuln in host_vulns:
                    severity = vuln.get('info', {}).get('severity', 'unknown').lower()
                    if severity in severity_counts:
                        severity_counts[severity] += 1

            print(f"   📊 Severity breakdown: Critical: {severity_counts['critical']}, High: {severity_counts['high']}, Medium: {severity_counts['medium']}, Low: {severity_counts['low']}")

        except Exception as e:
            print(f"   ❌ Failed to parse Nuclei results: {e}")
    elif not success:
        if "timeout" in error.lower():
            print(f"   ⏰ Nuclei scan timed out after {NUCLEI_TIMEOUT//60} minutes")
            print(f"   💡 Consider running with smaller target batches:")
            print(f"   📝 Split targets into groups of 50-100 for better performance")
        else:
            print(f"   ❌ Nuclei scan failed: {error}")

    return results


async def run_smart_directory_enumeration(targets: List[str], output_dir: str, recon_data: Dict = None, timeout_manager: ProfessionalTimeoutManager = None) -> Dict:
    """Run intelligent directory enumeration using context-aware wordlists with professional timeout management."""
    print("🔍 Running smart directory enumeration...")

    if not check_tool('ffuf') and not check_tool('gobuster'):
        print("   ⚠️  No directory enumeration tools found (ffuf/gobuster)")
        print("   📝 Manual installation:")
        print("   📝   FFUF: go install github.com/ffuf/ffuf@latest")
        print("   📝   Gobuster: go install github.com/OJ/gobuster/v3@latest")
        return {}

    # Detect target context for smart wordlist selection
    contexts = detect_target_technologies(recon_data or {})

    results = {}
    tool = 'ffuf' if check_tool('ffuf') else 'gobuster'

    for target in targets[:10]:  # Limit to first 10 targets
        if not target.startswith(('http://', 'https://')):
            target_url = f"https://{target}"
        else:
            target_url = target

        print(f"   🔍 Smart enumeration on {target}")

        # Determine best wordlists for this target
        wordlists_to_use = []

        # Always start with common directories
        common_wordlist = await get_smart_wordlist('directories', 'common')
        if common_wordlist:
            wordlists_to_use.append(('common', common_wordlist))

        # Add context-specific wordlists
        for context_type, subcategories in contexts.items():
            if context_type in ['api', 'admin', 'cms']:
                for subcategory in subcategories:
                    wordlist = await get_smart_wordlist(context_type, subcategory)
                    if wordlist:
                        wordlists_to_use.append((f"{context_type}_{subcategory}", wordlist))

        # If no smart wordlists available, use fallback
        if not wordlists_to_use:
            print(f"   ⚠️  No smart wordlists available, using fallback for {target}")
            wordlists_to_use = [('fallback', '/usr/share/wordlists/dirb/common.txt')]

        target_results = []

        # Run enumeration with each wordlist
        for wordlist_name, wordlist_path in wordlists_to_use:
            if not os.path.exists(wordlist_path):
                print(f"   ⚠️  Wordlist not found: {wordlist_path}")
                continue

            print(f"   📝 Using {wordlist_name} wordlist on {target}")

            output_file = os.path.join(output_dir, f"dirs_{target.replace(':', '_').replace('/', '_')}_{wordlist_name}.txt")

            if tool == 'ffuf':
                command = [
                    'ffuf', '-u', f"{target_url}/FUZZ", '-w', wordlist_path,
                    '-o', output_file, '-of', 'json', '-mc', '200,204,301,302,307,401,403',
                    '-t', '50', '-timeout', '10'
                ]
            else:
                command = [
                    'gobuster', 'dir', '-u', target_url, '-w', wordlist_path,
                    '-o', output_file, '-q', '-t', '50', '--timeout', '10s'
                ]

            # Use professional timeout manager if available
            if timeout_manager:
                success, output, error = timeout_manager.run_with_timeout(
                    command, 600, f"Directory enumeration on {target} with {wordlist_name}"
                )
            else:
                success, output, error = run_command(command, timeout=600)

            if success and os.path.exists(output_file):
                try:
                    if tool == 'ffuf':
                        with open(output_file, 'r') as f:
                            data = json.load(f)
                            wordlist_results = data.get('results', [])
                            target_results.extend(wordlist_results)
                    else:
                        with open(output_file, 'r') as f:
                            wordlist_results = [line.strip() for line in f if line.strip()]
                            target_results.extend(wordlist_results)

                    print(f"   ✅ Found {len(wordlist_results) if isinstance(wordlist_results, list) else 0} paths with {wordlist_name}")

                except Exception as e:
                    print(f"   ⚠️  Failed to parse {wordlist_name} results for {target}: {e}")
            elif not success and "timeout" in error.lower():
                print(f"   ⏰ Directory enumeration timed out for {target} with {wordlist_name}")
                print(f"   💡 Manual command: {' '.join(command)}")

        if target_results:
            results[target] = target_results

    print(f"   ✅ Smart directory enumeration completed on {len(results)} targets")
    return results


# Legacy function for backward compatibility
async def run_directory_enumeration(targets: List[str], output_dir: str) -> Dict:
    """Legacy directory enumeration function."""
    return await run_smart_directory_enumeration(targets, output_dir)


async def capture_screenshots(targets: List[str], output_dir: str, timeout_manager: ProfessionalTimeoutManager = None) -> Dict:
    """Capture screenshots of live targets with professional timeout management."""
    print("🔍 Capturing screenshots...")

    if not check_tool('gowitness') and not check_tool('aquatone'):
        print("   ⚠️  No screenshot tools found (gowitness/aquatone)")
        print("   📝 Manual installation:")
        print("   📝   Gowitness: go install github.com/sensepost/gowitness@latest")
        print("   📝   Aquatone: go install github.com/michenriksen/aquatone@latest")
        return {}

    tool = 'gowitness' if check_tool('gowitness') else 'aquatone'

    # Create target file
    target_file = os.path.join(output_dir, "screenshot_targets.txt")
    with open(target_file, 'w') as f:
        for target in targets:
            if not target.startswith(('http://', 'https://')):
                f.write(f"https://{target}\n")
            else:
                f.write(f"{target}\n")

    screenshot_dir = os.path.join(output_dir, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)

    if tool == 'gowitness':
        command = ['gowitness', 'file', '-f', target_file, '--screenshot-path', screenshot_dir, '--timeout', '30']
    else:
        command = ['aquatone', '-ports', '80,443,8080,8443', '-out', screenshot_dir]

    print(f"   📸 Taking screenshots of {len(targets)} targets...")

    # Use professional timeout manager if available
    if timeout_manager:
        success, _, error = timeout_manager.run_with_timeout(
            command, SCREENSHOT_TIMEOUT, f"Screenshot capture with {tool}"
        )
    else:
        success, _, error = run_command(command, timeout=SCREENSHOT_TIMEOUT)

    results = {}
    if success:
        # Count screenshot files
        screenshot_files = list(Path(screenshot_dir).glob("*.png"))
        results['screenshots_taken'] = len(screenshot_files)
        results['screenshot_dir'] = screenshot_dir
        print(f"   ✅ Captured {len(screenshot_files)} screenshots")
    else:
        if "timeout" in error.lower():
            print(f"   ⏰ Screenshot capture timed out after {SCREENSHOT_TIMEOUT//60} minutes")
            print(f"   💡 Manual command: {' '.join(command)}")
        else:
            print(f"   ❌ Screenshot capture failed: {error}")

    return results


async def run_url_discovery(domain: str, output_dir: str, timeout_manager: ProfessionalTimeoutManager = None) -> Dict:
    """Discover URLs using waybackurls and gau with professional timeout management."""
    print("🔍 Running URL discovery...")

    all_urls = set()

    # Run waybackurls
    if check_tool('waybackurls'):
        print("   🔍 Running waybackurls...")
        if timeout_manager:
            success, output, error = timeout_manager.run_with_timeout(
                ['waybackurls', domain], 300, f"Waybackurls for {domain}"
            )
        else:
            success, output, error = run_command(['waybackurls', domain], timeout=300)

        if success and output:
            urls = [line.strip() for line in output.split('\n') if line.strip()]
            all_urls.update(urls)
            print(f"   ✅ Waybackurls found {len(urls)} URLs")
        elif not success and "timeout" in error.lower():
            print(f"   ⏰ Waybackurls timed out for {domain}")
            print(f"   💡 Manual command: waybackurls {domain}")
    else:
        print("   ⚠️  Waybackurls not found")
        print("   📝 Manual installation: go install github.com/tomnomnom/waybackurls@latest")

    # Run gau
    if check_tool('gau'):
        print("   🔍 Running gau...")
        if timeout_manager:
            success, output, error = timeout_manager.run_with_timeout(
                ['gau', domain], 300, f"GAU for {domain}"
            )
        else:
            success, output, error = run_command(['gau', domain], timeout=300)

        if success and output:
            urls = [line.strip() for line in output.split('\n') if line.strip()]
            all_urls.update(urls)
            print(f"   ✅ GAU found {len(urls)} URLs")
        elif not success and "timeout" in error.lower():
            print(f"   ⏰ GAU timed out for {domain}")
            print(f"   💡 Manual command: gau {domain}")
    else:
        print("   ⚠️  GAU not found")
        print("   📝 Manual installation: go install github.com/lc/gau@latest")

    # Run waymore (enhanced URL discovery)
    if check_tool('waymore'):
        print("   🔍 Running waymore (enhanced URL discovery)...")
        if timeout_manager:
            success, output, error = timeout_manager.run_with_timeout(
                ['waymore', '-i', domain, '--no-subs'], 300, f"Waymore for {domain}"
            )
        else:
            success, output, error = run_command(['waymore', '-i', domain, '--no-subs'], timeout=300)

        if success and output:
            urls = [line.strip() for line in output.split('\n') if line.strip()]
            all_urls.update(urls)
            print(f"   ✅ Waymore found {len(urls)} URLs")
        elif not success and "timeout" in error.lower():
            print(f"   ⏰ Waymore timed out for {domain}")
            print(f"   💡 Manual command: waymore -i {domain} --no-subs")
    else:
        print("   ⚠️  Waymore not found")
        print("   📝 Manual installation: go install github.com/xnl-h4ck3r/waymore@latest")

    # Run katana for deep crawling
    if check_tool('katana'):
        print("   🔍 Running katana (deep crawling)...")
        if timeout_manager:
            success, output, error = timeout_manager.run_with_timeout(
                ['katana', '-u', f'https://{domain}', '-d', '3', '-silent'], 300, f"Katana for {domain}"
            )
        else:
            success, output, error = run_command(['katana', '-u', f'https://{domain}', '-d', '3', '-silent'], timeout=300)

        if success and output:
            urls = [line.strip() for line in output.split('\n') if line.strip()]
            all_urls.update(urls)
            print(f"   ✅ Katana found {len(urls)} URLs")
        elif not success and "timeout" in error.lower():
            print(f"   ⏰ Katana timed out for {domain}")
            print(f"   💡 Manual command: katana -u https://{domain} -d 3 -silent")
    else:
        print("   ⚠️  Katana not found")
        print("   📝 Manual installation: go install github.com/projectdiscovery/katana/cmd/katana@latest")

    # Run hakrawler for additional crawling
    if check_tool('hakrawler'):
        print("   🔍 Running hakrawler...")
        if timeout_manager:
            success, output, error = timeout_manager.run_with_timeout(
                ['hakrawler', '-url', f'https://{domain}', '-depth', '2'], 240, f"Hakrawler for {domain}"
            )
        else:
            success, output, error = run_command(['hakrawler', '-url', f'https://{domain}', '-depth', '2'], timeout=240)

        if success and output:
            urls = [line.strip() for line in output.split('\n') if line.strip()]
            all_urls.update(urls)
            print(f"   ✅ Hakrawler found {len(urls)} URLs")
        elif not success and "timeout" in error.lower():
            print(f"   ⏰ Hakrawler timed out for {domain}")
            print(f"   💡 Manual command: hakrawler -url https://{domain} -depth 2")
    else:
        print("   ⚠️  Hakrawler not found")
        print("   📝 Manual installation: go install github.com/hakluke/hakrawler@latest")

    # Run getJS for JavaScript file discovery
    if check_tool('getJS'):
        print("   🔍 Running getJS (JavaScript discovery)...")
        if timeout_manager:
            success, output, error = timeout_manager.run_with_timeout(
                ['getJS', '--url', f'https://{domain}'], 180, f"GetJS for {domain}"
            )
        else:
            success, output, error = run_command(['getJS', '--url', f'https://{domain}'], timeout=180)

        if success and output:
            js_urls = [line.strip() for line in output.split('\n') if line.strip() and '.js' in line]
            all_urls.update(js_urls)
            print(f"   ✅ GetJS found {len(js_urls)} JS files")
        elif not success and "timeout" in error.lower():
            print(f"   ⏰ GetJS timed out for {domain}")
            print(f"   💡 Manual command: getJS --url https://{domain}")
    else:
        print("   ⚠️  GetJS not found")
        print("   📝 Manual installation: go install github.com/003random/getJS@latest")

    # Deduplicate URLs using uro if available
    if check_tool('uro') and all_urls:
        print("   🔍 Deduplicating URLs with uro...")
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for url in all_urls:
                    f.write(f"{url}\n")
                temp_file = f.name

            success, output, error = run_command(['uro', '-i', temp_file], timeout=60)
            if success and output:
                deduplicated_urls = set()
                for url in output.split('\n'):
                    if url.strip():
                        deduplicated_urls.add(url.strip())
                original_count = len(all_urls)
                all_urls = deduplicated_urls
                print(f"   ✅ URO deduplication: {original_count} → {len(all_urls)} URLs")

            import os
            os.unlink(temp_file)

        except Exception as e:
            print(f"   ❌ URO deduplication failed: {e}")
    else:
        if not check_tool('uro'):
            print("   ⚠️  URO not found - URL deduplication SKIPPED")
            print("   📝 Manual installation: go install github.com/s0md3v/uro@latest")

    # Save URLs
    if all_urls:
        url_file = os.path.join(output_dir, "discovered_urls.txt")
        with open(url_file, 'w') as f:
            for url in sorted(all_urls):
                f.write(f"{url}\n")

        print(f"   ✅ Total unique URLs discovered: {len(all_urls)}")

    return {'urls': list(all_urls), 'count': len(all_urls)}


async def run_smart_api_discovery(targets: List[str], output_dir: str, recon_data: Dict = None) -> Dict:
    """Run intelligent API endpoint discovery using context-aware wordlists."""
    print("🔍 Running smart API discovery...")

    if not check_tool('ffuf') and not check_tool('gobuster'):
        print("   ⚠️  No fuzzing tools found for API discovery")
        return {}

    # Get API-specific wordlists
    api_wordlists = []

    # Download API endpoints wordlist
    endpoints_wordlist = await get_smart_wordlist('api', 'endpoints')
    if endpoints_wordlist:
        api_wordlists.append(('endpoints', endpoints_wordlist))

    # Download API objects wordlist
    objects_wordlist = await get_smart_wordlist('api', 'objects')
    if objects_wordlist:
        api_wordlists.append(('objects', objects_wordlist))

    # Check for GraphQL
    if recon_data and 'graphql' in str(recon_data.get('technology_summary', {})).lower():
        graphql_wordlist = await get_smart_wordlist('api', 'graphql')
        if graphql_wordlist:
            api_wordlists.append(('graphql', graphql_wordlist))

    if not api_wordlists:
        print("   ⚠️  No API wordlists available")
        return {}

    results = {}
    tool = 'ffuf' if check_tool('ffuf') else 'gobuster'

    # Focus on API-likely targets
    api_targets = []
    for target in targets:
        target_lower = target.lower()
        if any(keyword in target_lower for keyword in ['api', 'rest', 'v1', 'v2', 'v3', 'graphql']):
            api_targets.append(target)

    # If no obvious API targets, use first few targets
    if not api_targets:
        api_targets = targets[:5]

    for target in api_targets:
        if not target.startswith(('http://', 'https://')):
            target_url = f"https://{target}"
        else:
            target_url = target

        print(f"   🔍 API discovery on {target}")

        target_results = []

        for wordlist_name, wordlist_path in api_wordlists:
            print(f"   📝 Using {wordlist_name} API wordlist on {target}")

            output_file = os.path.join(output_dir, f"api_{target.replace(':', '_').replace('/', '_')}_{wordlist_name}.txt")

            # Test common API paths
            api_paths = ['/api/FUZZ', '/v1/FUZZ', '/v2/FUZZ', '/rest/FUZZ', '/FUZZ']

            for api_path in api_paths:
                if tool == 'ffuf':
                    command = [
                        'ffuf', '-u', f"{target_url}{api_path}", '-w', wordlist_path,
                        '-o', f"{output_file}_{api_path.replace('/', '_')}", '-of', 'json',
                        '-mc', '200,201,202,204,301,302,307,401,403,405',
                        '-t', '30', '-timeout', '10'
                    ]
                else:
                    command = [
                        'gobuster', 'dir', '-u', f"{target_url}{api_path.replace('/FUZZ', '')}",
                        '-w', wordlist_path, '-o', f"{output_file}_{api_path.replace('/', '_')}",
                        '-q', '-t', '30', '--timeout', '10s'
                    ]

                success, _, _ = run_command(command, timeout=300)

                if success:
                    try:
                        result_file = f"{output_file}_{api_path.replace('/', '_')}"
                        if os.path.exists(result_file):
                            if tool == 'ffuf':
                                with open(result_file, 'r') as f:
                                    data = json.load(f)
                                    path_results = data.get('results', [])
                                    target_results.extend(path_results)
                            else:
                                with open(result_file, 'r') as f:
                                    path_results = [line.strip() for line in f if line.strip()]
                                    target_results.extend(path_results)
                    except Exception as e:
                        print(f"   ⚠️  Failed to parse API results: {e}")

        if target_results:
            results[target] = target_results
            print(f"   ✅ Found {len(target_results)} API endpoints on {target}")

    print(f"   ✅ Smart API discovery completed on {len(results)} targets")
    return results


async def run_parameter_discovery(targets: List[str], output_dir: str, timeout_manager: ProfessionalTimeoutManager = None) -> Dict:
    """Discover parameters using various methods with professional timeout management."""
    print("🔍 Running parameter discovery...")

    results = {}

    # Use paramspider if available
    if check_tool('paramspider'):
        for target in targets[:5]:  # Limit to first 5 targets
            print(f"   🔍 Discovering parameters for {target}")

            output_file = os.path.join(output_dir, f"params_{target.replace(':', '_').replace('/', '_')}.txt")
            command = ['paramspider', '-d', target, '-o', output_file]

            # Use professional timeout manager if available
            if timeout_manager:
                success, _, error = timeout_manager.run_with_timeout(
                    command, 300, f"Parameter discovery for {target}"
                )
            else:
                success, _, error = run_command(command, timeout=300)

            if success and os.path.exists(output_file):
                try:
                    with open(output_file, 'r') as f:
                        params = [line.strip() for line in f if line.strip()]
                    results[target] = params
                    print(f"   ✅ Found {len(params)} parameters for {target}")
                except Exception as e:
                    print(f"   ⚠️  Failed to read parameters for {target}: {e}")
            elif not success and "timeout" in error.lower():
                print(f"   ⏰ Parameter discovery timed out for {target}")
                print(f"   💡 Manual command: paramspider -d {target} -o {output_file}")
    else:
        print("   ⚠️  ParamSpider not found, skipping parameter discovery")
        print("   📝 Manual installation: pip3 install paramspider")

    return results


async def run_advanced_analysis(recon_data: Dict, results_dir: str):
    """Run comprehensive post-reconnaissance analysis with professional timeout management."""
    print(f"\n🔥 Starting professional post-reconnaissance analysis...")
    print("=" * 80)

    start_time = time.time()

    # Initialize professional timeout manager
    timeout_manager = ProfessionalTimeoutManager()

    # Create analysis directories
    analysis_dir = os.path.join(results_dir, "advanced_analysis")
    os.makedirs(analysis_dir, exist_ok=True)

    vuln_dir = os.path.join(analysis_dir, "vulnerabilities")
    dirs_dir = os.path.join(analysis_dir, "directories")
    urls_dir = os.path.join(analysis_dir, "urls")
    params_dir = os.path.join(analysis_dir, "parameters")
    screenshots_dir = os.path.join(analysis_dir, "screenshots")
    reports_dir = os.path.join(analysis_dir, "reports")

    for directory in [vuln_dir, dirs_dir, urls_dir, params_dir, screenshots_dir, reports_dir]:
        os.makedirs(directory, exist_ok=True)

    # Get live subdomains
    live_subdomains = recon_data.get('live_subdomains_list', [])
    domain = recon_data.get('target_domain', '')

    if not live_subdomains:
        print("   ⚠️  No live subdomains found in reconnaissance data")
        return

    print(f"   🎯 Professional analysis of {len(live_subdomains)} live subdomains")
    print(f"   🛡️  VPS-optimized with intelligent timeout management")

    # Phase 1: Professional Vulnerability Scanning
    print(f"\n� Phase 1: Professional vulnerability scanning...")
    vuln_results = await run_professional_nuclei_scan(live_subdomains, vuln_dir, timeout_manager)

    # Phase 2: Smart Directory Enumeration
    print(f"\n� Phase 2: Smart directory enumeration...")
    dir_results = await run_smart_directory_enumeration(live_subdomains, dirs_dir, recon_data, timeout_manager)

    # Phase 3: Smart API Discovery
    print(f"\n� Phase 3: Smart API discovery...")
    api_results = await run_smart_api_discovery(live_subdomains, dirs_dir, recon_data)

    # Phase 4: URL Discovery
    print(f"\n� Phase 4: URL discovery...")
    url_results = await run_url_discovery(domain, urls_dir, timeout_manager)

    # Phase 5: Parameter Discovery
    print(f"\n� Phase 5: Parameter discovery...")
    param_results = await run_parameter_discovery(live_subdomains, params_dir, timeout_manager)

    # Phase 6: Screenshot Capture
    print(f"\n� Phase 6: Screenshot capture...")
    screenshot_results = await capture_screenshots(live_subdomains, screenshots_dir, timeout_manager)

    # Save manual commands for failed/timed out operations
    timeout_manager.save_manual_commands(analysis_dir)

    # Generate comprehensive report with timeout statistics
    duration = time.time() - start_time
    timeout_summary = timeout_manager.get_summary()

    analysis_report = {
        'target_domain': domain,
        'analysis_timestamp': datetime.now().isoformat(),
        'analysis_duration_seconds': round(duration, 2),
        'live_subdomains_analyzed': len(live_subdomains),
        'execution_summary': {
            'total_timeouts': timeout_summary['timeouts'],
            'total_skipped': timeout_summary['skipped'],
            'manual_commands_generated': len(timeout_summary['manual_commands']),
            'active_processes_at_end': timeout_summary['active_processes']
        },
        'vulnerabilities': {
            'hosts_with_vulns': len(vuln_results),
            'total_vulnerabilities': sum(len(vulns) for vulns in vuln_results.values()),
            'details': vuln_results
        },
        'directories': {
            'hosts_enumerated': len(dir_results),
            'details': dir_results
        },
        'api_endpoints': {
            'hosts_with_apis': len(api_results),
            'total_endpoints': sum(len(endpoints) for endpoints in api_results.values()),
            'details': api_results
        },
        'urls': {
            'total_discovered': url_results.get('count', 0),
            'sources': ['waybackurls', 'gau']
        },
        'parameters': {
            'hosts_analyzed': len(param_results),
            'details': param_results
        },
        'screenshots': screenshot_results,
        'manual_commands': timeout_summary['manual_commands']
    }

    # Save analysis report
    report_file = os.path.join(analysis_dir, "advanced_analysis_report.json")
    with open(report_file, 'w') as f:
        json.dump(analysis_report, f, indent=2)

    # Print results summary
    print(f"\n📊 Advanced Analysis Results:")
    print(f"   🎯 Target: {domain}")
    print(f"   ⏱️  Duration: {duration:.1f} seconds")
    print(f"   🔍 Subdomains analyzed: {len(live_subdomains)}")
    print(f"   🚨 Vulnerabilities found: {analysis_report['vulnerabilities']['total_vulnerabilities']}")
    print(f"   📁 Directory enumeration: {len(dir_results)} hosts")
    print(f"   🔌 API endpoints discovered: {analysis_report['api_endpoints']['total_endpoints']}")
    print(f"   🔗 URLs discovered: {url_results.get('count', 0)}")
    print(f"   🔧 Parameter discovery: {len(param_results)} hosts")
    print(f"   📸 Screenshots: {screenshot_results.get('screenshots_taken', 0)}")

    # Print vulnerability summary
    if vuln_results:
        print(f"\n🚨 Vulnerability Summary:")
        for host, vulns in list(vuln_results.items())[:10]:
            print(f"   • {host}: {len(vulns)} vulnerabilities")

    # Print API discovery summary
    if api_results:
        print(f"\n🔌 API Discovery Summary:")
        for host, endpoints in list(api_results.items())[:10]:
            print(f"   • {host}: {len(endpoints)} API endpoints")
    if api_results:
        print(f"\n🔌 API Discovery Summary:")
        for host, endpoints in list(api_results.items())[:10]:
            print(f"   • {host}: {len(endpoints)} API endpoints")

    # Print timeout and manual command summary
    if timeout_summary['timeouts'] > 0 or timeout_summary['skipped'] > 0:
        print(f"\n⚠️  Execution Summary:")
        print(f"   ⏰ Timeouts: {timeout_summary['timeouts']}")
        print(f"   ⏭️  Skipped: {timeout_summary['skipped']}")
        print(f"   📝 Manual commands generated: {len(timeout_summary['manual_commands'])}")

        if timeout_summary['manual_commands']:
            print(f"\n📝 Manual Commands for Review:")
            print(f"   📄 JSON format: {analysis_dir}/manual_commands.json")
            print(f"   🔧 Shell script: {analysis_dir}/manual_commands.sh")
            print(f"   💡 Review and execute manually for complete coverage")

    print(f"\n📁 Analysis results saved to: {analysis_dir}")
    print(f"📊 Detailed report: {report_file}")

    # Professional summary for VPS deployment
    print(f"\n🎯 Professional Bug Bounty Summary:")
    print(f"   🏆 Target: {domain}")
    print(f"   ⏱️  Total time: {duration:.1f}s")
    print(f"   🔍 Subdomains analyzed: {len(live_subdomains)}")
    print(f"   🚨 Critical findings: {analysis_report['vulnerabilities']['total_vulnerabilities']}")
    print(f"   🔌 API endpoints: {analysis_report['api_endpoints']['total_endpoints']}")
    print(f"   📸 Screenshots: {screenshot_results.get('screenshots_taken', 0)}")

    if analysis_report['vulnerabilities']['total_vulnerabilities'] > 0:
        print(f"\n🚨 VULNERABILITIES DETECTED - PRIORITIZE MANUAL REVIEW!")

    print(f"\n✅ Professional analysis completed - Ready for manual verification!")

    return analysis_report


def check_dependencies() -> tuple:
    """Check for post-recon dependencies."""
    required = []
    optional = []

    # Optional but recommended tools - Enhanced with 25 Smart Bug Bounty Tools
    tools = {
        # Critical Analysis Tools
        'nuclei': 'Nuclei (Vulnerability scanner)',
        'ffuf': 'FFUF (Web fuzzer)',
        'httpx': 'HTTPX (HTTP probing)',

        # Directory & Content Discovery
        'gobuster': 'Gobuster (Directory brute-forcer)',
        'katana': 'Katana (High-speed crawler)',
        'hakrawler': 'Hakrawler (Web crawler)',

        # URL & Parameter Discovery
        'waybackurls': 'Waybackurls (URL discovery)',
        'gau': 'GetAllUrls (URL discovery)',
        'waymore': 'Waymore (Enhanced URL discovery)',
        'arjun': 'Arjun (Parameter discovery)',
        'paramspider': 'ParamSpider (Parameter discovery)',
        'getJS': 'GetJS (Extract JS links)',

        # Screenshot & Visual
        'gowitness': 'Gowitness (Screenshot tool)',
        'aquatone': 'Aquatone (Screenshot tool)',

        # URL Manipulation & Filtering
        'qsreplace': 'QSReplace (Query string replacement)',
        'uro': 'URO (URL deduplicator)',
        'anew': 'Anew (Line deduplication)',

        # Intelligence & Search
        'uncover': 'Uncover (Search via Shodan, Censys)',
        'metabigor': 'Metabigor (Intelligence gathering)',

        # Network & Infrastructure
        'naabu': 'Naabu (Fast port scanner)',
        'dnsx': 'DNSX (DNS resolver)',
        'mapcidr': 'MapCIDR (IP/CIDR manipulation)',

        # Pattern Matching & Notification
        'gf': 'GF (Pattern matching)',
        'notify': 'Notify (Send results to Discord/Slack)'
    }

    for tool, description in tools.items():
        if not check_tool(tool):
            optional.append(description)

    return required, optional


def main():
    """Main function for post-reconnaissance analysis."""
    print_banner()

    print("\n🔥 K1NGB0B After Recon - Advanced Post-Reconnaissance Analysis")
    print("=" * 80)

    # Check dependencies
    print("\n🔍 Checking dependencies...")
    required_missing, optional_missing = check_dependencies()

    if required_missing:
        print(f"\n❌ Missing required dependencies:")
        for dep in required_missing:
            print(f"   • {dep}")
        return 1

    if optional_missing:
        print(f"\n⚠️  Optional tools not found (some features may be limited):")
        for dep in optional_missing:
            print(f"   • {dep}")
        print(f"\n💡 Install these tools for enhanced capabilities")
    else:
        print("✅ All analysis tools found!")

    # Find latest reconnaissance results
    print(f"\n🔍 Looking for reconnaissance results...")
    results_dir = find_latest_results()

    if not results_dir:
        print("❌ No reconnaissance results found!")
        print("💡 Run 'python3 k1ngb0b_recon.py' first to generate reconnaissance data")
        return 1

    print(f"✅ Found results directory: {results_dir}")

    try:
        # Load reconnaissance data
        print(f"\n📊 Loading reconnaissance data...")
        recon_data = load_recon_data(results_dir)

        domain = recon_data.get('target_domain', 'unknown')
        live_count = len(recon_data.get('live_subdomains_list', []))

        print(f"✅ Loaded data for domain: {domain}")
        print(f"📈 Live subdomains: {live_count}")

        if live_count == 0:
            print("⚠️  No live subdomains found in reconnaissance data")
            print("💡 Run reconnaissance again or check the target domain")
            return 1

        # Confirmation
        print(f"\n⚠️  About to start advanced analysis on {live_count} live subdomains")
        print(f"🎯 Target: {domain}")
        confirm = input("Continue with advanced analysis? (y/N): ").strip().lower()

        if confirm not in ['y', 'yes']:
            print("❌ Analysis cancelled by user")
            return 0

        # Run advanced analysis
        asyncio.run(run_advanced_analysis(recon_data, results_dir))

        print(f"\n🎉 Advanced analysis completed successfully!")
        print(f"📁 Check the 'advanced_analysis' directory in {results_dir}")

        return 0

    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
