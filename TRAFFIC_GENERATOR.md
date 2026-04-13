# Continuous Traffic Generator

## 🚀 Quick Start

### Option 1: Bash Script (Recommended)
```bash
./generate_traffic.sh
```

### Option 2: Python Script
```bash
python3 generate_traffic.py
```

### Option 3: Simple Continuous Ping
```bash
ping 8.8.8.8
```

## 📊 What It Does

The traffic generator creates continuous network traffic including:

- **ICMP**: Ping packets to multiple servers
- **DNS**: Domain name lookups
- **HTTP**: Web page requests
- **HTTPS**: Secure web connections
- **TCP/UDP**: Various protocol packets

## 🎯 For Your Demo

### Step 1: Start Backend
```bash
sudo python3 backend/app.py
```

### Step 2: Start Frontend
```bash
cd frontend
python3 -m http.server 8080
```

### Step 3: Connect to VPN
1. Open http://localhost:8080
2. Select a server
3. Click "Connect"
4. Verify "Encryption Status: Active"

### Step 4: Start Packet Capture
1. Click "Start Capture"
2. Watch for packets (may be simulated if not running with sudo)

### Step 5: Generate Traffic
```bash
# In a new terminal
./generate_traffic.sh
```

### Step 6: Watch the Magic! ✨
- Packets appear in real-time
- Each packet shows 🔒 badge
- Encrypted counter increases
- Protocol distribution updates
- Traffic stats update live

## 🎮 Traffic Generation Options

### Continuous Ping (Simple)
```bash
# Ping forever
ping 8.8.8.8

# Ping with interval
ping -i 0.5 8.8.8.8  # Every 0.5 seconds
```

### Multiple Pings (Parallel)
```bash
# Ping multiple servers simultaneously
ping 8.8.8.8 & ping 1.1.1.1 & ping 208.67.222.222
```

### Continuous Web Requests
```bash
# Infinite loop of web requests
while true; do
    curl -s http://example.com > /dev/null
    curl -s https://www.google.com > /dev/null
    sleep 2
done
```

### DNS Lookups
```bash
# Continuous DNS queries
while true; do
    nslookup google.com > /dev/null
    nslookup github.com > /dev/null
    sleep 1
done
```

### Mixed Traffic (Best for Demo)
```bash
# Use the provided script
./generate_traffic.sh
```

## 🛑 How to Stop

Press `Ctrl+C` in the terminal running the traffic generator.

## ⚙️ Customization

### Adjust Traffic Frequency

Edit `generate_traffic.sh` or `generate_traffic.py`:

```bash
# Change this line to adjust frequency
sleep 3  # Wait 3 seconds between bursts

# Options:
sleep 1   # More traffic (every 1 second)
sleep 5   # Less traffic (every 5 seconds)
sleep 0.5 # Very frequent (every 0.5 seconds)
```

### Add More Traffic Types

Add to the script:

```bash
# FTP
curl -s ftp://ftp.example.com

# SSH (will fail but generates packets)
ssh -o ConnectTimeout=1 example.com

# Custom ports
nc -zv example.com 80
```

## 📊 Expected Results

When running with **sudo** (real capture):
- ✅ Real packets from your network
- ✅ Actual source/destination IPs
- ✅ Real protocols (TCP, UDP, ICMP, DNS, HTTP, HTTPS)
- ✅ Encrypted with AES-256-GCM
- ✅ 🔒 badges on all packets

When running **without sudo** (simulated):
- ⚠️ Simulated packets
- ⚠️ Random IPs
- ⚠️ Still shows encryption
- ⚠️ Still demonstrates the system

## 🎓 For Your Project Guide

**Demo Script:**

1. "First, I'll connect to the VPN"
   - Show connection
   - Point out "Encryption Status: Active"
   - Show Session ID

2. "Now I'll start packet capture"
   - Click "Start Capture"
   - Explain it's using Scapy/Wireshark

3. "Let me generate some network traffic"
   - Run: `./generate_traffic.sh`
   - Show terminal output

4. "Watch the packets appear in real-time"
   - Point to packet list
   - Show 🔒 encrypted badges
   - Show encrypted counter increasing

5. "Each packet is encrypted with AES-256-GCM"
   - Point to encryption status
   - Show protocol distribution
   - Explain the security

6. "The system captures real network traffic"
   - Show different protocols
   - Explain TCP, UDP, HTTP, HTTPS, DNS, ICMP
   - Show real-time statistics

## 🔧 Troubleshooting

### No Packets Appearing?

**Check 1: VPN Connected?**
```
Status should show "Connected"
Encryption Status should show "Active"
```

**Check 2: Capture Started?**
```
Click "Start Capture" button
Status should show "Capturing..."
```

**Check 3: Traffic Generator Running?**
```
Terminal should show traffic generation messages
```

**Check 4: Running with sudo?**
```
For real capture: sudo python3 backend/app.py
For simulation: python3 backend/app.py (works without sudo)
```

### Packets Show "(simulated)"?

This means real capture failed. Either:
- Run backend with sudo: `sudo python3 backend/app.py`
- Or accept simulated mode (still demonstrates encryption)

### Too Much/Too Little Traffic?

Adjust the `sleep` value in the script:
- More traffic: `sleep 1`
- Less traffic: `sleep 5`

## 📝 Quick Commands Reference

```bash
# Start traffic generator
./generate_traffic.sh

# Simple continuous ping
ping 8.8.8.8

# Ping with custom interval
ping -i 0.5 8.8.8.8

# Multiple pings
ping 8.8.8.8 & ping 1.1.1.1

# Continuous web requests
while true; do curl -s http://example.com > /dev/null; sleep 2; done

# Stop any running traffic
# Press Ctrl+C in the terminal
```

## 🎉 Result

You'll see:
- ✅ Continuous packet flow
- ✅ Real-time encryption
- ✅ 🔒 badges on packets
- ✅ Encrypted counter increasing
- ✅ Protocol distribution updating
- ✅ Traffic statistics changing
- ✅ Professional demo!

---

**Perfect for impressing your project guide!** 🚀🔐
