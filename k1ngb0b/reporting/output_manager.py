"""
Output management and report generation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..config import get_config
from ..utils.colors import print_info, print_success


@dataclass
class OutputPaths:
    """Paths to output directories."""
    base: Path
    raw_discovery: Path
    processed_data: Path
    live_analysis: Path
    technologies: Path
    vulnerabilities: Path
    port_scanning: Path
    screenshots: Path
    final_reports: Path
    advanced_discovery: Path
    manual_verification: Path


class OutputManager:
    """Manages output directory structure and report generation."""

    def __init__(self, domain: str, base_dir: Optional[Path] = None):
        self.domain = domain
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.config = get_config()

        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path.cwd() / f"{domain}_results_{self.timestamp}"

        self.paths = self._create_structure()

    def _create_structure(self) -> OutputPaths:
        """Create the output directory structure."""
        dirs = {
            'raw_discovery': '01_raw_discovery',
            'processed_data': '02_processed_data',
            'live_analysis': '03_live_analysis',
            'technologies': '04_technologies',
            'vulnerabilities': '05_vulnerabilities',
            'port_scanning': '06_port_scanning',
            'screenshots': '07_screenshots',
            'final_reports': '08_final_reports',
            'advanced_discovery': '09_advanced_discovery',
            'manual_verification': '10_manual_verification',
        }

        paths = {'base': self.base_dir}

        for key, dirname in dirs.items():
            path = self.base_dir / dirname
            path.mkdir(parents=True, exist_ok=True)
            paths[key] = path

        return OutputPaths(**paths)

    def save_subdomains(self, subdomains: List[str], filename: str = 'all_subdomains.txt') -> Path:
        """Save discovered subdomains to file."""
        output_path = self.paths.processed_data / filename
        sorted_subs = sorted(set(subdomains))

        with open(output_path, 'w') as f:
            f.write('\n'.join(sorted_subs))

        print_info(f"Saved {len(sorted_subs)} subdomains to {output_path}")
        return output_path

    def save_live_hosts(self, hosts: List[str], filename: str = 'live_hosts.txt') -> Path:
        """Save live hosts to file."""
        output_path = self.paths.live_analysis / filename

        with open(output_path, 'w') as f:
            f.write('\n'.join(hosts))

        print_info(f"Saved {len(hosts)} live hosts to {output_path}")
        return output_path

    def save_json(self, data: Any, category: str, filename: str) -> Path:
        """Save JSON data to appropriate category directory."""
        category_map = {
            'discovery': self.paths.raw_discovery,
            'processed': self.paths.processed_data,
            'live': self.paths.live_analysis,
            'tech': self.paths.technologies,
            'vuln': self.paths.vulnerabilities,
            'ports': self.paths.port_scanning,
            'report': self.paths.final_reports,
            'advanced': self.paths.advanced_discovery,
        }

        output_dir = category_map.get(category, self.paths.final_reports)
        output_path = output_dir / filename

        with open(output_path, 'w') as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, indent=2)

        return output_path

    def save_raw_output(self, tool: str, output: str) -> Path:
        """Save raw tool output."""
        output_path = self.paths.raw_discovery / f"{tool}_raw.txt"

        with open(output_path, 'w') as f:
            f.write(output)

        return output_path

    def generate_summary_report(
        self,
        subdomains: List[str],
        live_hosts: List[str],
        vulnerabilities: Optional[List[Dict]] = None,
        ports: Optional[Dict] = None
    ) -> Path:
        """Generate a summary report."""
        report = {
            'target': self.domain,
            'timestamp': self.timestamp,
            'summary': {
                'total_subdomains': len(subdomains),
                'live_hosts': len(live_hosts),
                'vulnerabilities': len(vulnerabilities) if vulnerabilities else 0,
                'hosts_with_open_ports': len(ports) if ports else 0
            },
            'subdomains': sorted(subdomains),
            'live_hosts': live_hosts,
        }

        if vulnerabilities:
            report['vulnerabilities'] = vulnerabilities

        if ports:
            report['ports'] = ports

        output_path = self.paths.final_reports / 'summary_report.json'

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print_success(f"Summary report saved to {output_path}")
        return output_path

    def generate_markdown_report(
        self,
        subdomains: List[str],
        live_hosts: List[str],
        vulnerabilities: Optional[List[Dict]] = None
    ) -> Path:
        """Generate a markdown report."""
        lines = [
            f"# Reconnaissance Report: {self.domain}",
            f"",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            "## Summary",
            f"",
            f"| Metric | Count |",
            f"|--------|-------|",
            f"| Subdomains Discovered | {len(subdomains)} |",
            f"| Live Hosts | {len(live_hosts)} |",
            f"| Vulnerabilities | {len(vulnerabilities) if vulnerabilities else 0} |",
            f"",
        ]

        if live_hosts:
            lines.extend([
                "## Live Hosts",
                "",
            ])
            for host in live_hosts[:50]:  # Limit to 50
                lines.append(f"- {host}")
            if len(live_hosts) > 50:
                lines.append(f"- ... and {len(live_hosts) - 50} more")
            lines.append("")

        if vulnerabilities:
            lines.extend([
                "## Vulnerabilities",
                "",
            ])
            for vuln in vulnerabilities[:20]:  # Limit to 20
                severity = vuln.get('severity', 'unknown')
                name = vuln.get('name', 'Unknown')
                host = vuln.get('host', '')
                lines.append(f"- **[{severity.upper()}]** {name} at {host}")
            if len(vulnerabilities) > 20:
                lines.append(f"- ... and {len(vulnerabilities) - 20} more")
            lines.append("")

        output_path = self.paths.final_reports / 'report.md'

        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

        print_success(f"Markdown report saved to {output_path}")
        return output_path

    def get_paths(self) -> Dict[str, Path]:
        """Get all output paths as a dictionary."""
        return {
            'base': self.paths.base,
            'raw_discovery': self.paths.raw_discovery,
            'processed_data': self.paths.processed_data,
            'live_analysis': self.paths.live_analysis,
            'technologies': self.paths.technologies,
            'vulnerabilities': self.paths.vulnerabilities,
            'port_scanning': self.paths.port_scanning,
            'screenshots': self.paths.screenshots,
            'final_reports': self.paths.final_reports,
            'advanced_discovery': self.paths.advanced_discovery,
            'manual_verification': self.paths.manual_verification,
        }


def create_output_manager(domain: str, base_dir: Optional[Path] = None) -> OutputManager:
    """Create an output manager for a domain."""
    return OutputManager(domain, base_dir)
