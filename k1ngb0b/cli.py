#!/usr/bin/env python3
"""
K1NGB0B Recon Suite - Unified CLI
A professional reconnaissance toolkit for bug bounty and security assessments.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional, List

from .config import get_config, Config
from .utils.colors import Colors, print_header, print_info, print_success, print_error, print_warning
from .utils.tools import print_tool_status, check_all_tools
from .discovery.passive import PassiveDiscovery
from .discovery.active import ActiveDiscovery
from .discovery.permutations import SubdomainPermutator
from .probing.httpx_wrapper import HttpProber
from .scanner.ports import PortScanner
from .scanner.vulnerabilities import VulnerabilityScanner
from .scanner.content import ContentScanner
from .reporting.output_manager import OutputManager


VERSION = "3.0.0"


def print_banner() -> None:
    """Print the K1NGB0B banner."""
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║  K1NGB0B Recon Suite v{VERSION}                                  ║
║  Professional Reconnaissance Toolkit                          ║
║  Author: mrx-arafat (K1NGB0B)                                ║
╚══════════════════════════════════════════════════════════════╝{Colors.NC}
""")


async def cmd_discover(args) -> None:
    """Run subdomain discovery."""
    domain = args.domain
    output = OutputManager(domain, Path(args.output) if args.output else None)

    print_header(f"Subdomain Discovery: {domain}")

    all_subdomains = set()

    # Passive discovery
    if not args.active_only:
        print_info("Running passive discovery...")
        passive = PassiveDiscovery(domain, timeout=args.timeout)
        passive_results = await passive.run_all()
        all_subdomains.update(passive_results)
        print_success(f"Passive discovery: {len(passive_results)} subdomains")

    # Active discovery (tools)
    if not args.passive_only:
        print_info("Running active discovery (tools)...")
        active = ActiveDiscovery(domain, timeout=args.timeout)
        active_results = await active.run_all()
        all_subdomains.update(active_results)
        print_success(f"Active discovery: {len(active_results)} subdomains")

    # Permutation generation
    if args.permutations and all_subdomains:
        print_info("Generating permutations...")
        permutator = SubdomainPermutator(domain)
        perms = permutator.generate_permutations(all_subdomains)
        # Note: We don't add perms directly - they need validation
        output.save_json(list(perms), 'advanced', 'permutations.txt')

    # Save results
    output.save_subdomains(list(all_subdomains))

    print_success(f"Total unique subdomains: {len(all_subdomains)}")
    print_info(f"Results saved to: {output.paths.base}")


