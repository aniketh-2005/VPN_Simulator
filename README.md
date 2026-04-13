# 🔐 VPN Simulator with Real Packet Capture & AES-256 Encryption

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-stack VPN simulator with **real network packet capture**, **AES-256-GCM encryption**, and **real-time traffic monitoring**. Built with Python Flask backend and vanilla JavaScript frontend.

## ✨ Features

### 🔒 Security
- **AES-256-GCM Encryption**: Military-grade encryption for all captured packets
- **PBKDF2 Key Derivation**: 100,000 iterations with random salt per session
- **Unique Nonces**: Every packet encrypted with unique random nonce
- **Session Management**: Automatic key generation and rotation
- **IP Filtering**: Whitelist/blacklist support for access control

### 📡 Network Monitoring
- **Real Packet Capture**: Captures actual network traffic using Wireshark/tshark or Scapy
- **Protocol Analysis**: TCP, UDP, HTTP, HTTPS, DNS, ICMP detection
- **Real-time Statistics**: Live traffic monitoring via WebSocket
- **Visual Indicators**: 🔒 badges on encrypted packets

### 🌍 VPN Features
- **6 Global Servers**: US East/West, UK, Germany, Japan, Australia
- **IP Masking**: Simulates VPN IP assignment
- **Connection Stats**: Upload/download speed, ping, latency
- **Kill Switch**: Simulated security features
- **DNS Leak Protection**: Visual indicators

### 🎨 User Interface
- **Modern Dashboard**: Clean, professional design
- **Real-time Updates**: WebSocket-powered live data
- **Protocol Charts**: Visual distribution of traffic types
- **Packet List**: Recent packets with encryption status

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Wireshark with tshark (optional, for real packet capture)
- sudo/root access (required for packet capture)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/vpn-simulator.git
cd vpn-simulator
```

2. **Install Python dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Install Wireshark** (optional, for real packet capture)
```bash
# macOS
brew install wireshark

# Ubuntu/Debian
sudo apt-get install wireshark tshark
```

### Running the Application

1. **Start the backend** (requires sudo for packet capture)
```bash
sudo python3 backend/app.py
# or use the helper script
./run_backend.sh
```

2. **Open the frontend**
```bash
open frontend/index.html
# or navigate to http://localhost:8080 in your browser
```

3. **Use the application**
   - Select a VPN server location
   - Click "Connect" to establish VPN connection
   - Click "Start Capture" to begin capturing packets
   - Generate traffic to see packets being captured and encrypted

### Generating Test Traffic

```bash
# Use the traffic generator
./generate_traffic.sh

# Or manually generate traffic
ping 8.8.8.8
curl http://example.com
```

## 📁 Project Structure

```
vpn-simulator/
├── backend/
│   └── app.py              # Flask backend with packet capture & encryption
├── frontend/
│   ├── index.html          # Main UI
│   ├── app.js              # Frontend logic & WebSocket handling
│   └── style.css           # Modern styling
├── requirements.txt        # Python dependencies
├── run_backend.sh          # Backend startup script
├── generate_traffic.sh     # Traffic generator (bash)
├── generate_traffic.py     # Traffic generator (python)
├── test_capture.py         # Packet capture test script
├── QUICK_START.md          # Quick start guide
├── WIRESHARK_SETUP.md      # Wireshark installation guide
├── AES_ENCRYPTION.md       # Encryption implementation details
├── DATA_FLOW.md            # System architecture & data flow
├── TRAFFIC_GENERATOR.md    # Traffic generation guide
└── README.md               # This file
```

## 🔧 Technology Stack

### Backend
- **Flask**: Web framework
- **Flask-SocketIO**: Real-time WebSocket communication
- **Scapy**: Packet capture and analysis
- **Cryptography**: AES-256-GCM encryption

### Frontend
- **Vanilla JavaScript**: No frameworks, pure JS
- **Socket.IO Client**: WebSocket communication
- **CSS3**: Modern styling with animations

## 📊 Architecture

```
┌─────────────┐         WebSocket          ┌─────────────┐
│   Browser   │ ◄─────────────────────────► │   Flask     │
│  (Frontend) │    Real-time Updates        │  (Backend)  │
└─────────────┘                             └──────┬──────┘
                                                   │
                                                   │ Captures
                                                   ▼
                                            ┌─────────────┐
                                            │  Network    │
                                            │  Interface  │
                                            │  (en0/eth0) │
                                            └─────────────┘
```

## 🔐 Encryption Details

- **Algorithm**: AES-256-GCM
- **Key Size**: 256 bits (32 bytes)
- **Mode**: GCM (Galois/Counter Mode)
- **Nonce**: 96 bits (12 bytes, random per packet)
- **Tag**: 128 bits (16 bytes, authentication)
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Salt**: 128 bits (16 bytes, random per session)

See [AES_ENCRYPTION.md](AES_ENCRYPTION.md) for detailed implementation.

## 📖 Documentation

- [📘 Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- [🔧 Wireshark Setup](WIRESHARK_SETUP.md) - Install and configure Wireshark
- [🔐 AES Encryption](AES_ENCRYPTION.md) - Encryption implementation details
- [📊 Data Flow](DATA_FLOW.md) - System architecture and data flow
- [🚦 Traffic Generator](TRAFFIC_GENERATOR.md) - Generate test traffic

## 🎯 Use Cases

- **Educational**: Learn about VPNs, encryption, and packet capture
- **Network Analysis**: Monitor and analyze network traffic
- **Security Research**: Study packet encryption and protocol analysis
- **Demo/Presentation**: Showcase VPN technology and encryption

## ⚠️ Important Notes

- **Requires sudo/root**: Packet capture needs elevated privileges
- **Educational Purpose**: This is a simulator for learning, not production VPN
- **Network Interface**: Automatically detects best interface (en0, eth0, wlan0)
- **Real Capture**: Uses tshark or scapy for actual packet capture

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with Flask and Socket.IO
- Encryption powered by Python Cryptography library
- Packet capture using Scapy and Wireshark

---

**⭐ Star this repo if you find it useful!**
