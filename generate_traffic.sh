#!/bin/bash

# VPN Simulator - Continuous Traffic Generator
# This script generates continuous network traffic for demo purposes

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║           VPN SIMULATOR - CONTINUOUS TRAFFIC GENERATOR                   ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Starting continuous traffic generation..."
echo "📊 This will generate various types of network traffic"
echo "🔒 All traffic will be captured and encrypted by the VPN"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Counter for display
counter=0

# Infinite loop
while true; do
    counter=$((counter + 1))
    
    echo "[$counter] Generating traffic..."
    
    # ICMP - Ping (generates ICMP packets)
    echo "  → ICMP: Pinging 8.8.8.8..."
    ping -c 2 8.8.8.8 > /dev/null 2>&1 &
    
    # DNS - Domain lookups (generates DNS packets)
    echo "  → DNS: Looking up domains..."
    nslookup google.com > /dev/null 2>&1 &
    nslookup github.com > /dev/null 2>&1 &
    
    # HTTP - Web requests (generates TCP/HTTP packets)
    echo "  → HTTP: Fetching web pages..."
    curl -s http://example.com > /dev/null 2>&1 &
    curl -s http://httpbin.org/ip > /dev/null 2>&1 &
    
    # HTTPS - Secure web requests (generates TCP/HTTPS packets)
    echo "  → HTTPS: Secure connections..."
    curl -s https://www.google.com > /dev/null 2>&1 &
    curl -s https://api.github.com > /dev/null 2>&1 &
    
    # Additional pings to different servers
    echo "  → ICMP: Pinging multiple servers..."
    ping -c 1 1.1.1.1 > /dev/null 2>&1 &
    ping -c 1 208.67.222.222 > /dev/null 2>&1 &
    
    echo "  ✓ Traffic burst complete"
    echo ""
    
    # Wait before next burst (adjust this for more/less traffic)
    sleep 3
done
