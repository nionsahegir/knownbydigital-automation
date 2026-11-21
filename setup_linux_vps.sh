#!/bin/bash
# ==============================================================
# Known By Digital - 1-Click Ubuntu/Debian VPS Automated Setup
# ==============================================================
set -e

echo "🚀 [1/5] Updating Linux Packages & Installing FFmpeg..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg tzdata git

echo "⏰ [2/5] Setting Timezone to Asia/Dhaka (BST)..."
sudo timedatectl set-timezone Asia/Dhaka

echo "🐍 [3/5] Setting up Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🌐 [4/5] Installing Playwright Chromium & System Dependencies..."
playwright install chromium
playwright install-deps chromium

echo "⚙️ [5/5] Creating Systemd Background Service (24/7 Auto-Start on Reboot)..."
APP_DIR=$(pwd)
USER_NAME=$(whoami)

SERVICE_FILE="/etc/systemd/system/kbd-automation.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Known By Digital Autonomous Multi-Channel Social Automation
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python scheduler_daemon.py
Restart=always
RestartSec=10
EnvironmentFile=$APP_DIR/.env

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable kbd-automation.service
sudo systemctl restart kbd-automation.service

echo "=============================================================="
echo "✅ SUCCESS! Known By Digital Social Automation is now running 24/7!"
echo "Check status anytime with:  sudo systemctl status kbd-automation"
echo "View live logs with:        journalctl -u kbd-automation -f"
echo "=============================================================="
