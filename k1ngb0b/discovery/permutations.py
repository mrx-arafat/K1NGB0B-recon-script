"""
Subdomain permutation and pattern-based generation.
"""

import itertools
from typing import Set, List, Optional
from dataclasses import dataclass

from ..utils.colors import print_info, print_success


# Common subdomain prefixes and suffixes for permutations
ENVIRONMENT_PREFIXES = [
    'dev', 'development', 'staging', 'stage', 'stg', 'prod', 'production',
    'test', 'testing', 'qa', 'uat', 'demo', 'beta', 'alpha', 'preview',
    'sandbox', 'lab', 'canary', 'internal', 'external', 'private', 'public'
]

SERVICE_PREFIXES = [
    'api', 'app', 'admin', 'portal', 'dashboard', 'panel', 'manage',
    'auth', 'login', 'sso', 'oauth', 'gateway', 'proxy', 'cdn',
    'mail', 'smtp', 'imap', 'webmail', 'ftp', 'sftp', 'vpn',
    'db', 'database', 'mysql', 'postgres', 'redis', 'cache', 'elastic'
]

REGION_PREFIXES = [
    'us', 'eu', 'asia', 'apac', 'emea', 'na',
    'us-east', 'us-west', 'eu-west', 'eu-central', 'ap-south', 'ap-northeast',
    'east', 'west', 'north', 'south', 'central'
]

VERSION_SUFFIXES = [
    'v1', 'v2', 'v3', 'v4', '1', '2', '3',
    '01', '02', '03', '001', '002'
]

NUMBER_SUFFIXES = ['1', '2', '3', '01', '02', '03', '001', '002']


@dataclass
class PermutationConfig:
    """Configuration for permutation generation."""
    use_environments: bool = True
    use_services: bool = True
    use_regions: bool = False
    use_versions: bool = True
    use_numbers: bool = True
    max_permutations: int = 10000


class SubdomainPermutator:
    """Generate subdomain permutations based on discovered subdomains."""

    def __init__(self, domain: str, config: Optional[PermutationConfig] = None):
        self.domain = domain.lower().strip()
        self.config = config or PermutationConfig()

    def generate_permutations(self, known_subdomains: Set[str]) -> Set[str]:
        """Generate permutations based on known subdomains."""
        permutations: Set[str] = set()

        print_info(f"Generating permutations from {len(known_subdomains)} known subdomains...")

        # Extract base names from known subdomains
        base_names = self._extract_base_names(known_subdomains)

        # Generate environment variations
        if self.config.use_environments:
            for base in base_names:
                for env in ENVIRONMENT_PREFIXES:
                    permutations.add(f"{env}-{base}.{self.domain}")
                    permutations.add(f"{env}.{base}.{self.domain}")
                    permutations.add(f"{base}-{env}.{self.domain}")

        # Generate service variations
        if self.config.use_services:
            for base in base_names:
                for svc in SERVICE_PREFIXES:
                    permutations.add(f"{svc}-{base}.{self.domain}")
                    permutations.add(f"{base}-{svc}.{self.domain}")

        # Generate version variations
        if self.config.use_versions:
            for base in base_names:
                for ver in VERSION_SUFFIXES:
                    permutations.add(f"{base}-{ver}.{self.domain}")
                    permutations.add(f"{base}{ver}.{self.domain}")

        # Generate number variations
        if self.config.use_numbers:
            for base in base_names:
                for num in NUMBER_SUFFIXES:
                    permutations.add(f"{base}{num}.{self.domain}")
                    permutations.add(f"{base}-{num}.{self.domain}")

        # Generate region variations
        if self.config.use_regions:
            for base in base_names:
                for region in REGION_PREFIXES:
                    permutations.add(f"{region}-{base}.{self.domain}")
                    permutations.add(f"{base}-{region}.{self.domain}")

        # Limit total permutations
        if len(permutations) > self.config.max_permutations:
            permutations = set(list(permutations)[:self.config.max_permutations])

        print_success(f"Generated {len(permutations)} permutations")
        return permutations

    def _extract_base_names(self, subdomains: Set[str]) -> Set[str]:
        """Extract base names from subdomains for permutation."""
        base_names: Set[str] = set()

        for subdomain in subdomains:
            # Remove the domain suffix
            if subdomain.endswith(f".{self.domain}"):
                prefix = subdomain[:-len(f".{self.domain}")]
            else:
                continue

            # Split by dots and dashes
            parts = prefix.replace('-', '.').split('.')

            for part in parts:
                # Filter out common prefixes/numbers
                if (part and
                    len(part) > 2 and
                    not part.isdigit() and
                    part not in ENVIRONMENT_PREFIXES and
                    part not in VERSION_SUFFIXES):
                    base_names.add(part)

        return base_names

    def generate_basic_wordlist(self) -> List[str]:
        """Generate a basic subdomain wordlist."""
        words = []

        # Add environment prefixes
        words.extend(ENVIRONMENT_PREFIXES)

        # Add service prefixes
        words.extend(SERVICE_PREFIXES)

        # Add common combinations
        for env in ENVIRONMENT_PREFIXES[:5]:  # Top 5 environments
            for svc in SERVICE_PREFIXES[:10]:  # Top 10 services
                words.append(f"{env}-{svc}")
                words.append(f"{svc}-{env}")

        return words


def generate_permutations(
    domain: str,
    known_subdomains: Set[str],
    config: Optional[PermutationConfig] = None
) -> Set[str]:
    """Convenience function to generate permutations."""
    permutator = SubdomainPermutator(domain, config)
    return permutator.generate_permutations(known_subdomains)
