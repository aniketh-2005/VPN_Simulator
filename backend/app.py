from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import random
import time
import threading
from datetime import datetime
import subprocess
import re
from collections import defaultdict
import os
import signal
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import secrets

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# VPN Server locations
VPN_SERVERS = {
    'us-east': {'name': 'US East', 'location': 'New York', 'lat': 40.7128, 'lon': -74.0060, 'load': 0},
    'us-west': {'name': 'US West', 'location': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437, 'load': 0},
    'uk': {'name': 'United Kingdom', 'location': 'London', 'lat': 51.5074, 'lon': -0.1278, 'load': 0},
    'germany': {'name': 'Germany', 'location': 'Frankfurt', 'lat': 50.1109, 'lon': 8.6821, 'load': 0},
    'japan': {'name': 'Japan', 'location': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503, 'load': 0},
    'australia': {'name': 'Australia', 'location': 'Sydney', 'lat': -33.8688, 'lon': 151.2093, 'load': 0}
}

# Allowed IP addresses (whitelist) - only these can connect through VPN
ALLOWED_IPS = [
    '192.168.1.100',
    '192.168.1.101',
    '192.168.1.105',
    '10.0.0.50',
    '172.16.0.25'
]

# Blocked IP addresses (blacklist) - these are denied
BLOCKED_IPS = [
    '192.168.1.200',
    '10.0.0.99',
    '172.16.0.100'
]

# Connection state
connection_state = {
    'connected': False,
    'server': None,
    'ip_address': None,
    'original_ip': '192.168.1.100',
    'connection_time': None,
    'data_sent': 0,
    'data_received': 0,
    'ping': 0,
    'download_speed': 0,
    'upload_speed': 0,
    'packets_sent': 0,
    'packets_received': 0,
    'encryption': 'AES-256-GCM',
    'protocol': 'OpenVPN',
    'wireshark_capture': False,
    'encryption_key': None,
    'session_id': None,
    'encrypted_packets': 0,
    'decrypted_packets': 0
}

# Wireshark capture data
wireshark_data = {
    'packets': [],
    'protocols': defaultdict(int),
    'total_packets': 0,
    'capture_active': False,
    'capture_process': None,
    'interface': None
}

def check_ip_allowed(ip_address):
    """Check if IP is allowed to connect"""
    if ip_address in BLOCKED_IPS:
        return False, "IP address is blocked"
    if ip_address not in ALLOWED_IPS:
        return False, "IP address not in whitelist"
    return True, "IP allowed"

def generate_encryption_key():
    """Generate AES-256 encryption key using PBKDF2"""
    # Generate random salt
    salt = secrets.token_bytes(16)
    
    # Generate session password
    password = secrets.token_urlsafe(32).encode()
    
    # Derive 256-bit key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password)
    
    return key, salt, password

def encrypt_packet_data(data, key):
    """Encrypt packet data using AES-256-GCM"""
    try:
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Generate random nonce (96 bits for GCM)
        nonce = secrets.token_bytes(12)
        
        # Convert data to JSON string then bytes
        import json
        data_bytes = json.dumps(data).encode('utf-8')
        
        # Encrypt
        ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
        
        # Return nonce + ciphertext (both base64 encoded)
        return {
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'encrypted': True
        }
    except Exception as e:
        print(f"Encryption error: {e}")
        return data

def decrypt_packet_data(encrypted_data, key):
    """Decrypt packet data using AES-256-GCM"""
    try:
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Decode base64
        nonce = base64.b64decode(encrypted_data['nonce'])
        ciphertext = base64.b64decode(encrypted_data['ciphertext'])
        
        # Decrypt
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        # Convert back to dict
        import json
        return json.loads(plaintext.decode('utf-8'))
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

def generate_vpn_ip(server_id):
    """Generate a fake VPN IP based on server location"""
    ip_ranges = {
        'us-east': '10.1',
        'us-west': '10.2',
        'uk': '10.3',
        'germany': '10.4',
        'japan': '10.5',
        'australia': '10.6'
    }
    base = ip_ranges.get(server_id, '10.0')
    return f"{base}.{random.randint(1, 255)}.{random.randint(1, 255)}"

