#!/bin/bash

# Quick installation script for K1NGB0B Recon Script
# This script installs only the essential tools

set -e

echo "K1NGB0B Recon - Quick Install"
echo "============================="

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Go tools (assuming Go is already installed)
echo "Installing Go tools..."
go install github.com/tomnomnom/assetfinder@latest
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/tomnomnom/anew@latest

echo "Quick installation completed!"
echo "Usage: python3 -m k1ngb0b_recon <domain>"
