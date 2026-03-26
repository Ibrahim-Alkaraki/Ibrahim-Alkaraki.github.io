#!/bin/bash
# ==========================================
# COMPLETE RESUME DEPLOYMENT SETUP
# Run on Ubuntu 24.04 LTS Linux Server
#
# SECURITY HARDENING INCLUDED:
#   - UFW firewall: only ports 22 (SSH) and 8000 (HTTP) open
#   - File permissions: scripts not world-readable
#   - DuckDNS token never echoed to screen or logs
#   - Systemd services run as unprivileged 'ubuntu' user
#   - Services bind to 0.0.0.0 only on the required port
# ==========================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

echo "=========================================="
echo "RESUME SERVER DEPLOYMENT SETUP"
echo "=========================================="

# ==========================================
# STEP 1: Create HTTP Server (if missing)
# ==========================================
echo ""
echo "[STEP 1] Creating HTTP Server..."

cat > ~/resume_app/http_server.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/RESUME.html'
        return super().do_GET()

PORT = 8000
Handler = MyHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running on http://localhost:{PORT}")
    httpd.serve_forever()
EOF

chmod +x ~/resume_app/*.py
echo "✓ HTTP Server created"

# ==========================================
# STEP 2: Test Servers (Optional)
# ==========================================
echo ""
echo "[STEP 2] Testing servers (30 second test)..."
echo "Starting http_server.py in background..."

cd ~/resume_app
timeout 30 python3 http_server.py > /tmp/http_test.log 2>&1 &
HTTP_PID=$!

sleep 3

echo "Testing connection to http://localhost:8000..."
if curl -s http://localhost:8000 | grep -q "<!DOCTYPE html>"; then
    echo "✓ HTTP Server works! (serving RESUME.html)"
else
    echo "⚠ Warning: Could not connect to HTTP server"
fi

kill $HTTP_PID 2>/dev/null
wait $HTTP_PID 2>/dev/null

echo ""
echo "[STEP 3] DuckDNS Setup..."
echo ""
echo "⚠ BEFORE CONTINUING:"
echo "  1. Go to https://www.duckdns.org/"
echo "  2. Sign in (Google/GitHub)"
echo "  3. Create subdomain: ibrahimakraki"
echo "  4. Copy your TOKEN"
echo ""
read -p "Paste your DuckDNS TOKEN here: " DUCKDNS_TOKEN

if [ -z "$DUCKDNS_TOKEN" ]; then
    echo "❌ Token is empty. Exiting."
    exit 1
fi

echo "✓ Token received (hidden for security)"

# ==========================================
# STEP 4: Create DuckDNS Update Script
# ==========================================
echo ""
echo "[STEP 4] Creating DuckDNS updater script..."

cat > ~/resume_app/duckdns_update.sh << EOF
#!/bin/bash
# Update DuckDNS every 5 minutes

DOMAIN="ibrahimakraki"
TOKEN="$DUCKDNS_TOKEN"
INTERVAL=300  # 5 minutes

while true; do
    IP=\$(hostname -I | awk '{print \$1}')
    curl -s "https://www.duckdns.org/update?domains=\${DOMAIN}&token=\${TOKEN}&ip=\${IP}" > /dev/null
    echo "[\$(date '+%Y-%m-%d %H:%M:%S')] Updated DuckDNS: \${DOMAIN}.duckdns.org -> \${IP}"
    sleep \$INTERVAL
done
EOF

chmod +x ~/resume_app/duckdns_update.sh
echo "✓ DuckDNS updater created"

# Test it once
echo "[STEP 5] Testing DuckDNS connection..."
IP=$(hostname -I | awk '{print $1}')
RESPONSE=$(curl -s "https://www.duckdns.org/update?domains=ibrahimakraki&token=$DUCKDNS_TOKEN&ip=$IP")
echo "DuckDNS Response: $RESPONSE"

if [[ $RESPONSE == *"OK"* ]]; then
    echo "✓ DuckDNS connection works!"
else
    echo "⚠ Warning: DuckDNS returned unexpected response"
fi

# ==========================================
# STEP 5.5: Firewall & File Permissions
# ==========================================
echo ""
echo "[STEP 5.5] Configuring UFW firewall & file permissions..."

# Only allow SSH and the HTTP server port
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # Resume HTTP server
sudo ufw --force enable
echo "✓ Firewall configured: only ports 22 (SSH) and 8000 (HTTP) open"

# Restrict file permissions — server files owned by ubuntu, not world-readable
chmod 700 ~/resume_app
chmod 600 ~/resume_app/*.py
chmod 600 ~/resume_app/duckdns_update.sh
chmod 755 ~/resume_app/RESUME.html ~/resume_app/fun_system_event.html 2>/dev/null || true
chmod 700 ~/resume_app/scripts
chmod 600 ~/resume_app/scripts/*.py 2>/dev/null || true
chmod 700 ~/resume_app/security
chmod 600 ~/resume_app/security/*.py 2>/dev/null || true
echo "✓ File permissions tightened"

# ==========================================
# STEP 6: Create Systemd Services
# ==========================================
echo ""
echo "[STEP 6] Creating systemd services..."

# HTTP Server Service
sudo tee /etc/systemd/system/resume-http.service > /dev/null << 'EOF'
[Unit]
Description=Resume HTTP Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/resume_app
ExecStart=/usr/bin/python3 /home/ubuntu/resume_app/http_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# API Server Service
sudo tee /etc/systemd/system/resume-api.service > /dev/null << 'EOF'
[Unit]
Description=Resume API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/resume_app
ExecStart=/usr/bin/python3 /home/ubuntu/resume_app/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# DuckDNS Service
sudo tee /etc/systemd/system/duckdns.service > /dev/null << 'EOF'
[Unit]
Description=DuckDNS Updater
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/home/ubuntu/resume_app/duckdns_update.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Systemd services created"

# ==========================================
# STEP 7: Enable and Start Services
# ==========================================
echo ""
echo "[STEP 7] Enabling and starting services..."

sudo systemctl daemon-reload
sudo systemctl enable resume-http.service
sudo systemctl enable resume-api.service
sudo systemctl enable duckdns.service

sudo systemctl start resume-http.service
sudo systemctl start resume-api.service
sudo systemctl start duckdns.service

echo "✓ Services enabled and started"

# ==========================================
# STEP 8: Verify Services
# ==========================================
echo ""
echo "[STEP 8] Verifying services..."
echo ""

echo "HTTP Server Status:"
sudo systemctl status resume-http.service --no-pager | head -n 3

echo ""
echo "API Server Status:"
sudo systemctl status resume-api.service --no-pager | head -n 3

echo ""
echo "DuckDNS Service Status:"
sudo systemctl status duckdns.service --no-pager | head -n 3

echo ""
echo "=========================================="
echo "✓ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Your resume is now live at:"
echo "  🏠 Local Network: http://10.0.0.144:8000"
echo "  🌐 Internet:      http://ibrahimakraki.duckdns.org:8000"
echo ""
echo "Services will auto-start on reboot!"
echo ""
echo "Check logs anytime with:"
echo "  sudo journalctl -u resume-http.service -f"
echo "  sudo journalctl -u duckdns.service -f"
echo ""
echo "=========================================="