async def cmd_probe(args) -> None:
    """Probe hosts for live HTTP services."""
    print_header("HTTP Probing")

    # Load targets from file or use domain
    targets = []
    if args.list:
        with open(args.list, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
    elif args.domain:
        targets = [args.domain]
    else:
        print_error("Provide either --domain or --list")
        return

    prober = HttpProber(targets, timeout=args.timeout, threads=args.threads)
    results = await prober.probe()

    # Print results
    print_success(f"Live hosts: {results.total_live}")
    for host in results.live_hosts[:20]:
        status_color = Colors.GREEN if host.status_code == 200 else Colors.YELLOW
        print(f"  {status_color}[{host.status_code}]{Colors.NC} {host.url} - {host.title[:50]}")

    if len(results.live_hosts) > 20:
        print_info(f"  ... and {len(results.live_hosts) - 20} more")

    # Save if output specified
    if args.output:
        with open(args.output, 'w') as f:
            f.write('\n'.join(results.get_urls()))
        print_info(f"Saved to {args.output}")


async def cmd_ports(args) -> None:
    """Run port scanning."""
    print_header("Port Scanning")

    # Load targets
    targets = []
    if args.list:
        with open(args.list, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
    elif args.target:
        targets = [args.target]
    else:
        print_error("Provide either --target or --list")
        return

    # Parse ports
    ports = None
    if args.ports:
        ports = [int(p.strip()) for p in args.ports.split(',')]

    scanner = PortScanner(targets, ports=ports, timeout=args.timeout)
    results = await scanner.scan()

    # Print results
    for host, port_result in results.hosts.items():
        print_success(f"{host}: {port_result.ports}")

    # Save if output specified
    if args.output:
        with open(args.output, 'w') as f:
            f.write(scanner.to_json(results))
        print_info(f"Saved to {args.output}")


async def cmd_vuln(args) -> None:
    """Run vulnerability scanning."""
    print_header("Vulnerability Scanning")

    # Load targets
    targets = []
    if args.list:
        with open(args.list, 'r') as f:
            targets = [line.strip() for line in f if line.strip()]
    elif args.target:
        targets = [args.target]
    else:
        print_error("Provide either --target or --list")
        return

    # Parse severity
    severity = args.severity.split(',') if args.severity else None

    scanner = VulnerabilityScanner(
        targets,
        severity=severity,
        timeout=args.timeout
    )
    results = await scanner.scan()

    # Print findings
    for finding in results.findings[:20]:
        sev_color = {
            'critical': Colors.RED,
            'high': Colors.BRIGHT_RED,
            'medium': Colors.YELLOW,
            'low': Colors.BLUE,
            'info': Colors.CYAN
        }.get(finding.severity, Colors.NC)

        print(f"  {sev_color}[{finding.severity.upper()}]{Colors.NC} {finding.name}")
        print(f"    {Colors.DIM}{finding.matched_at}{Colors.NC}")

    if len(results.findings) > 20:
        print_info(f"  ... and {len(results.findings) - 20} more findings")

    # Save if output specified
    if args.output:
        with open(args.output, 'w') as f:
            f.write(scanner.to_json(results))
        print_info(f"Saved to {args.output}")


async def cmd_content(args) -> None:
    """Run content discovery."""
    print_header("Content Discovery")

    if not args.target:
        print_error("Provide --target URL")
        return

    scanner = ContentScanner(
        args.target,
        wordlist=args.wordlist,
        extensions=args.extensions.split(',') if args.extensions else None,
        timeout=args.timeout
    )
    results = await scanner.scan()

    # Print interesting results
    interesting = results.get_interesting()
    for result in interesting[:30]:
        status_color = {
            200: Colors.GREEN,
            301: Colors.YELLOW,
            302: Colors.YELLOW,
            403: Colors.RED,
            401: Colors.RED
        }.get(result.status, Colors.NC)

        print(f"  {status_color}[{result.status}]{Colors.NC} {result.url} [{result.length}]")

    if len(interesting) > 30:
        print_info(f"  ... and {len(interesting) - 30} more")

    # Save if output specified
    if args.output:
        with open(args.output, 'w') as f:
            f.write(scanner.to_json(results))
        print_info(f"Saved to {args.output}")


async def cmd_full(args) -> None:
    """Run full reconnaissance pipeline."""
    domain = args.domain
    output = OutputManager(domain, Path(args.output) if args.output else None)

    print_header(f"Full Reconnaissance: {domain}")

    # Stage 1: Discovery
    print_header("Stage 1: Subdomain Discovery")

    all_subdomains = set()

    # Passive
    print_info("Running passive discovery...")
    passive = PassiveDiscovery(domain, timeout=args.timeout)
    passive_results = await passive.run_all()
    all_subdomains.update(passive_results)

    # Active
    print_info("Running active discovery...")
    active = ActiveDiscovery(domain, timeout=args.timeout)
    active_results = await active.run_all()
    all_subdomains.update(active_results)

    output.save_subdomains(list(all_subdomains))
    print_success(f"Total subdomains: {len(all_subdomains)}")

    if not all_subdomains:
        print_warning("No subdomains found. Stopping.")
        return

    # Stage 2: Probing
    print_header("Stage 2: HTTP Probing")

    prober = HttpProber(list(all_subdomains), timeout=15, threads=50)
    probe_results = await prober.probe()

    live_urls = probe_results.get_urls()
    output.save_live_hosts(live_urls)
    print_success(f"Live hosts: {len(live_urls)}")

    if not live_urls:
        print_warning("No live hosts found. Stopping.")
        return

    # Stage 3: Vulnerability Scanning
    if not args.skip_vuln:
        print_header("Stage 3: Vulnerability Scanning")

        vuln_scanner = VulnerabilityScanner(
            live_urls[:100],  # Limit to 100 targets
            severity=['critical', 'high', 'medium'],
            timeout=600
        )
        vuln_results = await vuln_scanner.scan()

        if vuln_results.findings:
            output.save_json(
                vuln_scanner.to_json(vuln_results),
                'vuln',
                'nuclei_results.json'
            )

    # Stage 4: Port Scanning (optional)
    if args.ports:
        print_header("Stage 4: Port Scanning")

        # Extract hosts from URLs
        from urllib.parse import urlparse
        hosts = list(set(urlparse(url).netloc.split(':')[0] for url in live_urls))

        port_scanner = PortScanner(hosts[:50], timeout=300)  # Limit to 50 hosts
        port_results = await port_scanner.scan()

        if port_results.hosts:
            output.save_json(
                port_scanner.to_json(port_results),
                'ports',
                'port_scan.json'
            )

    # Generate reports
    print_header("Generating Reports")

    vuln_findings = []
    if not args.skip_vuln and vuln_results.findings:
        vuln_findings = [
            {'severity': f.severity, 'name': f.name, 'host': f.host}
            for f in vuln_results.findings
        ]

    output.generate_summary_report(
        list(all_subdomains),
        live_urls,
        vulnerabilities=vuln_findings
    )

    output.generate_markdown_report(
        list(all_subdomains),
        live_urls,
        vulnerabilities=vuln_findings
    )

    print_success(f"Reconnaissance complete! Results saved to: {output.paths.base}")


def cmd_check(args) -> None:
    """Check tool installation status."""
    print_banner()
    print_tool_status()

    all_ok, missing = check_all_tools()
    if not all_ok:
        print_warning("\nSome tools are missing. Run: python3 install.py")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='k1ngb0b',
        description='K1NGB0B Recon Suite - Professional Reconnaissance Toolkit'
    )
    parser.add_argument('--version', action='version', version=f'k1ngb0b {VERSION}')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # discover command
    discover_parser = subparsers.add_parser('discover', help='Subdomain discovery')
    discover_parser.add_argument('domain', help='Target domain')
    discover_parser.add_argument('-o', '--output', help='Output directory')
    discover_parser.add_argument('-t', '--timeout', type=int, default=60, help='Timeout per source')
    discover_parser.add_argument('--passive-only', action='store_true', help='Only passive discovery')
    discover_parser.add_argument('--active-only', action='store_true', help='Only active discovery')
    discover_parser.add_argument('--permutations', action='store_true', help='Generate permutations')

    # probe command
    probe_parser = subparsers.add_parser('probe', help='Probe hosts for HTTP services')
    probe_parser.add_argument('-d', '--domain', help='Single domain to probe')
    probe_parser.add_argument('-l', '--list', help='File with list of targets')
    probe_parser.add_argument('-o', '--output', help='Output file')
    probe_parser.add_argument('-t', '--timeout', type=int, default=10, help='Request timeout')
    probe_parser.add_argument('--threads', type=int, default=50, help='Number of threads')

    # ports command
    ports_parser = subparsers.add_parser('ports', help='Port scanning')
    ports_parser.add_argument('-t', '--target', help='Single target')
    ports_parser.add_argument('-l', '--list', help='File with list of targets')
    ports_parser.add_argument('-p', '--ports', help='Ports to scan (comma-separated)')
    ports_parser.add_argument('-o', '--output', help='Output file')
    ports_parser.add_argument('--timeout', type=int, default=300, help='Total timeout')

    # vuln command
    vuln_parser = subparsers.add_parser('vuln', help='Vulnerability scanning')
    vuln_parser.add_argument('-t', '--target', help='Single target URL')
    vuln_parser.add_argument('-l', '--list', help='File with list of URLs')
    vuln_parser.add_argument('-s', '--severity', default='critical,high,medium', help='Severity filter')
    vuln_parser.add_argument('-o', '--output', help='Output file')
    vuln_parser.add_argument('--timeout', type=int, default=600, help='Total timeout')

    # content command
    content_parser = subparsers.add_parser('content', help='Content discovery')
    content_parser.add_argument('-t', '--target', required=True, help='Target URL')
    content_parser.add_argument('-w', '--wordlist', help='Wordlist file')
    content_parser.add_argument('-e', '--extensions', help='Extensions (comma-separated)')
    content_parser.add_argument('-o', '--output', help='Output file')
    content_parser.add_argument('--timeout', type=int, default=300, help='Total timeout')

    # full command
    full_parser = subparsers.add_parser('full', help='Full reconnaissance pipeline')
    full_parser.add_argument('domain', help='Target domain')
    full_parser.add_argument('-o', '--output', help='Output directory')
    full_parser.add_argument('-t', '--timeout', type=int, default=60, help='Timeout per operation')
    full_parser.add_argument('--ports', action='store_true', help='Include port scanning')
    full_parser.add_argument('--skip-vuln', action='store_true', help='Skip vulnerability scanning')

    # check command
    check_parser = subparsers.add_parser('check', help='Check tool installation')

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return

    # Run the appropriate command
    if args.command == 'check':
        cmd_check(args)
    elif args.command == 'discover':
        asyncio.run(cmd_discover(args))
    elif args.command == 'probe':
        asyncio.run(cmd_probe(args))
    elif args.command == 'ports':
        asyncio.run(cmd_ports(args))
    elif args.command == 'vuln':
        asyncio.run(cmd_vuln(args))
    elif args.command == 'content':
        asyncio.run(cmd_content(args))
    elif args.command == 'full':
        asyncio.run(cmd_full(args))


if __name__ == '__main__':
    main()
