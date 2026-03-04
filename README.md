# Unzipper That Works

This project provides a Python script to automatically monitor a downloads directory for completed archive files, extract them, and then clean up the old archives after a specified period.

This script determines if a file is "fully downloaded" by checking its size and modification time. A file is considered complete and ready for extraction if its size and modification time have not changed for a configurable period (default: 120 seconds).

## Features

- Monitors a specified directory for new downloads.
- Uses a file stability check (no size or modification time changes) to determine if a file is complete.
- Extracts various archive types (e.g., `.zip`, `.rar`, `.7z`).
- Cleans up extracted archive files that are older than one month.
- Designed to run as a systemd service every 15 minutes.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:oscampbell/unzipper-that-works.git
    cd unzipper-that-works
    ```

2.  **Create a virtual environment and install dependencies:**
    The setup script handles this, but you can do it manually:
    ```bash
    # It is recommended to create the venv outside of the SMB share
    python3 -m venv /home/oliver/unzipper-venv
    source /home/oliver/unzipper-venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Install external unarchiver tools:**
    The `patool` library (used by this script) acts as a wrapper around command-line archive tools. Ensure you have the necessary tools installed on your system for the archive types you expect.
    For example, on Debian/Ubuntu:
    ```bash
    sudo apt install unzip unrar p7zip-full
    ```

4.  **Configure and run as a systemd service (Recommended):**
    The `setup.sh` script automates this process.
    ```bash
    ./setup.sh
    ```

## Usage

The script runs automatically once set up as a service. You can manually run it for testing:
```bash
/home/oliver/unzipper-venv/bin/python3 unzipper.py
```

## Project Structure

```
.
├── .gitignore
├── README.md
├── requirements.txt
├── unzipper.py
├── unzipper.service
├── unzipper.timer
├── setup.sh
└── file_states.json      # Stores file stability info (created on first run)
```
