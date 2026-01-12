"""
Vulnerability scanning module using Nuclei.
"""

import asyncio
import json
from pathlib import Path
from typing import Set, List, Dict, Optional
from dataclasses import dataclass, field

from ..utils.runner import AsyncRunner, get_runner
from ..utils.tools import check_tool
from ..utils.colors import print_info, print_success, print_warning, print_error
from ..config import get_config


@dataclass
class Finding:
    """A vulnerability finding from Nuclei."""
    template_id: str
    name: str
    severity: str
    host: str
    matched_at: str
    extracted_results: List[str] = field(default_factory=list)
    curl_command: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class VulnScanResult:
    """Result of vulnerability scanning."""
    findings: List[Finding] = field(default_factory=list)
    total_requests: int = 0
    duration: float = 0.0
    hosts_scanned: int = 0

    @property
    def critical_count(self) -> int:
        return len([f for f in self.findings if f.severity == 'critical'])

    @property
    def high_count(self) -> int:
        return len([f for f in self.findings if f.severity == 'high'])

    @property
    def medium_count(self) -> int:
        return len([f for f in self.findings if f.severity == 'medium'])

    @property
    def low_count(self) -> int:
        return len([f for f in self.findings if f.severity == 'low'])

    @property
    def info_count(self) -> int:
        return len([f for f in self.findings if f.severity == 'info'])


class VulnerabilityScanner:
    """Vulnerability scanning using Nuclei."""

    # Severity levels in order of importance
    SEVERITY_ORDER = ['critical', 'high', 'medium', 'low', 'info']

    def __init__(
        self,
        targets: List[str],
        severity: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        templates: Optional[List[str]] = None,
        timeout: int = 600,
        rate_limit: int = 150,
        concurrency: int = 25
    ):
        self.targets = targets
        self.severity = severity or ['critical', 'high', 'medium']
        self.tags = tags
        self.templates = templates
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.concurrency = concurrency
        self.config = get_config()

    async def scan(self) -> VulnScanResult:
        """Run vulnerability scan on targets."""
        result = VulnScanResult()

        if not self.targets:
            print_warning("No targets to scan")
            return result

        # Check if nuclei is available
        tool_info = check_tool('nuclei')
        if not tool_info.available:
            print_error("Nuclei not installed. Run install.py to install it.")
            return result

        print_info(f"Starting vulnerability scan on {len(self.targets)} targets...")
        print_info(f"Severity filter: {', '.join(self.severity)}")

        result = await self._run_nuclei()

        # Print summary
        if result.findings:
            print_success(f"Vulnerability scan complete: {len(result.findings)} findings")
            print_info(f"  Critical: {result.critical_count}, High: {result.high_count}, "
                      f"Medium: {result.medium_count}, Low: {result.low_count}")
        else:
            print_success("Vulnerability scan complete: No findings")

        return result

    async def _run_nuclei(self) -> VulnScanResult:
        """Run nuclei scanner."""
        result = VulnScanResult()
        runner = get_runner(timeout=self.timeout)

        # Create temporary file with targets
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('\n'.join(self.targets))
            targets_file = f.name

        try:
            # Build nuclei command
            cmd_args = [
                '-l', targets_file,
                '-severity', ','.join(self.severity),
                '-rate-limit', str(self.rate_limit),
                '-c', str(self.concurrency),
                '-json',
                '-silent',
            ]

            # Add tags filter if specified
            if self.tags:
                cmd_args.extend(['-tags', ','.join(self.tags)])

            # Add specific templates if specified
            if self.templates:
                for template in self.templates:
                    cmd_args.extend(['-t', template])

            import time
            start = time.time()

            run_result = await runner.run_tool('nuclei', cmd_args, timeout=self.timeout)
            result.duration = time.time() - start
            result.hosts_scanned = len(self.targets)

            if run_result.success or run_result.stdout:
                result = self._parse_nuclei_output(run_result.stdout, result)
            else:
                print_warning(f"Nuclei error: {run_result.stderr[:100]}")

        finally:
            # Cleanup temp file
            Path(targets_file).unlink(missing_ok=True)

        return result

    def _parse_nuclei_output(self, output: str, result: VulnScanResult) -> VulnScanResult:
        """Parse Nuclei JSON output."""
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                finding = Finding(
                    template_id=data.get('template-id', ''),
                    name=data.get('info', {}).get('name', ''),
                    severity=data.get('info', {}).get('severity', 'info'),
                    host=data.get('host', ''),
                    matched_at=data.get('matched-at', ''),
                    extracted_results=data.get('extracted-results', []),
                    curl_command=data.get('curl-command'),
                    description=data.get('info', {}).get('description'),
                    tags=data.get('info', {}).get('tags', [])
                )

                result.findings.append(finding)

            except json.JSONDecodeError:
                continue

        # Sort findings by severity
        severity_order = {s: i for i, s in enumerate(self.SEVERITY_ORDER)}
        result.findings.sort(key=lambda f: severity_order.get(f.severity, 99))

        return result

    def to_json(self, result: VulnScanResult) -> str:
        """Convert scan result to JSON."""
        data = {
            'summary': {
                'total_findings': len(result.findings),
                'critical': result.critical_count,
                'high': result.high_count,
                'medium': result.medium_count,
                'low': result.low_count,
                'info': result.info_count,
                'hosts_scanned': result.hosts_scanned,
                'duration': result.duration
            },
            'findings': []
        }

        for finding in result.findings:
            data['findings'].append({
                'template_id': finding.template_id,
                'name': finding.name,
                'severity': finding.severity,
                'host': finding.host,
                'matched_at': finding.matched_at,
                'description': finding.description,
                'tags': finding.tags
            })

        return json.dumps(data, indent=2)


async def scan_vulnerabilities(
    targets: List[str],
    severity: Optional[List[str]] = None,
    timeout: int = 600
) -> VulnScanResult:
    """Convenience function to run vulnerability scan."""
    scanner = VulnerabilityScanner(targets, severity=severity, timeout=timeout)
    return await scanner.scan()
