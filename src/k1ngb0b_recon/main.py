"""
Main application module for K1NGB0B Recon Script.
"""

import asyncio
import time
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
from tqdm import tqdm

from .config import Config
from .subdomain_discovery import SubdomainDiscovery
from .utils import (
    Logger, validate_domain, create_directory_structure,
    print_banner, format_duration, save_json_report
)


class ReconApp:
    """Main reconnaissance application."""
    
    def __init__(self, target_domain: str, config: Config, output_dir: str = "."):
        self.target_domain = target_domain
        self.config = config
        self.output_dir = output_dir
        self.logger = Logger()
        self.start_time = time.time()
        
        # Create directory structure
        self.directories = create_directory_structure(output_dir, target_domain)
        
        # Initialize subdomain discovery
        self.subdomain_discovery = SubdomainDiscovery(
            config, target_domain, self.directories
        )
    
    async def run_reconnaissance(self, run_live_check: bool = True) -> Dict[str, Any]:
        """Run the complete reconnaissance process."""
        self.logger.info(f"Starting reconnaissance for {self.target_domain}")
        
        results = {
            'target_domain': self.target_domain,
            'start_time': self.start_time,
            'subdomains': {
                'discovered': [],
                'live': [],
                'total_discovered': 0,
                'total_live': 0
            },
            'tools_used': [],
            'duration': 0,
            'status': 'running'
        }
        
        try:
            # Progress tracking
            progress_bar = None
            if not self.config.verbose:
                progress_bar = tqdm(total=100, desc="Discovery Progress", unit="%")
            
            def update_progress(message: str):
                if self.config.verbose:
                    self.logger.info(message)
                elif progress_bar:
                    progress_bar.set_description(message)
                    progress_bar.update(25)  # Rough progress estimation
            
            # Run subdomain discovery
            discovered_subdomains = await self.subdomain_discovery.discover_all(update_progress)
            results['subdomains']['discovered'] = discovered_subdomains
            results['subdomains']['total_discovered'] = len(discovered_subdomains)
            
            if progress_bar:
                progress_bar.close()
            
            # Run live subdomain check if requested
            if run_live_check and discovered_subdomains:
                live_subdomains = await self._run_live_check(discovered_subdomains)
                results['subdomains']['live'] = live_subdomains
                results['subdomains']['total_live'] = len(live_subdomains)
            
            # Generate reports
            await self._generate_reports(results)
            
            # Calculate duration
            results['duration'] = time.time() - self.start_time
            results['status'] = 'completed'
            
            self.logger.success(f"Reconnaissance completed in {format_duration(results['duration'])}")
            self._print_summary(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Reconnaissance failed: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
            results['duration'] = time.time() - self.start_time
            return results
    
    async def _run_live_check(self, subdomains: List[str]) -> List[str]:
        """Check which subdomains are live using httpx."""
        self.logger.info("Checking live subdomains...")
        
        if not self.subdomain_discovery.available_tools.get('httpx', False):
            self.logger.warning("httpx not available, skipping live check")
            return []
        
        try:
            # Create input file for httpx
            input_file = Path(self.directories['processed']) / 'all_subdomains.txt'
            output_file = Path(self.directories['processed']) / 'live_subdomains.txt'
            
            # Run httpx
            tool_config = self.config.get_tool_config('httpx')
            command = [
                'httpx',
                '-list', str(input_file),
                '-o', str(output_file),
                '-silent',
                '-timeout', str(tool_config.timeout),
                '-retries', str(tool_config.retries),
                '-threads', str(self.config.http.threads)
            ]
            
            from .utils import run_command
            result = run_command(command, timeout=tool_config.timeout * 2)
            
            if result.returncode == 0:
                live_subdomains = []
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        live_subdomains = [line.strip() for line in f if line.strip()]
                
                self.logger.success(f"Found {len(live_subdomains)} live subdomains")
                return live_subdomains
            else:
                self.logger.error(f"httpx failed: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error during live check: {e}")
            return []
    
    async def _generate_reports(self, results: Dict[str, Any]) -> None:
        """Generate various reports."""
        self.logger.info("Generating reports...")
        
        # JSON report
        json_report_file = Path(self.directories['reports']) / 'summary.json'
        save_json_report(results, str(json_report_file))
        
        # Text summary
        summary_file = Path(self.directories['reports']) / 'summary.txt'
        self._generate_text_summary(results, str(summary_file))
        
        self.logger.success("Reports generated successfully")
    
    def _generate_text_summary(self, results: Dict[str, Any], output_file: str) -> None:
        """Generate a text summary report."""
        with open(output_file, 'w') as f:
            f.write(f"K1NGB0B Recon Report\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"Target Domain: {results['target_domain']}\n")
            f.write(f"Scan Duration: {format_duration(results['duration'])}\n")
            f.write(f"Status: {results['status']}\n\n")
            
            f.write(f"Subdomain Discovery Results:\n")
            f.write(f"- Total Discovered: {results['subdomains']['total_discovered']}\n")
            f.write(f"- Total Live: {results['subdomains']['total_live']}\n\n")
            
            if results['subdomains']['discovered']:
                f.write(f"Discovered Subdomains:\n")
                for subdomain in sorted(results['subdomains']['discovered']):
                    f.write(f"  - {subdomain}\n")
                f.write("\n")
            
            if results['subdomains']['live']:
                f.write(f"Live Subdomains:\n")
                for subdomain in sorted(results['subdomains']['live']):
                    f.write(f"  - {subdomain}\n")
    
    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print a summary of the reconnaissance results."""
        print("\n" + "=" * 60)
        print("RECONNAISSANCE SUMMARY")
        print("=" * 60)
        print(f"Target Domain: {results['target_domain']}")
        print(f"Duration: {format_duration(results['duration'])}")
        print(f"Total Subdomains Discovered: {results['subdomains']['total_discovered']}")
        print(f"Live Subdomains: {results['subdomains']['total_live']}")
        print(f"Results Directory: {self.directories['base']}")
        print("=" * 60)


@click.command()
@click.argument('target_domain')
@click.option('--output', '-o', default='.', help='Output directory for results')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--no-live', is_flag=True, help='Skip live subdomain verification')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--debug', is_flag=True, help='Enable debug output')
def main(target_domain: str, output: str, config: Optional[str], no_live: bool, verbose: bool, debug: bool):
    """K1NGB0B Recon Script - Comprehensive domain reconnaissance tool."""
    
    # Print banner
    print_banner()
    
    # Validate domain
    if not validate_domain(target_domain):
        click.echo(f"Error: Invalid domain '{target_domain}'", err=True)
        sys.exit(1)
    
    # Load configuration
    try:
        app_config = Config(config) if config else Config()
        app_config.verbose = verbose
        app_config.debug = debug
        
        if debug:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)
    
    # Create and run the reconnaissance app
    try:
        app = ReconApp(target_domain, app_config, output)
        results = asyncio.run(app.run_reconnaissance(run_live_check=not no_live))
        
        if results['status'] == 'failed':
            sys.exit(1)
            
    except KeyboardInterrupt:
        click.echo("\nReconnaissance interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
