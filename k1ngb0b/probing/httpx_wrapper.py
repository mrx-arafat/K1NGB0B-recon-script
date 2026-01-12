"""
HTTP probing module using httpx.
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
class ProbeResult:
    """Result for a single probed host."""
    url: str
    status_code: int
    title: str = ""
    content_length: int = 0
    content_type: str = ""
    web_server: str = ""
    technologies: List[str] = field(default_factory=list)
    final_url: str = ""  # After redirects
    ip: str = ""
    cname: str = ""


@dataclass
class ProbeResults:
    """Results from probing multiple hosts."""
    live_hosts: List[ProbeResult] = field(default_factory=list)
    dead_hosts: List[str] = field(default_factory=list)
    duration: float = 0.0

    @property
    def total_live(self) -> int:
        return len(self.live_hosts)

    @property
    def total_dead(self) -> int:
        return len(self.dead_hosts)

    def get_by_status(self, status: int) -> List[ProbeResult]:
        """Get results by status code."""
        return [r for r in self.live_hosts if r.status_code == status]

    def get_urls(self) -> List[str]:
        """Get all live URLs."""
        return [r.url for r in self.live_hosts]


class HttpProber:
    """HTTP probing using httpx."""

    def __init__(
        self,
        targets: List[str],
        ports: Optional[List[int]] = None,
        timeout: int = 10,
        threads: int = 50,
        follow_redirects: bool = True
    ):
        self.targets = targets
        self.ports = ports or [80, 443, 8080, 8443]
        self.timeout = timeout
        self.threads = threads
        self.follow_redirects = follow_redirects
        self.config = get_config()

    async def probe(self) -> ProbeResults:
        """Probe all targets for live HTTP services."""
        results = ProbeResults()

        if not self.targets:
            print_warning("No targets to probe")
            return results

        # Check if httpx is available
        tool_info = check_tool('httpx')
        if not tool_info.available:
            print_error("httpx not installed. Run install.py to install it.")
            return results

        print_info(f"Probing {len(self.targets)} targets for live HTTP services...")

        results = await self._run_httpx()

        print_success(f"Probing complete: {results.total_live} live, {results.total_dead} dead")
        return results

    async def _run_httpx(self) -> ProbeResults:
        """Run httpx prober."""
        results = ProbeResults()
        runner = get_runner(timeout=300)  # Total timeout for all probing

        # Create temporary file with targets
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Add protocol prefixes if not present
            for target in self.targets:
                if not target.startswith('http'):
                    f.write(f"http://{target}\n")
                    f.write(f"https://{target}\n")
                else:
                    f.write(f"{target}\n")
            targets_file = f.name

        try:
            # Build httpx command
            cmd_args = [
                '-l', targets_file,
                '-timeout', str(self.timeout),
                '-threads', str(self.threads),
                '-status-code',
                '-title',
                '-content-length',
                '-content-type',
                '-web-server',
                '-tech-detect',
                '-ip',
                '-cname',
                '-json',
                '-silent',
            ]

            if self.follow_redirects:
                cmd_args.append('-follow-redirects')
                cmd_args.append('-location')

            import time
            start = time.time()

            run_result = await runner.run_tool('httpx', cmd_args, timeout=300)
            results.duration = time.time() - start

            if run_result.success or run_result.stdout:
                results = self._parse_httpx_output(run_result.stdout, results)
            else:
                print_warning(f"httpx error: {run_result.stderr[:100]}")

        finally:
            # Cleanup temp file
            Path(targets_file).unlink(missing_ok=True)

        return results

    def _parse_httpx_output(self, output: str, results: ProbeResults) -> ProbeResults:
        """Parse httpx JSON output."""
        seen_hosts = set()

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                url = data.get('url', '')
                if not url:
                    continue

                # Track unique hosts
                from urllib.parse import urlparse
                parsed = urlparse(url)
                host_key = parsed.netloc

                if host_key in seen_hosts:
                    continue
                seen_hosts.add(host_key)

                probe_result = ProbeResult(
                    url=url,
                    status_code=data.get('status_code', 0),
                    title=data.get('title', ''),
                    content_length=data.get('content_length', 0),
                    content_type=data.get('content_type', ''),
                    web_server=data.get('webserver', ''),
                    technologies=data.get('tech', []),
                    final_url=data.get('final_url', url),
                    ip=data.get('host', ''),
                    cname=data.get('cname', '')
                )

                results.live_hosts.append(probe_result)

            except json.JSONDecodeError:
                continue

        # Calculate dead hosts
        probed_hosts = set()
        for r in results.live_hosts:
            from urllib.parse import urlparse
            parsed = urlparse(r.url)
            probed_hosts.add(parsed.netloc.split(':')[0])

        for target in self.targets:
            if target.replace('http://', '').replace('https://', '').split('/')[0] not in probed_hosts:
                results.dead_hosts.append(target)

        # Sort by status code
        results.live_hosts.sort(key=lambda r: r.status_code)

        return results

    def to_json(self, results: ProbeResults) -> str:
        """Convert results to JSON."""
        data = {
            'summary': {
                'total_live': results.total_live,
                'total_dead': results.total_dead,
                'duration': results.duration
            },
            'live_hosts': [],
            'dead_hosts': results.dead_hosts
        }

        for r in results.live_hosts:
            data['live_hosts'].append({
                'url': r.url,
                'status_code': r.status_code,
                'title': r.title,
                'content_length': r.content_length,
                'content_type': r.content_type,
                'web_server': r.web_server,
                'technologies': r.technologies,
                'ip': r.ip
            })

        return json.dumps(data, indent=2)


async def probe_hosts(
    targets: List[str],
    timeout: int = 10,
    threads: int = 50
) -> ProbeResults:
    """Convenience function to probe hosts."""
    prober = HttpProber(targets, timeout=timeout, threads=threads)
    return await prober.probe()
