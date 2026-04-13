const API_URL = 'http://localhost:5001/api';
let socket;
let selectedServer = null;
let currentUserIP = '192.168.1.100'; // Default allowed IP

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadServers();
    checkStatus();
    initializeSocketIO();
    setupEventListeners();
    loadIPRules();
});

function initializeSocketIO() {
    socket = io('http://localhost:5001');
    
    socket.on('connect', () => {
        console.log('Socket.IO connected');
    });
    
    socket.on('traffic_update', (data) => {
        updateTrafficStats(data);
    });
    
    socket.on('packet_captured', (data) => {
        updatePacketCapture(data);
    });
}

function setupEventListeners() {
    document.getElementById('connectBtn').addEventListener('click', connectToVPN);
    document.getElementById('disconnectBtn').addEventListener('click', disconnectFromVPN);
    document.getElementById('serverDropdown').addEventListener('change', (e) => {
        selectedServer = e.target.value;
    });
    document.getElementById('startCaptureBtn').addEventListener('click', startPacketCapture);
    document.getElementById('stopCaptureBtn').addEventListener('click', stopPacketCapture);
    document.getElementById('checkIpBtn').addEventListener('click', checkIPAddress);
    document.getElementById('changeIpBtn').addEventListener('click', changeUserIP);
}

async function loadServers() {
    try {
        const response = await fetch(`${API_URL}/servers`);
        const servers = await response.json();
        
        displayServers(servers);
        populateServerDropdown(servers);
    } catch (error) {
        console.error('Error loading servers:', error);
        document.getElementById('serverList').innerHTML = '<p class="loading">Error loading servers</p>';
    }
}

function displayServers(servers) {
    const serverList = document.getElementById('serverList');
    serverList.innerHTML = '';
    
    servers.forEach(server => {
        const serverItem = document.createElement('div');
        serverItem.className = 'server-item';
        serverItem.innerHTML = `
            <div class="server-header">
                <span class="server-name">${server.name}</span>
                <span class="server-load">Load: ${server.load}%</span>
            </div>
            <div class="server-location">📍 ${server.location}</div>
        `;
        
        serverItem.addEventListener('click', () => {
            selectedServer = server.id;
            document.getElementById('serverDropdown').value = server.id;
            document.querySelectorAll('.server-item').forEach(item => {
                item.classList.remove('active');
            });
            serverItem.classList.add('active');
        });
        
        serverList.appendChild(serverItem);
    });
}

function populateServerDropdown(servers) {
    const dropdown = document.getElementById('serverDropdown');
    dropdown.innerHTML = '<option value="">Choose a server...</option>';
    
    servers.forEach(server => {
        const option = document.createElement('option');
        option.value = server.id;
        option.textContent = `${server.name} - ${server.location}`;
        dropdown.appendChild(option);
    });
}

