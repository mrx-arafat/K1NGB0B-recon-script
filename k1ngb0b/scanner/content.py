"""
Content discovery module using FFUF.
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
class ContentResult:
    """A discovered content/endpoint."""
    url: str
    status: int
    length: int
    words: int
    lines: int
    content_type: Optional[str] = None
    redirect_location: Optional[str] = None


@dataclass
class ContentScanResult:
    """Result of content discovery."""
    results: List[ContentResult] = field(default_factory=list)
    target: str = ""
    wordlist: str = ""
    duration: float = 0.0
    total_requests: int = 0

    def get_by_status(self, status: int) -> List[ContentResult]:
        """Get results by status code."""
        return [r for r in self.results if r.status == status]

    def get_interesting(self) -> List[ContentResult]:
        """Get interesting results (200, 301, 302, 403)."""
        interesting = [200, 201, 301, 302, 307, 308, 401, 403]
        return [r for r in self.results if r.status in interesting]


class ContentScanner:
    """Content discovery using FFUF."""

    # Default wordlist locations
    WORDLIST_LOCATIONS = [
        '~/.k1ngb0b/wordlists/common.txt',
        '/usr/share/wordlists/dirb/common.txt',
        '/usr/share/seclists/Discovery/Web-Content/common.txt',
    ]

    def __init__(
        self,
        target: str,
        wordlist: Optional[str] = None,
        extensions: Optional[List[str]] = None,
        timeout: int = 300,
        threads: int = 40,
        rate_limit: int = 0
    ):
        self.target = target.rstrip('/')
        self.wordlist = wordlist
        self.extensions = extensions or []
        self.timeout = timeout
        self.threads = threads
        self.rate_limit = rate_limit
        self.config = get_config()

    def _find_wordlist(self) -> Optional[str]:
        """Find an available wordlist."""
        if self.wordlist and Path(self.wordlist).expanduser().exists():
            return str(Path(self.wordlist).expanduser())

        for location in self.WORDLIST_LOCATIONS:
            path = Path(location).expanduser()
            if path.exists():
                return str(path)

        # Try to use config wordlist
        wordlist_path = self.config.get_wordlist('web', 'common')
        if wordlist_path:
            return str(wordlist_path)

        return None

    async def scan(self) -> ContentScanResult:
        """Run content discovery scan."""
        result = ContentScanResult(target=self.target)

        # Check if ffuf is available
        tool_info = check_tool('ffuf')
        if not tool_info.available:
            print_error("FFUF not installed. Run install.py to install it.")
            return result

        # Find wordlist
        wordlist = self._find_wordlist()
        if not wordlist:
            print_error("No wordlist found. Download one to ~/.k1ngb0b/wordlists/")
            return result

        result.wordlist = wordlist
        print_info(f"Starting content discovery on {self.target}")
        print_info(f"Using wordlist: {wordlist}")

        result = await self._run_ffuf(wordlist, result)

        if result.results:
            print_success(f"Content discovery complete: {len(result.results)} paths found")
            interesting = result.get_interesting()
            if interesting:
                print_info(f"  Interesting paths: {len(interesting)}")
        else:
            print_success("Content discovery complete: No paths found")

        return result

    async def _run_ffuf(self, wordlist: str, result: ContentScanResult) -> ContentScanResult:
        """Run FFUF scanner."""
        runner = get_runner(timeout=self.timeout)

        # Build target URL with FUZZ placeholder
        target_url = f"{self.target}/FUZZ"

        # Build ffuf command
        cmd_args = [
            '-u', target_url,
            '-w', wordlist,
            '-t', str(self.threads),
            '-mc', '200,201,301,302,307,308,401,403,405,500',  # Match codes
            '-json',
            '-s',  # Silent mode
        ]

        # Add rate limit if specified
        if self.rate_limit > 0:
            cmd_args.extend(['-rate', str(self.rate_limit)])

        # Add extensions if specified
        if self.extensions:
            cmd_args.extend(['-e', ','.join(self.extensions)])

        import time
        start = time.time()

        run_result = await runner.run_tool('ffuf', cmd_args, timeout=self.timeout)
        result.duration = time.time() - start

        if run_result.success or run_result.stdout:
            result = self._parse_ffuf_output(run_result.stdout, result)
        else:
            print_warning(f"FFUF error: {run_result.stderr[:100]}")

        return result

    def _parse_ffuf_output(self, output: str, result: ContentScanResult) -> ContentScanResult:
        """Parse FFUF JSON output."""
        try:
            data = json.loads(output)

            result.total_requests = data.get('commandline', {}).get('requestcount', 0)

            for entry in data.get('results', []):
                content_result = ContentResult(
                    url=entry.get('url', ''),
                    status=entry.get('status', 0),
                    length=entry.get('length', 0),
                    words=entry.get('words', 0),
                    lines=entry.get('lines', 0),
                    content_type=entry.get('content-type'),
                    redirect_location=entry.get('redirectlocation')
                )
                result.results.append(content_result)

        except json.JSONDecodeError:
            # Try to parse line by line (older format)
            for line in output.splitlines():
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    content_result = ContentResult(
                        url=entry.get('url', ''),
                        status=entry.get('status', 0),
                        length=entry.get('length', 0),
                        words=entry.get('words', 0),
                        lines=entry.get('lines', 0)
                    )
                    result.results.append(content_result)
                except json.JSONDecodeError:
                    continue

        # Sort by status code
        result.results.sort(key=lambda r: r.status)

        return result

    def to_json(self, result: ContentScanResult) -> str:
        """Convert scan result to JSON."""
        data = {
            'target': result.target,
            'wordlist': result.wordlist,
            'total_found': len(result.results),
            'duration': result.duration,
            'results': []
        }

        for r in result.results:
            data['results'].append({
                'url': r.url,
                'status': r.status,
                'length': r.length,
                'words': r.words,
                'lines': r.lines,
                'content_type': r.content_type
            })

        return json.dumps(data, indent=2)


async def discover_content(
    target: str,
    wordlist: Optional[str] = None,
    timeout: int = 300
) -> ContentScanResult:
    """Convenience function to run content discovery."""
    scanner = ContentScanner(target, wordlist=wordlist, timeout=timeout)
    return await scanner.scan()
