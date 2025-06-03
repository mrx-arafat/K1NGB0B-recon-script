"""
Subdomain discovery module for K1NGB0B Recon Script.
"""

import asyncio
import aiohttp
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set, Dict, Optional, Callable
from pathlib import Path
import subprocess

from .config import Config
from .utils import (
    Logger, run_command, check_tool_availability, 
    deduplicate_subdomains, read_file_lines, write_file_lines,
    append_file_lines
)


class SubdomainDiscovery:
    """Main class for subdomain discovery operations."""
    
    def __init__(self, config: Config, target_domain: str, output_dirs: Dict[str, str]):
        self.config = config
        self.target_domain = target_domain
        self.output_dirs = output_dirs
        self.logger = Logger()
        self.discovered_subdomains: Set[str] = set()
        
        # Tool availability check
        self.available_tools = self._check_tool_availability()
    
    def _check_tool_availability(self) -> Dict[str, bool]:
        """Check which tools are available on the system."""
        tools = ['assetfinder', 'subfinder', 'httpx', 'anew', 'curl']
        availability = {}
        
        for tool in tools:
            availability[tool] = check_tool_availability(tool)
            if not availability[tool]:
                self.logger.warning(f"Tool '{tool}' not found in PATH")
        
        return availability
    
    async def discover_all(self, progress_callback: Optional[Callable] = None) -> List[str]:
        """Run all subdomain discovery methods."""
        self.logger.info(f"Starting subdomain discovery for {self.target_domain}")
        start_time = time.time()
        
        # List of discovery methods
        discovery_methods = [
            ('assetfinder', self._run_assetfinder),
            ('subfinder', self._run_subfinder),
            ('crt_sh', self._run_crt_sh),
            ('wayback', self._run_wayback),
        ]
        
        # Run discovery methods concurrently
        tasks = []
        for method_name, method in discovery_methods:
            if self.config.is_tool_enabled(method_name):
                tasks.append(self._run_with_progress(method_name, method, progress_callback))
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all subdomains
        all_subdomains = []
        for i, result in enumerate(results):
            method_name = discovery_methods[i][0]
            if isinstance(result, Exception):
                self.logger.error(f"Error in {method_name}: {result}")
            else:
                all_subdomains.extend(result)
        
        # Deduplicate and clean
        unique_subdomains = deduplicate_subdomains(all_subdomains)
        self.discovered_subdomains.update(unique_subdomains)
        
        # Save results
        self._save_discovery_results(unique_subdomains)
        
        duration = time.time() - start_time
        self.logger.success(f"Discovery completed in {duration:.2f}s. Found {len(unique_subdomains)} unique subdomains")
        
        return unique_subdomains
    
    async def _run_with_progress(self, method_name: str, method: Callable, progress_callback: Optional[Callable]) -> List[str]:
        """Run a discovery method with progress tracking."""
        if progress_callback:
            progress_callback(f"Running {method_name}...")
        
        try:
            result = await method()
            if progress_callback:
                progress_callback(f"Completed {method_name}: {len(result)} subdomains")
            return result
        except Exception as e:
            self.logger.error(f"Error in {method_name}: {e}")
            return []
    
    async def _run_assetfinder(self) -> List[str]:
        """Run assetfinder for subdomain discovery."""
        if not self.available_tools.get('assetfinder', False):
            self.logger.warning("Assetfinder not available, skipping...")
            return []
        
        self.logger.info("Running assetfinder...")
        output_file = Path(self.output_dirs['raw']) / 'assetfinder.txt'
        
        try:
            tool_config = self.config.get_tool_config('assetfinder')
            command = ['assetfinder', '-subs-only', self.target_domain]
            command.extend(tool_config.additional_args)
            
            result = run_command(command, timeout=tool_config.timeout)
            
            if result.returncode == 0:
                subdomains = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                write_file_lines(str(output_file), subdomains)
                self.logger.success(f"Assetfinder found {len(subdomains)} subdomains")
                return subdomains
            else:
                self.logger.error(f"Assetfinder failed: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error running assetfinder: {e}")
            return []
    
    async def _run_subfinder(self) -> List[str]:
        """Run subfinder for subdomain discovery."""
        if not self.available_tools.get('subfinder', False):
            self.logger.warning("Subfinder not available, skipping...")
            return []
        
        self.logger.info("Running subfinder...")
        output_file = Path(self.output_dirs['raw']) / 'subfinder.txt'
        
        try:
            tool_config = self.config.get_tool_config('subfinder')
            command = ['subfinder', '-d', self.target_domain, '-o', str(output_file)]
            command.extend(tool_config.additional_args)
            
            result = run_command(command, timeout=tool_config.timeout)
            
            if result.returncode == 0:
                subdomains = read_file_lines(str(output_file))
                self.logger.success(f"Subfinder found {len(subdomains)} subdomains")
                return subdomains
            else:
                self.logger.error(f"Subfinder failed: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error running subfinder: {e}")
            return []
    
    async def _run_crt_sh(self) -> List[str]:
        """Fetch subdomains from crt.sh (Certificate Transparency)."""
        if not self.available_tools.get('curl', False):
            self.logger.warning("curl not available, skipping crt.sh...")
            return []
        
        self.logger.info("Fetching subdomains from crt.sh...")
        output_file = Path(self.output_dirs['raw']) / 'crt.txt'
        
        try:
            tool_config = self.config.get_tool_config('crt_sh')
            url = f"https://crt.sh/?q={self.target_domain}&output=json"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=tool_config.timeout)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        subdomains = set()
                        
                        for entry in data:
                            name_value = entry.get('name_value', '')
                            # Handle multiple domains in name_value
                            for domain in name_value.split('\n'):
                                domain = domain.strip()
                                if domain and self.target_domain in domain:
                                    # Remove wildcards
                                    domain = domain.replace('*.', '')
                                    if domain:
                                        subdomains.add(domain)
                        
                        subdomain_list = list(subdomains)
                        write_file_lines(str(output_file), subdomain_list)
                        self.logger.success(f"crt.sh found {len(subdomain_list)} subdomains")
                        return subdomain_list
                    else:
                        self.logger.error(f"crt.sh request failed with status {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error fetching from crt.sh: {e}")
            return []
    
    async def _run_wayback(self) -> List[str]:
        """Fetch subdomains from Wayback Machine."""
        self.logger.info("Fetching subdomains from Wayback Machine...")
        output_file = Path(self.output_dirs['raw']) / 'wayback.txt'
        
        try:
            tool_config = self.config.get_tool_config('wayback')
            url = f"http://web.archive.org/cdx/search/cdx?url=*.{self.target_domain}/*&output=text&fl=original&collapse=urlkey"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=tool_config.timeout)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        subdomains = set()
                        
                        for line in content.split('\n'):
                            if line.strip():
                                # Extract domain from URL
                                match = re.search(r'https?://([^/]+)', line)
                                if match:
                                    domain = match.group(1)
                                    # Clean domain
                                    domain = domain.replace('www.', '').replace(':80', '').replace(':443', '')
                                    if self.target_domain in domain:
                                        subdomains.add(domain)
                        
                        subdomain_list = list(subdomains)
                        write_file_lines(str(output_file), subdomain_list)
                        self.logger.success(f"Wayback Machine found {len(subdomain_list)} subdomains")
                        return subdomain_list
                    else:
                        self.logger.error(f"Wayback Machine request failed with status {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error fetching from Wayback Machine: {e}")
            return []
    
    def add_manual_subdomains(self, manual_file: str) -> List[str]:
        """Add manually discovered subdomains."""
        manual_subdomains = read_file_lines(manual_file)
        if manual_subdomains:
            self.logger.info(f"Added {len(manual_subdomains)} manual subdomains")
            self.discovered_subdomains.update(manual_subdomains)
        return manual_subdomains
    
    def _save_discovery_results(self, subdomains: List[str]) -> None:
        """Save discovery results to files."""
        # Save all subdomains
        all_subs_file = Path(self.output_dirs['processed']) / 'all_subdomains.txt'
        write_file_lines(str(all_subs_file), subdomains)
        
        # Save unique subdomains
        unique_subs_file = Path(self.output_dirs['processed']) / 'unique_subdomains.txt'
        write_file_lines(str(unique_subs_file), subdomains)
        
        self.logger.info(f"Results saved to {self.output_dirs['processed']}")
    
    def get_discovered_subdomains(self) -> List[str]:
        """Get all discovered subdomains."""
        return sorted(list(self.discovered_subdomains))