def get_network_interfaces():
    """Get available network interfaces (prioritize real interfaces)"""
    try:
        # Try using ifconfig (macOS/Linux)
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        interfaces = []
        
        # List of virtual/loopback interfaces to skip
        skip_interfaces = ['lo', 'lo0', 'gif', 'stf', 'bridge', 'utun', 'awdl', 'llw', 'anpi']
        
        for line in result.stdout.split('\n'):
            if line and not line.startswith('\t') and not line.startswith(' '):
                interface = line.split(':')[0]
                
                # Skip virtual/loopback interfaces
                should_skip = False
                for skip in skip_interfaces:
                    if interface.startswith(skip):
                        should_skip = True
                        break
                
                if not should_skip and interface:
                    interfaces.append(interface)
        
        # Prioritize common real interfaces
        priority_interfaces = ['en0', 'eth0', 'wlan0', 'en1', 'en2']
        for priority in priority_interfaces:
            if priority in interfaces:
                # Move to front
                interfaces.remove(priority)
                interfaces.insert(0, priority)
        
        return interfaces if interfaces else ['en0']
    except:
        # Fallback to common interface names
        return ['en0', 'eth0', 'wlan0', 'Wi-Fi']

def capture_with_tshark(interface):
    """Capture real network traffic using tshark (Wireshark CLI)"""
    try:
        # tshark command to capture packets
        # -i: interface, -T: output format, -e: fields to extract
        cmd = [
            'tshark',
            '-i', interface,
            '-T', 'fields',
            '-e', 'frame.time',
            '-e', 'ip.proto',
            '-e', 'ip.src',
            '-e', 'ip.dst',
            '-e', 'frame.len',
            '-e', 'tcp.port',
            '-e', 'udp.port',
            '-e', '_ws.col.Protocol',
            '-E', 'separator=|'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        wireshark_data['capture_process'] = process
        
        protocol_map = {
            '6': 'TCP',
            '17': 'UDP',
            '1': 'ICMP',
            '2': 'IGMP'
        }
        
        for line in process.stdout:
            if not wireshark_data['capture_active']:
                break
                
            try:
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    timestamp = parts[0] if parts[0] else datetime.now().isoformat()
                    proto_num = parts[1]
                    src_ip = parts[2] if parts[2] else 'N/A'
                    dst_ip = parts[3] if parts[3] else 'N/A'
                    length = parts[4] if parts[4] else '0'
                    protocol = parts[7] if len(parts) > 7 and parts[7] else protocol_map.get(proto_num, 'OTHER')
                    
                    packet = {
                        'timestamp': timestamp,
                        'protocol': protocol,
                        'src_ip': src_ip,
                        'dst_ip': dst_ip,
                        'length': int(length) if length.isdigit() else 0,
                        'info': f'{protocol} packet'
                    }
                    
                    # Encrypt packet data if VPN is connected
                    if connection_state['connected'] and connection_state['encryption_key']:
                        encrypted_packet = encrypt_packet_data(packet, connection_state['encryption_key'])
                        connection_state['encrypted_packets'] += 1
                        
                        # Debug logging
                        if connection_state['encrypted_packets'] <= 5 or connection_state['encrypted_packets'] % 10 == 0:
                            print(f"🔒 Encrypted packet #{connection_state['encrypted_packets']} (tshark)")
                        
                        # Store encrypted version
                        wireshark_data['packets'].append({
                            'encrypted': True,
                            'data': encrypted_packet,
                            'original': packet
                        })
                    else:
                        wireshark_data['packets'].append(packet)
                    
                    wireshark_data['protocols'][protocol] += 1
                    wireshark_data['total_packets'] += 1
                    
                    # Keep only last 100 packets
                    if len(wireshark_data['packets']) > 100:
                        wireshark_data['packets'].pop(0)
                    
                    # Emit packet data (with encryption info)
                    socketio.emit('packet_captured', {
                        'packet': packet,
                        'encrypted': connection_state['connected'],
                        'encryption_method': 'AES-256-GCM' if connection_state['connected'] else None,
                        'total_packets': wireshark_data['total_packets'],
                        'encrypted_packets': connection_state['encrypted_packets'],
                        'protocols': dict(wireshark_data['protocols'])
                    })
            except Exception as e:
                print(f"Error parsing packet: {e}")
                continue
                
    except FileNotFoundError:
        print("tshark not found. Please install Wireshark with command-line tools.")
        return False
    except Exception as e:
        print(f"Capture error: {e}")
        return False
    
    return True

def capture_with_scapy(interface):
    """Capture real network traffic using scapy"""
    try:
        from scapy.all import sniff, IP, TCP, UDP, ICMP
        
        print(f"✓ Scapy imported successfully")
        print(f"✓ Starting sniff on interface: {interface}")
        print(f"✓ Waiting for packets... (generate traffic with: ping 8.8.8.8)")
        
        packet_count = 0
        
        def packet_callback(packet):
            nonlocal packet_count
            
            if not wireshark_data['capture_active']:
                return True  # Stop sniffing
            
            try:
                if IP in packet:
                    packet_count += 1
                    
                    protocol = 'OTHER'
                    if TCP in packet:
                        protocol = 'TCP'
                    elif UDP in packet:
                        protocol = 'UDP'
                    elif ICMP in packet:
                        protocol = 'ICMP'
                    
                    # Check for HTTP/HTTPS
                    if TCP in packet:
                        if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                            protocol = 'HTTP'
                        elif packet[TCP].dport == 443 or packet[TCP].sport == 443:
                            protocol = 'HTTPS'
                        elif packet[TCP].dport == 53 or packet[TCP].sport == 53:
                            protocol = 'DNS'
                    
                    packet_data = {
                        'timestamp': datetime.now().isoformat(),
                        'protocol': protocol,
                        'src_ip': packet[IP].src,
                        'dst_ip': packet[IP].dst,
                        'length': len(packet),
                        'info': f'{protocol} packet'
                    }
                    
                    # Print to console for verification
                    if packet_count <= 5 or packet_count % 10 == 0:
                        print(f"📦 Packet #{packet_count}: {protocol} {packet[IP].src} → {packet[IP].dst}")
                    
                    # Encrypt packet data if VPN is connected
                    if connection_state['connected'] and connection_state['encryption_key']:
                        encrypted_packet = encrypt_packet_data(packet_data, connection_state['encryption_key'])
                        connection_state['encrypted_packets'] += 1
                        
                        # Debug logging
                        if connection_state['encrypted_packets'] <= 5 or connection_state['encrypted_packets'] % 10 == 0:
                            print(f"🔒 Encrypted packet #{connection_state['encrypted_packets']}")
                        
                        # Store encrypted version
                        wireshark_data['packets'].append({
                            'encrypted': True,
                            'data': encrypted_packet,
                            'original': packet_data  # Keep for display
                        })
                    else:
                        # Debug: why not encrypting?
                        if packet_count <= 3:
                            print(f"⚠️ NOT encrypting: connected={connection_state['connected']}, has_key={connection_state['encryption_key'] is not None}")
                        wireshark_data['packets'].append(packet_data)
                    
                    wireshark_data['protocols'][protocol] += 1
                    wireshark_data['total_packets'] += 1
                    
                    # Keep only last 100 packets
                    if len(wireshark_data['packets']) > 100:
                        wireshark_data['packets'].pop(0)
                    
                    # Emit packet data (with encryption info)
                    emit_data = {
                        'packet': packet_data,
                        'encrypted': connection_state['connected'],
                        'encryption_method': 'AES-256-GCM' if connection_state['connected'] else None,
                        'total_packets': wireshark_data['total_packets'],
                        'encrypted_packets': connection_state['encrypted_packets'],
                        'protocols': dict(wireshark_data['protocols'])
                    }
                    
                    # Debug: log what we're emitting
                    if packet_count <= 3 or packet_count % 20 == 0:
                        print(f"📡 Emitting: total={emit_data['total_packets']}, encrypted={emit_data['encrypted_packets']}, is_encrypted={emit_data['encrypted']}")
                    
                    socketio.emit('packet_captured', emit_data)
            except Exception as e:
                print(f"Error processing packet: {e}")
        
        # Start sniffing
        print(f"🎯 Scapy capture active on {interface}")
        sniff(iface=interface, prn=packet_callback, store=False, 
              stop_filter=lambda x: not wireshark_data['capture_active'])
        
        return True
        
    except ImportError:
        print("❌ Scapy not installed. Install with: pip3 install scapy")
        return False
    except PermissionError as e:
        print(f"❌ Permission denied: {e}")
        print("   Make sure you're running with sudo!")
        return False
    except Exception as e:
        print(f"❌ Scapy capture error: {e}")
        return False

def capture_network_traffic():
    """Capture real network traffic using available method"""
    interface = wireshark_data['interface']
    
    print(f"\n{'='*70}")
    print(f"🔍 STARTING PACKET CAPTURE")
    print(f"{'='*70}")
    print(f"Interface: {interface}")
    print(f"Running as: {'root/sudo' if os.geteuid() == 0 else 'normal user'}")
    print(f"{'='*70}\n")
    
    # Try tshark first (more reliable)
    print("Attempting Method 1: tshark (Wireshark CLI)...")
    success = capture_with_tshark(interface)
    
    if success:
        print("✅ Using tshark for packet capture")
        return
    
    # If tshark fails, try scapy
    print("\nAttempting Method 2: scapy (Python library)...")
    success = capture_with_scapy(interface)
    
    if success:
        print("✅ Using scapy for packet capture")
        return
    
    # If both fail, show error and DO NOT use simulation
    print("\n" + "="*70)
    print("❌ REAL PACKET CAPTURE FAILED")
    print("="*70)
    print("Both tshark and scapy failed to capture packets.")
    print("\nPossible reasons:")
    print("  1. Not running with sudo (required for packet capture)")
    print("  2. Interface has no traffic")
    print("  3. Permissions issue with /dev/bpf*")
    print("\nTo fix:")
    print("  • Make sure you're running: sudo python3 backend/app.py")
    print("  • Try a different interface (en0 instead of en2)")
    print("  • Generate traffic: ping 8.8.8.8")
    print("="*70 + "\n")
    
    # DO NOT fall back to simulation
    wireshark_data['capture_active'] = False
    
    socketio.emit('capture_error', {
        'error': 'Real packet capture failed',
        'message': 'Both tshark and scapy failed. Check backend console for details.'
    })

def capture_simulated_traffic():
    """Fallback: Simulate packet capture if real capture fails"""
    try:
        while wireshark_data['capture_active']:
            protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'DNS', 'ICMP']
            protocol = random.choice(protocols)
            
            packet = {
                'timestamp': datetime.now().isoformat(),
                'protocol': protocol,
                'src_ip': connection_state['original_ip'],
                'dst_ip': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'length': random.randint(64, 1500),
                'info': f'{protocol} packet (simulated)'
            }
            
            # Encrypt if VPN connected
            if connection_state['connected'] and connection_state['encryption_key']:
                encrypted_packet = encrypt_packet_data(packet, connection_state['encryption_key'])
                connection_state['encrypted_packets'] += 1
                
                wireshark_data['packets'].append({
                    'encrypted': True,
                    'data': encrypted_packet,
                    'original': packet
                })
            else:
                wireshark_data['packets'].append(packet)
            
            wireshark_data['protocols'][protocol] += 1
            wireshark_data['total_packets'] += 1
            
            if len(wireshark_data['packets']) > 100:
                wireshark_data['packets'].pop(0)
            
            socketio.emit('packet_captured', {
                'packet': packet,
                'encrypted': connection_state['connected'],
                'encryption_method': 'AES-256-GCM' if connection_state['connected'] else None,
                'total_packets': wireshark_data['total_packets'],
                'encrypted_packets': connection_state['encrypted_packets'],
                'protocols': dict(wireshark_data['protocols'])
            })
            
            time.sleep(random.uniform(0.1, 0.5))
    except Exception as e:
        print(f"Simulation error: {e}")

