"""
Setup script for K1NGB0B Recon Script.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="k1ngb0b-recon",
    version="2.0.0",
    author="mrx-arafat",
    author_email="mrx.arafat@example.com",
    description="A comprehensive domain reconnaissance tool for cybersecurity professionals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrx-arafat/k1ngb0b-recon",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "k1ngb0b-recon=k1ngb0b_recon.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "k1ngb0b_recon": ["*.yaml", "*.yml"],
    },
    keywords="reconnaissance, subdomain, security, bug-bounty, cybersecurity, domain-discovery",
    project_urls={
        "Bug Reports": "https://github.com/mrx-arafat/k1ngb0b-recon/issues",
        "Source": "https://github.com/mrx-arafat/k1ngb0b-recon",
        "Documentation": "https://github.com/mrx-arafat/k1ngb0b-recon/blob/main/README.md",
    },
)
