#!/bin/bash

# This script automates the setup of the unzipper-that-works service and timer.

echo "--- Setting up unzipper-that-works service and timer ---"

# --- Step 1: Install Python Dependencies ---
VENV_DIR="/home/oliver/unzipper-venv"
echo "Installing Python dependencies into $VENV_DIR..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install -r requirements.txt
deactivate
echo "Python dependencies installed."

# --- Step 2: Install external unarchiver tools ---
echo ""
echo "IMPORTANT: Ensure you have external unarchiver tools installed on your system."
echo "For Debian/Ubuntu, run: sudo apt install unzip unrar-free p7zip-full"
echo "Without these, the script cannot extract archives."

# --- Step 3: Copy systemd unit files ---
echo ""
echo "Copying systemd unit files to /etc/systemd/system/..."
sudo cp unzipper.service /etc/systemd/system/unzipper.service
sudo cp unzipper.timer /etc/systemd/system/unzipper.timer
echo "Systemd unit files copied."

# --- Step 4: Reload systemd daemon ---
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "Systemd daemon reloaded."

# --- Step 5: Enable and Start the Timer ---
echo "Enabling and starting unzipper.timer..."
sudo systemctl enable unzipper.timer
sudo systemctl start unzipper.timer
echo "unzipper.timer enabled and started."

echo ""
echo "--- Setup Complete! ---"
echo "The unzipper service will now run every 15 minutes."
echo "You can check its status with: sudo systemctl status unzipper.timer"
echo "You can view logs with: journalctl -u unzipper.service -f"
echo "Remember to install external unarchiver tools if you haven't already!"
