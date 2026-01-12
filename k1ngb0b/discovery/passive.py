"""
Passive subdomain discovery through CT logs, DNS aggregators, and public APIs.
"""

import asyncio
import json
import re
import random
from typing import List, Set, Dict, Optional
from dataclasses import dataclass, field

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from ..utils.colors import print_info, print_success, print_warning, print_error
from ..utils.runner import run_sync


@dataclass
class DiscoveryResult:
    """Result from a passive discovery source."""
    source: str
    subdomains: Set[str] = field(default_factory=set)
    success: bool = True
    error: Optional[str] = None


def is_valid_subdomain(subdomain: str, domain: str) -> bool:
    """Validate if a subdomain belongs to the target domain."""
    if not subdomain or not domain:
        return False

    subdomain = subdomain.lower().strip()
    domain = domain.lower().strip()

    # Remove wildcards
    subdomain = subdomain.replace('*.', '')

    # Must end with the domain
    if not subdomain.endswith(domain):
        return False

    # Basic validation
    if len(subdomain) > 255:
        return False

    # Check for valid characters
    pattern = r'^[a-z0-9]([a-z0-9\-\.]*[a-z0-9])?$'
    if not re.match(pattern, subdomain):
        return False

    return True


class PassiveDiscovery:
    """Passive subdomain discovery using multiple sources."""

    # User agent for requests
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

    def __init__(self, domain: str, timeout: int = 45):
        self.domain = domain.lower().strip()
        self.timeout = timeout
        self.discovered: Set[str] = set()
        self.results: Dict[str, DiscoveryResult] = {}

    async def run_all(self) -> Set[str]:
        """Run all passive discovery sources."""
        print_info(f"Starting passive discovery for {self.domain}")

        if not AIOHTTP_AVAILABLE:
            print_warning("aiohttp not available, using fallback methods")
            return await self._run_fallback()

        # Run all sources concurrently
        tasks = [
            self._query_crtsh(),
            self._query_certspotter(),
            self._query_subdomain_center(),
            self._query_hackertarget(),
            self._query_threatcrowd(),
            self._query_rapiddns(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, DiscoveryResult):
                self.results[result.source] = result
                self.discovered.update(result.subdomains)
            elif isinstance(result, Exception):
                print_warning(f"Discovery task failed: {result}")

        print_success(f"Passive discovery complete: {len(self.discovered)} subdomains found")
        return self.discovered

    async def _run_fallback(self) -> Set[str]:
        """Fallback discovery using curl."""
        # Use crt.sh with curl
        result = run_sync([
            'curl', '-s', f'https://crt.sh/?q=%.{self.domain}&output=json'
        ], timeout=30)

        if result.success and result.stdout:
            try:
                data = json.loads(result.stdout)
                for entry in data:
                    name_value = entry.get('name_value', '')
                    for sub in name_value.split('\n'):
                        clean = sub.strip().replace('*.', '')
                        if is_valid_subdomain(clean, self.domain):
                            self.discovered.add(clean.lower())
            except json.JSONDecodeError:
                pass

        # Use hackertarget with curl
        result = run_sync([
            'curl', '-s', f'https://api.hackertarget.com/hostsearch/?q={self.domain}'
        ], timeout=30)

        if result.success and result.stdout:
            for line in result.stdout.split('\n'):
                if ',' in line:
                    subdomain = line.split(',')[0].strip()
                    if is_valid_subdomain(subdomain, self.domain):
                        self.discovered.add(subdomain.lower())

        return self.discovered

    async def _make_request(
        self,
        url: str,
        headers: Optional[Dict] = None
    ) -> Optional[aiohttp.ClientResponse]:
        """Make an async HTTP request with error handling."""
        if headers is None:
            headers = {
                'User-Agent': self.USER_AGENT,
                'Accept': 'application/json, text/plain, */*',
            }

        try:
            connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception:
            pass

        return None

    async def _query_crtsh(self) -> DiscoveryResult:
        """Query crt.sh Certificate Transparency logs."""
        result = DiscoveryResult(source='crt.sh')

        url = f'https://crt.sh/?q=%.{self.domain}&output=json'
        print_info(f"  Querying crt.sh...")

        try:
            text = await self._make_request(url)
            if text:
                data = json.loads(text)
                for entry in data:
                    name_value = entry.get('name_value', '')
                    for sub in name_value.split('\n'):
                        clean = sub.strip().replace('*.', '')
                        if is_valid_subdomain(clean, self.domain):
                            result.subdomains.add(clean.lower())
        except Exception as e:
            result.success = False
            result.error = str(e)

        # Rate limit
        await asyncio.sleep(random.uniform(0.5, 1.5))
        return result

    async def _query_certspotter(self) -> DiscoveryResult:
        """Query CertSpotter API."""
        result = DiscoveryResult(source='certspotter')

        url = f'https://api.certspotter.com/v1/issuances?domain={self.domain}&include_subdomains=true&expand=dns_names'
        print_info(f"  Querying CertSpotter...")

        try:
            text = await self._make_request(url)
            if text:
                data = json.loads(text)
                for entry in data:
                    dns_names = entry.get('dns_names', [])
                    for name in dns_names:
                        clean = name.strip().replace('*.', '')
                        if is_valid_subdomain(clean, self.domain):
                            result.subdomains.add(clean.lower())
        except Exception as e:
            result.success = False
            result.error = str(e)

        await asyncio.sleep(random.uniform(0.5, 1.5))
        return result

    async def _query_subdomain_center(self) -> DiscoveryResult:
        """Query subdomain.center API."""
        result = DiscoveryResult(source='subdomain.center')

        url = f'https://api.subdomain.center/?domain={self.domain}'
        print_info(f"  Querying subdomain.center...")

        try:
            text = await self._make_request(url)
            if text:
                data = json.loads(text)
                for subdomain in data:
                    if is_valid_subdomain(subdomain, self.domain):
                        result.subdomains.add(subdomain.lower())
        except Exception as e:
            result.success = False
            result.error = str(e)

        await asyncio.sleep(random.uniform(0.5, 1.5))
        return result

    async def _query_hackertarget(self) -> DiscoveryResult:
        """Query HackerTarget API."""
        result = DiscoveryResult(source='hackertarget')

        url = f'https://api.hackertarget.com/hostsearch/?q={self.domain}'
        print_info(f"  Querying HackerTarget...")

        try:
            text = await self._make_request(url)
            if text:
                for line in text.split('\n'):
                    if ',' in line:
                        subdomain = line.split(',')[0].strip()
                        if is_valid_subdomain(subdomain, self.domain):
                            result.subdomains.add(subdomain.lower())
        except Exception as e:
            result.success = False
            result.error = str(e)

        await asyncio.sleep(random.uniform(0.5, 1.5))
        return result

    async def _query_threatcrowd(self) -> DiscoveryResult:
        """Query ThreatCrowd API."""
        result = DiscoveryResult(source='threatcrowd')

        url = f'https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={self.domain}'
        print_info(f"  Querying ThreatCrowd...")

        try:
            text = await self._make_request(url)
            if text:
                data = json.loads(text)
                if 'subdomains' in data:
                    for subdomain in data['subdomains']:
                        if is_valid_subdomain(subdomain, self.domain):
                            result.subdomains.add(subdomain.lower())
        except Exception as e:
            result.success = False
            result.error = str(e)

        await asyncio.sleep(random.uniform(1.0, 2.0))
        return result

    async def _query_rapiddns(self) -> DiscoveryResult:
        """Query RapidDNS."""
        result = DiscoveryResult(source='rapiddns')

        url = f'https://rapiddns.io/subdomain/{self.domain}?full=1'
        print_info(f"  Querying RapidDNS...")

        try:
            text = await self._make_request(url)
            if text:
                # Parse HTML for subdomains
                pattern = rf'([a-zA-Z0-9]([a-zA-Z0-9\-]{{0,61}}[a-zA-Z0-9])?\.)*{re.escape(self.domain)}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple) and match[0]:
                        subdomain = match[0].rstrip('.') + self.domain
                    else:
                        subdomain = str(match)
                    if is_valid_subdomain(subdomain, self.domain):
                        result.subdomains.add(subdomain.lower())
        except Exception as e:
            result.success = False
            result.error = str(e)

        await asyncio.sleep(random.uniform(1.0, 2.0))
        return result

    def get_summary(self) -> str:
        """Get a summary of discovery results."""
        lines = [f"Passive Discovery Summary for {self.domain}"]
        lines.append("-" * 50)

        for source, result in self.results.items():
            status = "OK" if result.success else "FAILED"
            lines.append(f"  {source}: {len(result.subdomains)} subdomains [{status}]")

        lines.append("-" * 50)
        lines.append(f"Total unique subdomains: {len(self.discovered)}")

        return '\n'.join(lines)
