# Unzipper That Works

This project provides a robust Python script to automatically monitor a directory for downloaded archives, extract them once they are complete, and then clean up the original archive files after a configurable period.

It is designed to be resilient, ensuring that it only extracts files that have finished downloading. This is achieved by monitoring file size and modification times, preventing interference with ongoing downloads.

## Features

- Monitors a specified directory for new downloads.
- Uses a file stability check (no size or modification time changes) to determine if a file is complete.
- Extracts various archive types (e.g., `.zip`, `.rar`, `.7z`).
- Cleans up extracted archive files that are older than one month.
- Designed to run as a systemd service every 15 minutes.
- Includes a distribution-agnostic setup script for easy installation.

## Installation

Choose the automatic method for a quick setup or the manual method if you prefer granular control.

### Automatic Installation (Recommended)

This method uses the included setup script to install all dependencies and configure the systemd service automatically. It will prompt for your password to install system-level packages.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/oscampbell/unzipper-that-works.git
    cd unzipper-that-works
    ```

2.  **Run the setup script:**
    Make the script executable and run it.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

That's it! The script will handle system dependencies, Python packages, and systemd service setup.

### Manual Installation

Follow these steps if you want to set up the service manually.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/oscampbell/unzipper-that-works.git
    cd unzipper-that-works
    ```

2.  **Install System Dependencies:**
    You need Python, pip, venv, and the command-line tools for the archive formats you use.

    *   **For Debian/Ubuntu:**
        ```bash
        sudo apt-get update
        sudo apt-get install -y python3-venv python3-pip unzip unrar p7zip-full
        ```
    *   **For Fedora/CentOS/RHEL:**
        ```bash
        sudo dnf install -y python3-devel python3-pip unzip unrar p7zip
        ```
    *   **For Arch Linux:**
        ```bash
        sudo pacman -Syu --noconfirm python python-pip unzip unrar p7zip
        ```

3.  **Create a Virtual Environment:**
    Create a local virtual environment to isolate Python packages.
    ```bash
    python3 -m venv .venv
    ```

4.  **Install Python Dependencies:**
    Activate the virtual environment and install the required package from `requirements.txt`.
    ```bash
    source .venv/bin/activate
    pip install -r requirements.txt
    deactivate
    ```

5.  **Configure and Install the systemd Service:**
    You need to update the service file with the correct paths for your system before copying it.

    *   **Get Project Path:**
        ```bash
        PROJECT_DIR=$(pwd)
        ```
    *   **Get User/Group:**
        ```bash
        CURRENT_USER=$(whoami)
        CURRENT_GROUP=$(id -gn $CURRENT_USER)
        ```
    *   **Create a temporary service file and replace placeholders:**
        ```bash
        cp unzipper.service unzipper.service.tmp
        sed -i "s|__WORKING_DIR__|$PROJECT_DIR|g" unzipper.service.tmp
        sed -i "s|__VENV_PATH__|$PROJECT_DIR/.venv|g" unzipper.service.tmp
        sed -i "s|__USER__|$CURRENT_USER|g" unzipper.service.tmp
        sed -i "s|__GROUP__|$CURRENT_GROUP|g" unzipper.service.tmp
        ```
    *   **Copy the files to the systemd directory:**
        ```bash
        sudo cp unzipper.service.tmp /etc/systemd/system/unzipper.service
        sudo cp unzipper.timer /etc/systemd/system/unzipper.timer
        ```

6.  **Enable and Start the Service:**
    Reload the systemd daemon and start the timer.
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now unzipper.timer
    ```

## How It Works

The script operates in a clear, sequential process designed to be run periodically as a service.

### 1. File Stability Check
The core logic revolves around determining if an archive is "fully downloaded." To do this, it maintains a state file (`file_states.json`) that tracks archives.

- **New Files:** When a new archive (e.g., `.zip`, `.rar`) is detected, it is added to the state file.
- **Monitoring:** On subsequent runs, the script checks if the file's size or modification time has changed.
- **Stability Threshold:** A file is only considered "stable" and ready for extraction if it hasn't changed for a specific duration (default: 30 minutes).

### 2. Extraction
Once an archive is deemed stable, the extraction process begins:

- **Destination:** The script creates a new folder named after the archive.
- **Extraction:** It uses `patoolib` to handle `.zip`, `.rar`, `.7z`, and more.
- **Marking as Complete:** A marker file (`.gemini_extracted_marker`) is created to prevent re-extraction.

### 3. Old Archive Cleanup
To prevent the download directory from filling up, extracted archives older than a configurable number of days (default: 30) are automatically deleted along with their marker files.

## Usage
Once the service is set up, it runs automatically. To check its status or view logs:

- **Check timer status:**
  ```bash
  sudo systemctl status unzipper.timer
  ```
- **Follow service logs:**
  ```bash
  journalctl -u unzipper.service -f
  ```
- **Manual Run:**
  You can also run the script manually for testing (ensure you are in the project directory):
  ```bash
  source .venv/bin/activate
  python unzipper.py
  ```
