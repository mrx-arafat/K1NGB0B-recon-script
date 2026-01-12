"""
Port scanning module using RustScan and Nmap.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Set, List, Dict, Optional
from dataclasses import dataclass, field

from ..utils.runner import AsyncRunner, get_runner, run_sync
from ..utils.tools import check_tool
from ..utils.colors import print_info, print_success, print_warning, print_error
from ..config import get_config


@dataclass
class PortResult:
    """Result for a single host's port scan."""
    host: str
    ports: List[int] = field(default_factory=list)
    services: Dict[int, str] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


@dataclass
class ScanResult:
    """Result for the entire port scan."""
    hosts: Dict[str, PortResult] = field(default_factory=dict)
    total_open_ports: int = 0
    duration: float = 0.0


class PortScanner:
    """Port scanning using RustScan or Nmap."""

    # Common ports for web applications
    WEB_PORTS = [80, 443, 8080, 8443, 8000, 8888, 3000, 9000, 9443]

    # Extended common ports
    COMMON_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
        993, 995, 1723, 3306, 3389, 5432, 5900, 8080, 8443
    ]

    def __init__(
        self,
        targets: List[str],
        ports: Optional[List[int]] = None,
        timeout: int = 300,
        batch_size: int = 100
    ):
        self.targets = targets
        self.ports = ports or self.COMMON_PORTS
        self.timeout = timeout
        self.batch_size = batch_size
        self.config = get_config()

    async def scan(self) -> ScanResult:
        """Run port scan on all targets."""
        result = ScanResult()

        if not self.targets:
            print_warning("No targets to scan")
            return result

        print_info(f"Starting port scan on {len(self.targets)} targets...")

        # Check available tools
        has_rustscan = check_tool('rustscan').available
        has_nmap = check_tool('nmap').available

        if has_rustscan:
            print_info("Using RustScan for fast port discovery")
            result = await self._scan_with_rustscan()
        elif has_nmap:
            print_info("Using Nmap for port scanning")
            result = await self._scan_with_nmap()
        else:
            print_error("No port scanner available. Install rustscan or nmap.")
            return result

        print_success(f"Port scan complete: {result.total_open_ports} open ports found")
        return result

    async def _scan_with_rustscan(self) -> ScanResult:
        """Scan using RustScan."""
        result = ScanResult()
        runner = get_runner(timeout=self.timeout)

        # Prepare targets file
        targets_str = ','.join(self.targets[:self.batch_size])  # Limit batch

        # Build RustScan command
        ports_str = ','.join(str(p) for p in self.ports)
        cmd_args = [
            '-a', targets_str,
            '-p', ports_str,
            '--ulimit', '5000',
            '-b', '500',  # Batch size
            '-t', '2000',  # Timeout per port
            '-g',  # Greppable output
        ]

        import time
        start = time.time()

        run_result = await runner.run_tool('rustscan', cmd_args, timeout=self.timeout)
        result.duration = time.time() - start

        if run_result.success:
            # Parse RustScan output
            result = self._parse_rustscan_output(run_result.stdout, result)
        else:
            print_warning(f"RustScan failed: {run_result.stderr[:100]}")

        return result

    async def _scan_with_nmap(self) -> ScanResult:
        """Scan using Nmap."""
        result = ScanResult()
        runner = get_runner(timeout=self.timeout)

        # Limit targets for safety
        targets = self.targets[:50]
        targets_str = ' '.join(targets)

        # Build Nmap command
        ports_str = ','.join(str(p) for p in self.ports)
        cmd_args = [
            '-sS',  # SYN scan
            '-Pn',  # Skip host discovery
            '-p', ports_str,
            '-T4',  # Aggressive timing
            '--open',  # Only show open ports
            '-oG', '-',  # Greppable output to stdout
        ] + targets

        import time
        start = time.time()

        run_result = await runner.run_tool('nmap', cmd_args, timeout=self.timeout)
        result.duration = time.time() - start

        if run_result.success:
            result = self._parse_nmap_output(run_result.stdout, result)
        else:
            print_warning(f"Nmap failed: {run_result.stderr[:100]}")

        return result

    def _parse_rustscan_output(self, output: str, result: ScanResult) -> ScanResult:
        """Parse RustScan greppable output."""
        # RustScan output format: IP:PORT or HOST -> [PORTS]
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            # Format: host -> [port1, port2, ...]
            if '->' in line:
                parts = line.split('->')
                if len(parts) == 2:
                    host = parts[0].strip()
                    ports_str = parts[1].strip().strip('[]')
                    ports = []
                    for p in ports_str.split(','):
                        try:
                            ports.append(int(p.strip()))
                        except ValueError:
                            continue

                    if ports:
                        result.hosts[host] = PortResult(host=host, ports=ports)
                        result.total_open_ports += len(ports)

            # Format: host:port
            elif ':' in line and line[0].isdigit():
                parts = line.rsplit(':', 1)
                if len(parts) == 2:
                    host = parts[0]
                    try:
                        port = int(parts[1])
                        if host not in result.hosts:
                            result.hosts[host] = PortResult(host=host)
                        result.hosts[host].ports.append(port)
                        result.total_open_ports += 1
                    except ValueError:
                        continue

        return result

    def _parse_nmap_output(self, output: str, result: ScanResult) -> ScanResult:
        """Parse Nmap greppable output."""
        # Nmap greppable format:
        # Host: IP (hostname) Ports: port/status/protocol/owner/service...

        for line in output.splitlines():
            if not line.startswith('Host:'):
                continue

            # Extract host
            host_match = re.search(r'Host: (\S+)', line)
            if not host_match:
                continue

            host = host_match.group(1)

            # Extract ports
            ports_match = re.search(r'Ports: (.+?)(?:\t|$)', line)
            if not ports_match:
                continue

            ports_str = ports_match.group(1)
            ports = []
            services = {}

            for port_info in ports_str.split(','):
                parts = port_info.strip().split('/')
                if len(parts) >= 2 and parts[1] == 'open':
                    try:
                        port = int(parts[0])
                        ports.append(port)
                        if len(parts) >= 5 and parts[4]:
                            services[port] = parts[4]
                    except ValueError:
                        continue

            if ports:
                result.hosts[host] = PortResult(host=host, ports=ports, services=services)
                result.total_open_ports += len(ports)

        return result

    def to_json(self, result: ScanResult) -> str:
        """Convert scan result to JSON."""
        data = {
            'total_hosts': len(result.hosts),
            'total_open_ports': result.total_open_ports,
            'duration': result.duration,
            'hosts': {}
        }

        for host, port_result in result.hosts.items():
            data['hosts'][host] = {
                'ports': port_result.ports,
                'services': port_result.services
            }

        return json.dumps(data, indent=2)


async def scan_ports(
    targets: List[str],
    ports: Optional[List[int]] = None,
    timeout: int = 300
) -> ScanResult:
    """Convenience function to run port scan."""
    scanner = PortScanner(targets, ports, timeout)
    return await scanner.scan()