def simulate_traffic():
    """Simulate network traffic while connected"""
    while connection_state['connected']:
        # Update data transfer
        data_sent_increment = random.randint(100, 5000)
        data_received_increment = random.randint(500, 10000)
        connection_state['data_sent'] += data_sent_increment
        connection_state['data_received'] += data_received_increment
        
        # Update packets
        connection_state['packets_sent'] += random.randint(10, 50)
        connection_state['packets_received'] += random.randint(20, 80)
        
        # Update speeds (in KB/s)
        connection_state['upload_speed'] = data_sent_increment / 1024
        connection_state['download_speed'] = data_received_increment / 1024
        
        # Update ping (ms) - varies based on server location
        base_ping = {
            'us-east': 25,
            'us-west': 45,
            'uk': 85,
            'germany': 95,
            'japan': 150,
            'australia': 180
        }
        server_id = connection_state['server']
        connection_state['ping'] = base_ping.get(server_id, 50) + random.randint(-10, 20)
        
        # Update server load
        if connection_state['server']:
            VPN_SERVERS[connection_state['server']]['load'] = random.randint(20, 80)
        
        socketio.emit('traffic_update', {
            'data_sent': connection_state['data_sent'],
            'data_received': connection_state['data_received'],
            'upload_speed': round(connection_state['upload_speed'], 2),
            'download_speed': round(connection_state['download_speed'], 2),
            'ping': connection_state['ping'],
            'packets_sent': connection_state['packets_sent'],
            'packets_received': connection_state['packets_received'],
            'timestamp': datetime.now().isoformat()
        })
        
        time.sleep(1)

