#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║           VPN SIMULATOR - BACKEND WITH REAL PACKET CAPTURE              ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🔐 Starting backend with sudo (required for packet capture)..."
echo "📊 This will capture REAL network packets from your interface"
echo ""
echo "Press Ctrl+C to stop"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

sudo python3 backend/app.py
