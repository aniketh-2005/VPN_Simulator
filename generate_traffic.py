#!/usr/bin/env python3
"""
VPN Simulator - Continuous Traffic Generator (Python version)
Generates continuous network traffic for demo purposes
"""

import subprocess
import time
import sys
from datetime import datetime

def print_header():
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                          ║")
    print("║           VPN SIMULATOR - CONTINUOUS TRAFFIC GENERATOR                   ║")
    print("║                                                                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print()
    print("🚀 Starting continuous traffic generation...")
    print("📊 This will generate various types of network traffic")
    print("🔒 All traffic will be captured and encrypted by the VPN")
    print()
    print("Press Ctrl+C to stop")
    print()
    print("═══════════════════════════════════════════════════════════════════════════")
    print()

def run_command(cmd, description):
    """Run a command silently"""
    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
        print(f"  → {description}")
    except Exception as e:
        print(f"  ✗ {description} failed: {e}")

def generate_traffic_burst(counter):
    """Generate a burst of network traffic"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{counter}] {timestamp} - Generating traffic...")
    
    # ICMP - Ping
    run_command("ping -c 2 8.8.8.8", "ICMP: Pinging 8.8.8.8")
    run_command("ping -c 1 1.1.1.1", "ICMP: Pinging 1.1.1.1")
    
    # DNS - Domain lookups
    run_command("nslookup google.com", "DNS: Looking up google.com")
    run_command("nslookup github.com", "DNS: Looking up github.com")
    
    # HTTP - Web requests
    run_command("curl -s http://example.com", "HTTP: Fetching example.com")
    run_command("curl -s http://httpbin.org/ip", "HTTP: Fetching httpbin.org")
    
    # HTTPS - Secure web requests
    run_command("curl -s https://www.google.com", "HTTPS: Fetching google.com")
    run_command("curl -s https://api.github.com", "HTTPS: Fetching github.com")
    
    print("  ✓ Traffic burst complete")
    print()

def main():
    print_header()
    
    counter = 0
    
    try:
        while True:
            counter += 1
            generate_traffic_burst(counter)
            
            # Wait before next burst (adjust for more/less traffic)
            time.sleep(3)
            
    except KeyboardInterrupt:
        print()
        print("═══════════════════════════════════════════════════════════════════════════")
        print()
        print(f"🛑 Stopped after {counter} traffic bursts")
        print("✓ Traffic generation complete")
        print()
        sys.exit(0)

if __name__ == "__main__":
    main()