@app.route('/api/servers', methods=['GET'])
def get_servers():
    """Get list of available VPN servers"""
    servers = []
    for server_id, info in VPN_SERVERS.items():
        servers.append({
            'id': server_id,
            'name': info['name'],
            'location': info['location'],
            'lat': info['lat'],
            'lon': info['lon'],
            'load': random.randint(10, 90)
        })
    return jsonify(servers)

@app.route('/api/connect', methods=['POST'])
def connect():
    """Connect to a VPN server"""
    data = request.json
    server_id = data.get('server_id')
    user_ip = data.get('user_ip', connection_state['original_ip'])
    
    if server_id not in VPN_SERVERS:
        return jsonify({'error': 'Invalid server'}), 400
    
    # Check if IP is allowed
    allowed, message = check_ip_allowed(user_ip)
    if not allowed:
        return jsonify({
            'error': message,
            'status': 'blocked',
            'ip_address': user_ip
        }), 403
    
    # Simulate connection delay
    time.sleep(1)
    
    # Generate encryption key for this session
    encryption_key, salt, password = generate_encryption_key()
    session_id = secrets.token_urlsafe(16)
    
    connection_state['connected'] = True
    connection_state['server'] = server_id
    connection_state['original_ip'] = user_ip
    connection_state['ip_address'] = generate_vpn_ip(server_id)
    connection_state['connection_time'] = datetime.now().isoformat()
    connection_state['data_sent'] = 0
    connection_state['data_received'] = 0
    connection_state['packets_sent'] = 0
    connection_state['packets_received'] = 0
    connection_state['ping'] = 0
    connection_state['upload_speed'] = 0
    connection_state['download_speed'] = 0
    connection_state['encryption_key'] = encryption_key
    connection_state['session_id'] = session_id
    connection_state['encrypted_packets'] = 0
    connection_state['decrypted_packets'] = 0
    
    # Start traffic simulation in background
    threading.Thread(target=simulate_traffic, daemon=True).start()
    
    return jsonify({
        'status': 'connected',
        'server': VPN_SERVERS[server_id],
        'ip_address': connection_state['ip_address'],
        'connection_time': connection_state['connection_time'],
        'encryption': connection_state['encryption'],
        'protocol': connection_state['protocol'],
        'session_id': session_id,
        'encryption_enabled': True,
        'key_size': 256,
        'cipher_mode': 'GCM'
    })

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """Disconnect from VPN"""
    connection_state['connected'] = False
    connection_state['server'] = None
    connection_state['ip_address'] = None
    connection_state['connection_time'] = None
    connection_state['encryption_key'] = None
    connection_state['session_id'] = None
    connection_state['encrypted_packets'] = 0
    connection_state['decrypted_packets'] = 0
    
    # Stop packet capture
    wireshark_data['capture_active'] = False
    if wireshark_data['capture_process']:
        try:
            wireshark_data['capture_process'].terminate()
        except:
            pass
        wireshark_data['capture_process'] = None
    
    return jsonify({'status': 'disconnected'})