async function connectToVPN() {
    if (!selectedServer) {
        alert('Please select a server first');
        return;
    }
    
    const connectBtn = document.getElementById('connectBtn');
    connectBtn.disabled = true;
    connectBtn.textContent = 'Connecting...';
    
    try {
        const response = await fetch(`${API_URL}/connect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                server_id: selectedServer,
                user_ip: currentUserIP
            })
        });
        
        const data = await response.json();
        
        if (response.status === 403) {
            alert(`Connection Blocked: ${data.error}`);
            connectBtn.disabled = false;
            connectBtn.textContent = 'Connect';
            return;
        }
        
        if (data.status === 'connected') {
            updateUIConnected(data);
            
            // Show encryption details
            console.log('Encryption enabled:', data.encryption_enabled);
            console.log('Session ID:', data.session_id);
            console.log('Cipher:', data.encryption);
        }
    } catch (error) {
        console.error('Error connecting:', error);
        alert('Failed to connect to VPN');
        connectBtn.disabled = false;
        connectBtn.textContent = 'Connect';
    }
}

async function disconnectFromVPN() {
    try {
        const response = await fetch(`${API_URL}/disconnect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (data.status === 'disconnected') {
            updateUIDisconnected();
        }
    } catch (error) {
        console.error('Error disconnecting:', error);
    }
}

async function checkStatus() {
    try {
        const response = await fetch(`${API_URL}/status`);
        const data = await response.json();
        
        if (data.connected) {
            updateUIConnected(data);
            
            // Update encryption status if available
            if (data.encryption_enabled) {
                document.getElementById('encryptionStatus').textContent = 'Active';
                document.getElementById('encryptionStatus').style.color = '#28a745';
                if (data.session_id) {
                    document.getElementById('sessionId').textContent = data.session_id.substring(0, 16) + '...';
                }
            }
        }
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

function updateUIConnected(data) {
    console.log('updateUIConnected called with data:', data);
    
    // Update status badge
    const statusBadge = document.getElementById('statusBadge');
    statusBadge.classList.add('connected');
    document.getElementById('statusText').textContent = 'Connected';
    
    // Update IP addresses
    document.getElementById('vpnIp').textContent = data.ip_address;
    document.getElementById('vpnIpContainer').style.display = 'flex';
    
    // Update connection info
    document.getElementById('connectedServer').textContent = data.server.name;
    document.getElementById('connectedLocation').textContent = data.server.location;
    document.getElementById('connectionTime').textContent = new Date(data.connection_time).toLocaleTimeString();
    document.getElementById('connectionInfo').style.display = 'block';
    
    // Update security info
    if (data.encryption && data.protocol) {
        document.getElementById('encryption').textContent = data.encryption;
        document.getElementById('protocol').textContent = data.protocol;
        
        console.log('Encryption enabled:', data.encryption_enabled);
        console.log('Session ID:', data.session_id);
        
        // Show encryption details if available
        if (data.encryption_enabled) {
            console.log('Setting encryption status to Active');
            document.getElementById('encryptionStatus').textContent = 'Active';
            document.getElementById('encryptionStatus').style.color = '#28a745';
            if (data.session_id) {
                const shortId = data.session_id.substring(0, 16) + '...';
                console.log('Setting session ID to:', shortId);
                document.getElementById('sessionId').textContent = shortId;
            }
        } else {
            console.log('Encryption not enabled in data');
        }
    } else {
        console.log('No encryption or protocol in data');
    }
    
    // Update buttons
    document.getElementById('connectBtn').style.display = 'none';
    document.getElementById('disconnectBtn').style.display = 'block';
    document.getElementById('serverSelect').style.display = 'none';
    
    // Enable Wireshark controls
    document.getElementById('startCaptureBtn').disabled = false;
}

function updateUIDisconnected() {
    // Update status badge
    const statusBadge = document.getElementById('statusBadge');
    statusBadge.classList.remove('connected');
    document.getElementById('statusText').textContent = 'Disconnected';
    
    // Hide VPN IP
    document.getElementById('vpnIpContainer').style.display = 'none';
    
    // Hide connection info
    document.getElementById('connectionInfo').style.display = 'none';
    
    // Reset encryption status
    document.getElementById('encryptionStatus').textContent = 'Inactive';
    document.getElementById('encryptionStatus').style.color = '#666';
    document.getElementById('sessionId').textContent = '-';
    
    // Update buttons
    document.getElementById('connectBtn').style.display = 'block';
    document.getElementById('connectBtn').disabled = false;
    document.getElementById('connectBtn').textContent = 'Connect';
    document.getElementById('disconnectBtn').style.display = 'none';
    document.getElementById('serverSelect').style.display = 'block';
    
    // Reset traffic stats
    document.getElementById('dataSent').textContent = '0 KB';
    document.getElementById('dataReceived').textContent = '0 KB';
    document.getElementById('uploadSpeed').textContent = '0 KB/s';
    document.getElementById('downloadSpeed').textContent = '0 KB/s';
    document.getElementById('ping').textContent = '0 ms';
    document.getElementById('packetsSent').textContent = '0';
    document.getElementById('packetsReceived').textContent = '0';
    document.getElementById('encryptedPackets').textContent = '0';
    
    // Disable Wireshark controls
    document.getElementById('startCaptureBtn').disabled = true;
    document.getElementById('stopCaptureBtn').disabled = true;
    
    // Clear active server selection
    document.querySelectorAll('.server-item').forEach(item => {
        item.classList.remove('active');
    });
    selectedServer = null;
}

function updateTrafficStats(data) {
    const dataSent = (data.data_sent / 1024).toFixed(2);
    const dataReceived = (data.data_received / 1024).toFixed(2);
    
    document.getElementById('dataSent').textContent = `${dataSent} KB`;
    document.getElementById('dataReceived').textContent = `${dataReceived} KB`;
    document.getElementById('uploadSpeed').textContent = `${data.upload_speed.toFixed(2)} KB/s`;
    document.getElementById('downloadSpeed').textContent = `${data.download_speed.toFixed(2)} KB/s`;
    document.getElementById('ping').textContent = `${data.ping} ms`;
    document.getElementById('packetsSent').textContent = data.packets_sent;
    document.getElementById('packetsReceived').textContent = data.packets_received;
}

// Wireshark Functions
async function startPacketCapture() {
    try {
        const response = await fetch(`${API_URL}/wireshark/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (response.status === 400) {
            alert(data.message || data.error);
            return;
        }
        
        if (data.status === 'capturing') {
            document.getElementById('startCaptureBtn').disabled = true;
            document.getElementById('stopCaptureBtn').disabled = false;
            document.getElementById('captureStatus').textContent = 'Capturing...';
            document.getElementById('captureStatus').style.color = '#28a745';
            
            // Show capture method
            if (data.method === 'real') {
                console.log(`Real capture started on ${data.interface}`);
            }
        }
    } catch (error) {
        console.error('Error starting capture:', error);
        alert('Failed to start capture. Check console for details.');
    }
}

async function stopPacketCapture() {
    try {
        const response = await fetch(`${API_URL}/wireshark/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        document.getElementById('startCaptureBtn').disabled = false;
        document.getElementById('stopCaptureBtn').disabled = true;
        document.getElementById('captureStatus').textContent = 'Stopped';
        document.getElementById('captureStatus').style.color = '#666';
        
        console.log(`Captured ${data.total_packets} packets`);
    } catch (error) {
        console.error('Error stopping capture:', error);
    }
}

function updatePacketCapture(data) {
    const packet = data.packet;
    const packetList = document.getElementById('packetList');
    
    const packetItem = document.createElement('div');
    packetItem.className = 'packet-item';
    
    // Add encryption indicator if encrypted
    const encryptionBadge = data.encrypted ? 
        '<span class="encryption-badge">🔒 Encrypted</span>' : '';
    
    packetItem.innerHTML = `
        <span class="packet-protocol">${packet.protocol}</span>
        <span class="packet-src">${packet.src_ip}</span>
        <span class="packet-arrow">→</span>
        <span class="packet-dst">${packet.dst_ip}</span>
        <span class="packet-length">${packet.length}B</span>
        ${encryptionBadge}
    `;
    
    packetList.insertBefore(packetItem, packetList.firstChild);
    
    // Keep only last 20 packets in UI
    while (packetList.children.length > 20) {
        packetList.removeChild(packetList.lastChild);
    }
    
    // Update total packets
    document.getElementById('totalPackets').textContent = data.total_packets;
    
    // Update encrypted packets counter with debug logging
    if (data.encrypted_packets !== undefined) {
        console.log(`🔒 Updating encrypted counter: ${data.encrypted_packets} (encrypted: ${data.encrypted})`);
        document.getElementById('encryptedPackets').textContent = data.encrypted_packets;
    } else {
        console.log('⚠️ No encrypted_packets in data:', data);
    }
    
    // Update protocol distribution
    updateProtocolChart(data.protocols);
}

function updateProtocolChart(protocols) {
    const chartContainer = document.getElementById('protocolChart');
    chartContainer.innerHTML = '';
    
    const total = Object.values(protocols).reduce((a, b) => a + b, 0);
    
    for (const [protocol, count] of Object.entries(protocols)) {
        const percentage = ((count / total) * 100).toFixed(1);
        const bar = document.createElement('div');
        bar.className = 'protocol-bar';
        bar.innerHTML = `
            <div class="protocol-label">${protocol}</div>
            <div class="protocol-bar-fill" style="width: ${percentage}%"></div>
            <div class="protocol-count">${count} (${percentage}%)</div>
        `;
        chartContainer.appendChild(bar);
    }
}

// IP Filtering Functions
async function loadIPRules() {
    try {
        const response = await fetch(`${API_URL}/ip-rules`);
        const data = await response.json();
        
        displayIPRules(data.allowed_ips, data.blocked_ips);
        document.getElementById('currentIp').textContent = currentUserIP;
    } catch (error) {
        console.error('Error loading IP rules:', error);
    }
}

function displayIPRules(allowed, blocked) {
    const allowedList = document.getElementById('allowedIpList');
    const blockedList = document.getElementById('blockedIpList');
    
    allowedList.innerHTML = allowed.map(ip => 
        `<div class="ip-item allowed">✓ ${ip}</div>`
    ).join('');
    
    blockedList.innerHTML = blocked.map(ip => 
        `<div class="ip-item blocked">✗ ${ip}</div>`
    ).join('');
}

async function checkIPAddress() {
    const ipInput = document.getElementById('ipCheckInput').value;
    
    if (!ipInput) {
        alert('Please enter an IP address');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/check-ip`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ip: ipInput })
        });
        
        const data = await response.json();
        
        const resultDiv = document.getElementById('ipCheckResult');
        resultDiv.style.display = 'block';
        
        if (data.allowed) {
            resultDiv.className = 'ip-check-result allowed';
            resultDiv.innerHTML = `✓ ${data.ip} is ALLOWED`;
        } else {
            resultDiv.className = 'ip-check-result blocked';
            resultDiv.innerHTML = `✗ ${data.ip} is BLOCKED: ${data.message}`;
        }
    } catch (error) {
        console.error('Error checking IP:', error);
    }
}

function changeUserIP() {
    const newIP = prompt('Enter your IP address:', currentUserIP);
    
    if (newIP) {
        currentUserIP = newIP;
        document.getElementById('currentIp').textContent = currentUserIP;
        document.getElementById('originalIp').textContent = currentUserIP;
        alert(`IP changed to ${currentUserIP}. Try connecting to VPN now!`);
    }
}
