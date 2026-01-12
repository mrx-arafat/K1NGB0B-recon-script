"""
Active subdomain discovery using external tools.
"""

import asyncio
import shutil
from pathlib import Path
from typing import Set, List, Optional, Dict
from dataclasses import dataclass, field

from ..utils.runner import AsyncRunner, get_runner, run_sync
from ..utils.tools import check_tool, get_available_tools
from ..utils.colors import print_info, print_success, print_warning, print_error
from ..config import get_config


@dataclass
class ToolResult:
    """Result from running a discovery tool."""
    tool: str
    subdomains: Set[str] = field(default_factory=set)
    success: bool = True
    error: Optional[str] = None
    duration: float = 0.0


class ActiveDiscovery:
    """Active subdomain discovery using security tools."""

    # Tools in order of preference
    DISCOVERY_TOOLS = ['subfinder', 'assetfinder', 'amass', 'findomain']

    def __init__(self, domain: str, timeout: int = 300):
        self.domain = domain.lower().strip()
        self.timeout = timeout
        self.discovered: Set[str] = set()
        self.results: Dict[str, ToolResult] = {}
        self.config = get_config()

    async def run_all(self) -> Set[str]:
        """Run all available discovery tools."""
        print_info(f"Starting active discovery for {self.domain}")

        available = get_available_tools(self.DISCOVERY_TOOLS)

        if not available:
            print_warning("No discovery tools available. Run install.py to install them.")
            return self.discovered

        print_info(f"Available tools: {', '.join(available)}")

        runner = get_runner(timeout=self.timeout)

        # Run tools concurrently
        tasks = []
        for tool in available:
            if tool == 'subfinder':
                tasks.append(self._run_subfinder(runner))
            elif tool == 'assetfinder':
                tasks.append(self._run_assetfinder(runner))
            elif tool == 'amass':
                tasks.append(self._run_amass(runner))
            elif tool == 'findomain':
                tasks.append(self._run_findomain(runner))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, ToolResult):
                self.results[result.tool] = result
                self.discovered.update(result.subdomains)
                if result.success:
                    print_success(f"  {result.tool}: {len(result.subdomains)} subdomains")
                else:
                    print_warning(f"  {result.tool}: failed - {result.error}")
            elif isinstance(result, Exception):
                print_warning(f"Tool task failed: {result}")

        print_success(f"Active discovery complete: {len(self.discovered)} subdomains found")
        return self.discovered

    def _parse_output(self, output: str) -> Set[str]:
        """Parse tool output for subdomains."""
        subdomains = set()
        for line in output.splitlines():
            line = line.strip()
            if line and self.domain in line:
                # Clean up the subdomain
                sub = line.lower()
                # Remove common prefixes
                for prefix in ['http://', 'https://', 'www.']:
                    if sub.startswith(prefix):
                        sub = sub[len(prefix):]
                # Remove paths
                if '/' in sub:
                    sub = sub.split('/')[0]
                # Remove ports
                if ':' in sub:
                    sub = sub.split(':')[0]

                if sub.endswith(self.domain) and len(sub) <= 255:
                    subdomains.add(sub)

        return subdomains

    async def _run_subfinder(self, runner: AsyncRunner) -> ToolResult:
        """Run subfinder for subdomain enumeration."""
        result = ToolResult(tool='subfinder')
        print_info("  Running subfinder...")

        run_result = await runner.run_tool(
            'subfinder',
            ['-d', self.domain, '-silent', '-all'],
            timeout=self.timeout
        )

        result.duration = run_result.duration

        if run_result.success:
            result.subdomains = self._parse_output(run_result.stdout)
        else:
            result.success = False
            result.error = run_result.stderr[:100] if run_result.stderr else "Unknown error"

        return result

    async def _run_assetfinder(self, runner: AsyncRunner) -> ToolResult:
        """Run assetfinder for subdomain enumeration."""
        result = ToolResult(tool='assetfinder')
        print_info("  Running assetfinder...")

        run_result = await runner.run_tool(
            'assetfinder',
            ['--subs-only', self.domain],
            timeout=self.timeout
        )

        result.duration = run_result.duration

        if run_result.success:
            result.subdomains = self._parse_output(run_result.stdout)
        else:
            result.success = False
            result.error = run_result.stderr[:100] if run_result.stderr else "Unknown error"

        return result

    async def _run_amass(self, runner: AsyncRunner) -> ToolResult:
        """Run amass for subdomain enumeration."""
        result = ToolResult(tool='amass')
        print_info("  Running amass (passive mode)...")

        # Use passive mode for speed
        run_result = await runner.run_tool(
            'amass',
            ['enum', '-passive', '-d', self.domain],
            timeout=self.timeout
        )

        result.duration = run_result.duration

        if run_result.success:
            result.subdomains = self._parse_output(run_result.stdout)
        else:
            result.success = False
            result.error = run_result.stderr[:100] if run_result.stderr else "Unknown error"

        return result

    async def _run_findomain(self, runner: AsyncRunner) -> ToolResult:
        """Run findomain for subdomain enumeration."""
        result = ToolResult(tool='findomain')
        print_info("  Running findomain...")

        run_result = await runner.run_tool(
            'findomain',
            ['-t', self.domain, '-q'],
            timeout=self.timeout
        )

        result.duration = run_result.duration

        if run_result.success:
            result.subdomains = self._parse_output(run_result.stdout)
        else:
            result.success = False
            result.error = run_result.stderr[:100] if run_result.stderr else "Unknown error"

        return result

    def get_summary(self) -> str:
        """Get a summary of discovery results."""
        lines = [f"Active Discovery Summary for {self.domain}"]
        lines.append("-" * 50)

        for tool, result in self.results.items():
            status = "OK" if result.success else "FAILED"
            time_str = f"{result.duration:.1f}s"
            lines.append(f"  {tool}: {len(result.subdomains)} subdomains [{status}] ({time_str})")

        lines.append("-" * 50)
        lines.append(f"Total unique subdomains: {len(self.discovered)}")

        return '\n'.join(lines)


async def run_discovery(domain: str, timeout: int = 300) -> Set[str]:
    """Convenience function to run active discovery."""
    discovery = ActiveDiscovery(domain, timeout)
    return await discovery.run_all()
