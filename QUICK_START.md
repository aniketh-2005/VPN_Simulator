# Quick Start Guide - VPN Simulator with Real Wireshark Capture

## ✅ System Status

Your system is ready for **REAL packet capture** using **scapy**!

## 🚀 Quick Start (3 Steps)

### Step 1: Test Your Setup
```bash
python3 test_capture.py
```

### Step 2: Start Backend with sudo (for REAL capture)
```bash
sudo python3 backend/app.py
```
**Password required** - This allows capturing real network packets

### Step 3: Start Frontend (in new terminal)
```bash
cd frontend
python3 -m http.server 8080
```

### Step 4: Open Browser
```
http://localhost:8080
```

## 🎮 Demo Flow

### 1. Test IP Filtering (2 minutes)
```
✅ Default IP: 192.168.1.100 (allowed)
   - Click "Connect" → Success!

❌ Change IP to: 192.168.1.200 (blocked)
   - Click "Change IP" → Enter: 192.168.1.200
   - Click "Connect" → BLOCKED!

✅ Change back to: 192.168.1.100
   - Click "Change IP" → Enter: 192.168.1.100
   - Click "Connect" → Success!
```

### 2. Start Real Packet Capture (3 minutes)
```
1. Connect to VPN (select any server)
2. Click "Start Capture"
3. Generate traffic:
   - Open new tab: google.com
   - Open new tab: youtube.com
   - Terminal: curl http://example.com
4. Watch REAL packets appear!
5. See protocol distribution chart
```

### 3. Generate More Traffic (Optional)
```bash
# In a new terminal, run these commands:

# HTTP traffic
curl http://example.com

# Multiple requests
for i in {1..5}; do curl -s http://example.com > /dev/null; sleep 1; done

# DNS queries
nslookup google.com
nslookup youtube.com

# Ping (ICMP)
ping -c 5 8.8.8.8
```

## 📊 What You'll See

### Real Packet Capture Shows:
- ✅ **Real source IPs** from your computer
- ✅ **Real destination IPs** (Google, YouTube, etc.)
- ✅ **Actual protocols** (TCP, UDP, HTTP, HTTPS, DNS)
- ✅ **Real packet sizes** (not random numbers)
- ✅ **Live timestamps**

### Simulated Capture Shows:
- ⚠️ Random IPs
- ⚠️ "(simulated)" label in packet info

## 🎯 For Your Project Guide

### Presentation Points:

**1. IP Access Control:**
- "We implemented whitelist/blacklist for IP filtering"
- "Only approved IPs can connect to the VPN"
- Demo: Show blocked IP getting denied

**2. Real Packet Capture:**
- "We're using Scapy to capture REAL network packets"
- "This is the same technology Wireshark uses"
- Demo: Show real packets from browsing

**3. Protocol Analysis:**
- "We analyze different protocols: TCP, UDP, HTTP, HTTPS, DNS"
- "The chart shows protocol distribution"
- Demo: Show protocol breakdown

**4. VPN Simulation:**
- "IP address changes when connected"
- "Different servers have different latencies"
- "Real-time traffic statistics"

## 🔧 Troubleshooting

### "Permission denied" when capturing
```bash
# Solution: Run with sudo
sudo python3 backend/app.py
```

### No packets appearing
```bash
# 1. Make sure you're connected to VPN first
# 2. Generate traffic (open websites)
# 3. Check backend console for errors
# 4. Try: sudo python3 backend/app.py
```

### "Port already in use"
```bash
# Kill existing processes
lsof -ti:5001 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

## 📝 Allowed vs Blocked IPs

### ✅ Allowed IPs (will connect):
- 192.168.1.100 (default)
- 192.168.1.101
- 192.168.1.105
- 10.0.0.50
- 172.16.0.25

### ❌ Blocked IPs (will be denied):
- 192.168.1.200
- 10.0.0.99
- 172.16.0.100

### 🔍 Test any IP:
Use the "Check IP" tool in the UI!

## 🎉 You're Ready!

Your VPN simulator with real Wireshark capture is ready to demo!

**Current Status:**
- ✅ Scapy installed (real packet capture)
- ✅ 19 network interfaces detected
- ✅ IP filtering configured
- ✅ Frontend ready
- ⚠️ Need sudo for real capture

**Run this now:**
```bash
sudo python3 backend/app.py
```

Then open: http://localhost:8080

Good luck with your presentation! 🚀
