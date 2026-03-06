#!/bin/bash

# This script automates the setup of the unzipper-that-works service and timer.

set -e # Exit immediately if a command exits with a non-zero status.

echo "--- Setting up unzipper-that-works service and timer ---"

# --- Step 1: Detect Package Manager and Install System Dependencies ---
echo "Detecting package manager and installing system dependencies..."
echo "This may require you to enter your password for sudo."

install_packages() {
    if [ -x "$(command -v apt-get)" ]; then
        sudo apt-get update
        sudo apt-get install -y python3-venv python3-pip unzip unrar p7zip-full
    elif [ -x "$(command -v dnf)" ]; then
        sudo dnf install -y python3-devel python3-pip unzip unrar p7zip
    elif [ -x "$(command -v yum)" ]; then
        # For older CentOS/RHEL
        sudo yum install -y python3-devel python3-pip unzip unrar p7zip
    elif [ -x "$(command -v pacman)" ]; then
        sudo pacman -Syu --noconfirm python python-pip unzip unrar p7zip
    else
        echo "ERROR: Unsupported package manager. Please install the following manually:"
        echo " - python3-venv, python3-pip"
        echo " - unzip, unrar, p7zip"
        exit 1
    fi
}

install_packages
echo "System dependencies installed."

# --- Step 2: Create Virtual Environment and Install Python Dependencies ---
VENV_DIR=".venv"
PROJECT_DIR=$(pwd)

echo "Creating Python virtual environment in $VENV_DIR..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install -r requirements.txt
deactivate
echo "Python dependencies installed."

# --- Step 3: Configure systemd Unit Files ---
echo "Configuring systemd unit files..."

CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn $CURRENT_USER)

# Create temporary copies to avoid modifying the git-tracked files directly
cp unzipper.service unzipper.service.tmp
cp unzipper.timer unzipper.timer.tmp

# Replace placeholders
sed -i "s|__WORKING_DIR__|$PROJECT_DIR|g" unzipper.service.tmp
sed -i "s|__VENV_PATH__|$PROJECT_DIR/$VENV_DIR|g" unzipper.service.tmp
sed -i "s|__USER__|$CURRENT_USER|g" unzipper.service.tmp
sed -i "s|__GROUP__|$CURRENT_GROUP|g" unzipper.service.tmp

echo "Configured service file:"
cat unzipper.service.tmp

# --- Step 4: Copy systemd unit files to system directory ---
echo "Copying systemd unit files to /etc/systemd/system/..."
sudo cp unzipper.service.tmp /etc/systemd/system/unzipper.service
sudo cp unzipper.timer.tmp /etc/systemd/system/unzipper.timer
rm unzipper.service.tmp unzipper.timer.tmp
echo "Systemd unit files copied."

# --- Step 5: Reload systemd, Enable and Start the Timer ---
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "Enabling and starting unzipper.timer..."
sudo systemctl enable --now unzipper.timer
echo "unzipper.timer enabled and started."

echo ""
echo "--- Setup Complete! ---"
echo "The unzipper service will now run every 15 minutes."
echo "To check the timer status: sudo systemctl status unzipper.timer"
echo "To view service logs: journalctl -u unzipper.service -f"
