# Complete Linux Server Deployment Guide

## Your Setup
- **Server**: `ibrahim@mylinuxserver`
- **Local IP**: `10.0.0.144`
- **OS**: Ubuntu 24.04 LTS
- **Domain**: DuckDNS (free) - `ibrahimakraki.duckdns.org`

---

## PHASE 1: Transfer Files from Mac to Linux Server

Run these commands **on your Mac** (in the ResumeRepo directory):

```bash
cd /Users/admin/Desktop/Learn/ResumeRepo

# Transfer all resume files to Linux server
scp RESUME.html ibrahim@10.0.0.144:~/resume_app/
scp server.py ibrahim@10.0.0.144:~/resume_app/
scp password_manager_enhanced.py ibrahim@10.0.0.144:~/resume_app/
scp network_device_manager_enhanced.py ibrahim@10.0.0.144:~/resume_app/
scp file_manager_enhanced.py ibrahim@10.0.0.144:~/resume_app/
scp fun_system_event.html ibrahim@10.0.0.144:~/resume_app/
```

It will ask for your Linux password - type it.

---

## PHASE 2: Setup on Linux Server

Run these commands **on your Linux server**:

### Step 1: Create HTTP server
```bash
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
```

### Step 2: Make scripts executable
```bash
chmod +x ~/resume_app/*.py
```

### Step 3: Test the setup (optional)
```bash
cd ~/resume_app
# Terminal 1
python3 server.py &

# Terminal 2
python3 http_server.py &

# You should see them running. Kill with: jobs, kill %1, kill %2
```

---

## PHASE 3: DuckDNS Setup (Free Domain)

### Step 1: Create DuckDNS account
1. Go to: https://www.duckdns.org/
2. Sign in with your choice (Google/GitHub)
3. Create subdomain: `ibrahimakraki`
4. Copy your **token** (you'll need it)

### Step 2: Create DuckDNS update script
```bash
cat > ~/resume_app/duckdns_update.sh << 'EOF'
#!/bin/bash
# Update DuckDNS every 5 minutes with your current IP

DOMAIN="ibrahimakraki"
TOKEN="YOUR_DUCKDNS_TOKEN_HERE"  # REPLACE THIS
INTERVAL=300  # 5 minutes

while true; do
    # Get your current public/local IP
    IP=$(hostname -I | awk '{print $1}')
    
    # Update DuckDNS
    curl -s "https://www.duckdns.org/update?domains=${DOMAIN}&token=${TOKEN}&ip=${IP}" > /dev/null
    
    echo "[$(date)] Updated DuckDNS: ${DOMAIN}.duckdns.org -> ${IP}"
    sleep $INTERVAL
done
EOF

chmod +x ~/resume_app/duckdns_update.sh
```

**IMPORTANT**: Replace `YOUR_DUCKDNS_TOKEN_HERE` with your actual DuckDNS token!

---

## PHASE 4: Create Systemd Services (Auto-Start on Boot)

### Service 1: Resume HTTP Server
```bash
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
```

### Service 2: Resume API Server
```bash
sudo tee /etc/systemd/system/resume-api.service > /dev/null << 'EOF'
[Unit]
Description=Resume API Backend
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
```

### Service 3: DuckDNS Updater
```bash
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
```

### Enable and Start Services
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable resume-http.service
sudo systemctl enable resume-api.service
sudo systemctl enable duckdns.service

# Start services now
sudo systemctl start resume-http.service
sudo systemctl start resume-api.service
sudo systemctl start duckdns.service

# Check status
sudo systemctl status resume-http.service
sudo systemctl status resume-api.service
sudo systemctl status duckdns.service
```

---

## PHASE 5: Setup Domain with HTTPS (Optional but Recommended)

### Install Certbot for HTTPS
```bash
sudo apt install -y certbot python3-certbot-nginx nginx

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Get SSL Certificate
```bash
sudo certbot certonly --standalone -d ibrahimakraki.duckdns.org
```

---

## FINAL: Access Your Resume

After everything is set up:

1. **Local Network**: `http://10.0.0.144:8000`
2. **From Internet**: `https://ibrahimakraki.duckdns.org` (after nginx reverse proxy setup)
3. **API Calls**: `http://10.0.0.144:5000` or `https://ibrahimakraki.duckdns.org/api`

---

## Troubleshooting

### Check service logs
```bash
sudo journalctl -u resume-http.service -f
sudo journalctl -u resume-api.service -f
sudo journalctl -u duckdns.service -f
```

### Kill and restart services
```bash
sudo systemctl restart resume-http.service
sudo systemctl restart resume-api.service
```

### Check if ports are in use
```bash
sudo lsof -i :8000
sudo lsof -i :5000
```

---

## Security Notes
- Only expose what's necessary (port 80/443)
- DuckDNS updates your IP every 5 minutes
- Use HTTPS in production
- Consider firewall rules: `sudo ufw allow 80,443/tcp`

---

Good to go! 🚀