@app.route('/api/wireshark/start', methods=['POST'])
def start_wireshark():
    """Start Wireshark packet capture"""
    if not connection_state['connected']:
        return jsonify({
            'error': 'Not connected to VPN',
            'message': 'Please connect to a VPN server first before starting packet capture'
        }), 400
    
    data = request.get_json(silent=True) or {}
    interface = data.get('interface')
    
    # Get available interfaces if not specified
    if not interface:
        interfaces = get_network_interfaces()
        if interfaces:
            # Force en0 if available (main Wi-Fi interface)
            if 'en0' in interfaces:
                interface = 'en0'
            else:
                interface = interfaces[0]
        else:
            interface = 'en0'  # Default for macOS
    
    print(f"\n🔍 Capture request received")
    print(f"   Selected interface: {interface}")
    print(f"   Available interfaces: {get_network_interfaces()}")
    print(f"   Running as: {'root/sudo ✓' if os.geteuid() == 0 else 'normal user ✗'}")
    
    wireshark_data['capture_active'] = True
    wireshark_data['packets'] = []
    wireshark_data['protocols'] = defaultdict(int)
    wireshark_data['total_packets'] = 0
    wireshark_data['interface'] = interface
    
    # Start capture in background
    threading.Thread(target=capture_network_traffic, daemon=True).start()
    
    return jsonify({
        'status': 'capturing',
        'message': f'Packet capture started on {interface}',
        'interface': interface,
        'method': 'real',  # Indicates real capture attempt
        'sudo': os.geteuid() == 0
    })

