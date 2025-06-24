#!/usr/bin/env python3

"""
🔥 K1NGB0B Port Scanner v1.0 - Fast Port Discovery with RustScan
Advanced port scanning using RustScan for maximum speed and efficiency
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import time

class K1NGB0BPortScanner:
    def __init__(self):
        self.banner = """
🔥 K1NGB0B Port Scanner v1.0 - Fast Port Discovery
⚡ Powered by RustScan for maximum speed and efficiency
🎯 Professional port scanning for reconnaissance
        """
        
    def print_banner(self):
        print(self.banner)
        
    def check_rustscan(self):
        """Check if rustscan is installed"""
        try:
            result = subprocess.run(['rustscan', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ RustScan found: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        print("❌ RustScan not found!")
        print("\n📦 Install RustScan:")
        print("   cargo install rustscan")
        print("   # OR")
        print("   wget https://github.com/RustScan/RustScan/releases/download/2.0.1/rustscan_2.0.1_amd64.deb")
        print("   sudo dpkg -i rustscan_2.0.1_amd64.deb")
        return False
        
    def load_targets(self, input_file):
        """Load targets from file"""
        targets = []
        try:
            with open(input_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        targets.append(line)
            print(f"📋 Loaded {len(targets)} targets from {input_file}")
            return targets
        except FileNotFoundError:
            print(f"❌ File not found: {input_file}")
            return []
            
    def create_output_dir(self, target_name):
        """Create output directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"{target_name}_ports_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
        
    def run_rustscan(self, targets, output_dir, ports=None, top_ports=None):
        """Run RustScan on targets"""
        print(f"\n🚀 Starting RustScan on {len(targets)} targets...")
        
        # Prepare targets file
        targets_file = os.path.join(output_dir, "targets.txt")
        with open(targets_file, 'w') as f:
            for target in targets:
                f.write(f"{target}\n")
                
        # Build rustscan command
        cmd = [
            'rustscan',
            '-a', targets_file,
            '--ulimit', '5000',
            '--timeout', '3000',
            '--tries', '1',
            '--batch-size', '4500'
        ]
        
        # Add port specification
        if ports:
            cmd.extend(['-p', ports])
        elif top_ports:
            cmd.extend(['--top'])
        else:
            # Default: scan top 1000 ports
            cmd.extend(['--top'])
            
        # Output files
        json_output = os.path.join(output_dir, "rustscan_results.json")
        txt_output = os.path.join(output_dir, "rustscan_results.txt")
        
        print(f"📊 Command: {' '.join(cmd)}")
        print(f"📁 Output directory: {output_dir}")
        
        try:
            # Run rustscan
            start_time = time.time()
            with open(txt_output, 'w') as f:
                process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
                print("⏳ RustScan running... (this may take a while)")
                stderr_output = process.communicate()[1]
                
            end_time = time.time()
            duration = end_time - start_time
            
            if process.returncode == 0:
                print(f"✅ RustScan completed in {duration:.1f} seconds")
                self.parse_results(txt_output, json_output)
                return True
            else:
                print(f"❌ RustScan failed with return code {process.returncode}")
                if stderr_output:
                    print(f"Error: {stderr_output}")
                return False
                
        except Exception as e:
            print(f"❌ Error running RustScan: {e}")
            return False
            
    def parse_results(self, txt_file, json_file):
        """Parse RustScan results and create JSON summary"""
        results = {
            "scan_info": {
                "timestamp": datetime.now().isoformat(),
                "tool": "rustscan",
                "total_hosts": 0,
                "hosts_with_open_ports": 0,
                "total_open_ports": 0
            },
            "hosts": {}
        }
        
        try:
            with open(txt_file, 'r') as f:
                content = f.read()
                
            # Parse rustscan output
            lines = content.split('\n')
            current_host = None
            
            for line in lines:
                line = line.strip()
                
                # Look for host lines
                if "Open" in line and "->" in line:
                    # Format: "Open 192.168.1.1:22"
                    parts = line.split()
                    if len(parts) >= 2:
                        host_port = parts[1]
                        if ':' in host_port:
                            host, port = host_port.split(':')
                            
                            if host not in results["hosts"]:
                                results["hosts"][host] = {
                                    "hostname": host,
                                    "open_ports": []
                                }
                                
                            results["hosts"][host]["open_ports"].append({
                                "port": int(port),
                                "protocol": "tcp",
                                "state": "open"
                            })
                            
            # Calculate statistics
            results["scan_info"]["total_hosts"] = len(results["hosts"])
            results["scan_info"]["hosts_with_open_ports"] = len([h for h in results["hosts"].values() if h["open_ports"]])
            results["scan_info"]["total_open_ports"] = sum(len(h["open_ports"]) for h in results["hosts"].values())
            
            # Save JSON results
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"📊 Scan Results:")
            print(f"   🎯 Total hosts scanned: {results['scan_info']['total_hosts']}")
            print(f"   🟢 Hosts with open ports: {results['scan_info']['hosts_with_open_ports']}")
            print(f"   🔌 Total open ports: {results['scan_info']['total_open_ports']}")
            
            # Show top findings
            if results["hosts"]:
                print(f"\n🔥 Top Findings:")
                for host, data in list(results["hosts"].items())[:5]:
                    if data["open_ports"]:
                        ports = [str(p["port"]) for p in data["open_ports"]]
                        print(f"   🎯 {host}: {', '.join(ports)}")
                        
        except Exception as e:
            print(f"❌ Error parsing results: {e}")
            
    def main(self):
        parser = argparse.ArgumentParser(description="K1NGB0B Port Scanner - Fast port discovery with RustScan")
        parser.add_argument('-t', '--target', help='Single target to scan')
        parser.add_argument('-f', '--file', help='File containing targets (one per line)')
        parser.add_argument('-p', '--ports', help='Specific ports to scan (e.g., "22,80,443" or "1-1000")')
        parser.add_argument('--top', action='store_true', help='Scan top 1000 ports (default)')
        parser.add_argument('-o', '--output', help='Output directory name')
        
        args = parser.parse_args()
        
        self.print_banner()
        
        # Check if rustscan is installed
        if not self.check_rustscan():
            sys.exit(1)
            
        # Get targets
        targets = []
        if args.target:
            targets = [args.target]
        elif args.file:
            targets = self.load_targets(args.file)
        else:
            # Interactive mode
            target = input("\n🎯 Enter target domain/IP (or file path with -f): ").strip()
            if os.path.isfile(target):
                targets = self.load_targets(target)
            else:
                targets = [target]
                
        if not targets:
            print("❌ No targets specified!")
            sys.exit(1)
            
        # Create output directory
        if args.output:
            output_dir = args.output
            os.makedirs(output_dir, exist_ok=True)
        else:
            target_name = targets[0].replace('.', '_').replace('/', '_')
            output_dir = self.create_output_dir(target_name)
            
        # Run scan
        success = self.run_rustscan(targets, output_dir, args.ports, args.top)
        
        if success:
            print(f"\n✅ Port scan completed!")
            print(f"📁 Results saved to: {output_dir}/")
            print(f"📊 JSON results: {output_dir}/rustscan_results.json")
            print(f"📋 Raw output: {output_dir}/rustscan_results.txt")
        else:
            print(f"\n❌ Port scan failed!")
            
if __name__ == "__main__":
    scanner = K1NGB0BPortScanner()
    scanner.main()
