# Wireshark Real Packet Capture Setup Guide

This guide will help you set up REAL packet capture from your network interface.

## 🎯 Capture Methods

The application supports **3 methods** for packet capture (in order of preference):

1. **tshark** (Wireshark CLI) - Most reliable
2. **scapy** (Python library) - Good alternative
3. **Simulation** - Fallback if above methods fail

## 📋 Prerequisites

### Method 1: Using tshark (Recommended)

**macOS:**
```bash
# Install Wireshark (includes tshark)
brew install wireshark

# Or download from: https://www.wireshark.org/download.html
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tshark

# Allow non-root users to capture packets
sudo dpkg-reconfigure wireshark-common
# Select "Yes" when asked
sudo usermod -a -G wireshark $USER
# Log out and log back in
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install wireshark-cli
```

### Method 2: Using scapy (Already Installed)

Scapy is already installed via requirements.txt:
```bash
pip3 install scapy
```

## 🔐 Permissions Setup

### macOS Permissions

**Option A: Run with sudo (Quick but not recommended for production)**
```bash
sudo python3 backend/app.py
```

**Option B: Grant capture permissions to Python (Recommended)**
```bash
# Find your Python path
which python3

# Grant capture permissions
sudo chmod +x /Library/Frameworks/Python.framework/Versions/3.12/bin/python3
```

### Linux Permissions

**For tshark:**
```bash
# Add your user to wireshark group
sudo usermod -a -G wireshark $USER

# Set capabilities for tshark
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tshark

# Log out and log back in for changes to take effect
```

**For scapy:**
```bash
# Run with sudo or set capabilities
sudo python3 backend/app.py

# OR set capabilities for Python
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
```

## 🚀 Running with Real Capture

### Step 1: Check Available Network Interfaces

```bash
# macOS/Linux
ifconfig

# Or
ip addr show
```

Common interfaces:
- **macOS**: `en0` (Wi-Fi), `en1` (Ethernet)
- **Linux**: `eth0` (Ethernet), `wlan0` (Wi-Fi)
- **Windows**: `Wi-Fi`, `Ethernet`

### Step 2: Start Backend with Permissions

**macOS:**
```bash
sudo python3 backend/app.py
```

**Linux:**
```bash
sudo python3 backend/app.py
```

### Step 3: Start Frontend
```bash
cd frontend
python3 -m http.server 8080
```

### Step 4: Test Capture

1. Open http://localhost:8080
2. Connect to VPN
3. Click "Start Capture"
4. Open another browser tab and visit websites
5. Watch REAL packets appear!

## 🧪 Testing Real Capture

### Generate Network Traffic

**Terminal commands to generate traffic:**

```bash
# HTTP traffic
curl http://example.com

# HTTPS traffic
curl https://www.google.com

# DNS queries
nslookup google.com

# Ping (ICMP)
ping -c 5 8.8.8.8

# Multiple requests
for i in {1..10}; do curl -s http://example.com > /dev/null; done
```

**Browser actions:**
- Visit websites (HTTP/HTTPS traffic)
- Watch YouTube videos (TCP/UDP traffic)
- Use social media (various protocols)
- Download files (TCP traffic)

## 🔍 Verification

### Check if tshark is working:
```bash
tshark -v
```

### Check if scapy is working:
```bash
python3 -c "from scapy.all import sniff; print('Scapy OK')"
```

### Test packet capture manually:
```bash
# Using tshark (requires sudo)
sudo tshark -i en0 -c 10

# Using scapy
sudo python3 -c "from scapy.all import sniff; sniff(count=10)"
```

## 📊 What You'll See

When real capture is working, you'll see:
- **Real source/destination IPs** from your network
- **Actual protocols** being used (TCP, UDP, HTTP, HTTPS, DNS, ICMP)
- **Real packet sizes** (not random)
- **Actual timestamps** of packet capture
- **Your real traffic** to websites and services

## 🐛 Troubleshooting

### "tshark not found"
```bash
# Install Wireshark/tshark
brew install wireshark  # macOS
sudo apt-get install tshark  # Linux
```

### "Permission denied"
```bash
# Run with sudo
sudo python3 backend/app.py
```

### "No suitable device found"
```bash
# Check available interfaces
ifconfig

# Specify interface in the UI or code
```

### "Scapy import error"
```bash
# Install scapy
pip3 install scapy
```

### Capture shows "simulated" packets
This means both tshark and scapy failed. Check:
1. Is tshark installed? (`tshark -v`)
2. Is scapy installed? (`pip3 list | grep scapy`)
3. Are you running with sudo?
4. Is the interface name correct?

## 🎓 For Your Project Demo

### Demo Script:

1. **Show the setup:**
   ```bash
   # Terminal 1
   sudo python3 backend/app.py
   
   # Terminal 2
   cd frontend && python3 -m http.server 8080
   ```

2. **Explain the capture methods:**
   - "We're using tshark/scapy to capture real network packets"
   - "This is the same technology Wireshark uses"

3. **Start capture and generate traffic:**
   - Connect to VPN
   - Start packet capture
   - Open new tab: visit google.com, youtube.com
   - Run: `curl http://example.com`
   - Show real packets appearing

4. **Explain what you see:**
   - "These are REAL packets from my network interface"
   - "You can see actual source/destination IPs"
   - "Protocol distribution shows real traffic patterns"
   - "HTTP/HTTPS traffic from browser requests"
   - "DNS queries for domain resolution"

5. **Show IP filtering:**
   - "Only whitelisted IPs can connect"
   - "Blocked IPs are denied access"
   - Demonstrate with different IPs

## 🔒 Security Notes

- **Never run untrusted code with sudo**
- Packet capture can see sensitive data on your network
- Only capture on networks you own/control
- This is for educational purposes only
- Be aware of privacy and legal implications

## 📝 Alternative: Capture to File

If live capture doesn't work, you can capture to a file first:

```bash
# Capture packets to file
sudo tshark -i en0 -w capture.pcap -c 100

# Then read from file in your code
tshark -r capture.pcap -T fields -e frame.time -e ip.src -e ip.dst
```

## ✅ Success Indicators

You'll know real capture is working when:
- ✅ Console shows: "Starting packet capture on interface: en0"
- ✅ Packets show real IPs (not random)
- ✅ Protocols match your actual traffic
- ✅ Packet info doesn't say "(simulated)"
- ✅ Traffic increases when you browse websites

## 🎉 Ready to Demo!

Once you see real packets flowing, you're ready to present to your project guide!

---

**Need help?** Check the backend console for error messages and capture method being used.