@app.route('/api/wireshark/stop', methods=['POST'])
def stop_wireshark():
    """Stop Wireshark packet capture"""
    wireshark_data['capture_active'] = False
    
    # Kill tshark process if running
    if wireshark_data['capture_process']:
        try:
            wireshark_data['capture_process'].terminate()
            wireshark_data['capture_process'].wait(timeout=2)
        except:
            try:
                wireshark_data['capture_process'].kill()
            except:
                pass
        wireshark_data['capture_process'] = None
    
    return jsonify({
        'status': 'stopped',
        'total_packets': wireshark_data['total_packets'],
        'protocols': dict(wireshark_data['protocols'])
    })

@app.route('/api/wireshark/interfaces', methods=['GET'])
def get_interfaces():
    """Get available network interfaces"""
    interfaces = get_network_interfaces()
    return jsonify({
        'interfaces': interfaces,
        'default': interfaces[0] if interfaces else 'en0'
    })

@app.route('/api/wireshark/packets', methods=['GET'])
def get_packets():
    """Get captured packets"""
    return jsonify({
        'packets': wireshark_data['packets'][-50:],  # Last 50 packets
        'total_packets': wireshark_data['total_packets'],
        'protocols': dict(wireshark_data['protocols']),
        'capture_active': wireshark_data['capture_active']
    })

@app.route('/api/ip-rules', methods=['GET'])
def get_ip_rules():
    """Get IP whitelist and blacklist"""
    return jsonify({
        'allowed_ips': ALLOWED_IPS,
        'blocked_ips': BLOCKED_IPS
    })

@app.route('/api/check-ip', methods=['POST'])
def check_ip():
    """Check if an IP is allowed"""
    data = request.json
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'error': 'IP address required'}), 400
    
    allowed, message = check_ip_allowed(ip)
    
    return jsonify({
        'ip': ip,
        'allowed': allowed,
        'message': message,
        'in_whitelist': ip in ALLOWED_IPS,
        'in_blacklist': ip in BLOCKED_IPS
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current connection status"""
    if connection_state['connected']:
        return jsonify({
            'connected': True,
            'server': VPN_SERVERS[connection_state['server']],
            'ip_address': connection_state['ip_address'],
            'original_ip': connection_state['original_ip'],
            'connection_time': connection_state['connection_time'],
            'data_sent': connection_state['data_sent'],
            'data_received': connection_state['data_received'],
            'ping': connection_state['ping'],
            'upload_speed': connection_state['upload_speed'],
            'download_speed': connection_state['download_speed'],
            'packets_sent': connection_state['packets_sent'],
            'packets_received': connection_state['packets_received'],
            'encryption': connection_state['encryption'],
            'protocol': connection_state['protocol'],
            'session_id': connection_state['session_id'],
            'encrypted_packets': connection_state['encrypted_packets'],
            'encryption_enabled': True
        })
    else:
        return jsonify({
            'connected': False,
            'original_ip': connection_state['original_ip']
        })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
