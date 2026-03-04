# Unzipper That Works

This project provides a robust Python script to automatically monitor a directory for downloaded archives, extract them once they are complete, and then clean up the original archive files after a configurable period.

It is designed to be resilient, ensuring that it only extracts files that have finished downloading. This is achieved by monitoring file size and modification times, preventing interference with ongoing downloads.

## How It Works

The script operates in a clear, sequential process designed to be run periodically as a service.

### 1. File Stability Check

The core logic of this script revolves around determining if an archive is "fully downloaded" and ready for extraction. To do this, it maintains a state file (`file_states.json`) that tracks the properties of archives in the download directory.

- **New Files:** When a new archive (e.g., `.zip`, `.rar`) is detected, it is added to the state file with its current size, modification time, and a timestamp.
- **Monitoring:** On subsequent runs, the script checks if the file's size or modification time has changed. If it has, the file is considered "in-progress," and the script updates its state and moves on.
- **Stability Threshold:** A file is only considered "stable" and ready for extraction if its size and modification time have not changed for a specific duration (default: 120 seconds). This prevents the script from trying to extract a file that is still being written to disk.

### 2. Extraction

Once an archive is deemed stable, the extraction process begins:

- **Destination:** The script creates a new folder in the same directory, named after the archive file (without the extension).
- **Extraction:** It uses the `patoolib` library to handle the extraction, which supports a wide range of formats like `.zip`, `.rar`, `.7z`, and more.
- **Marking as Complete:** After a successful extraction, the script creates a marker file (e.g., `MyArchive.zip.gemini_extracted_marker`). This file signals that the archive has been processed and prevents it from being extracted again on future runs.

### 3. Old Archive Cleanup

To prevent the download directory from filling up with redundant archives, a cleanup process runs automatically:

- **Age Limit:** The script scans for marker files older than a configurable number of days (default: 30 days).
- **Deletion:** If an extracted archive is older than the limit, the script deletes both the original archive file and its associated marker file, freeing up space.

## Log Examples

The script provides detailed logs to show its progress. Here are some examples of what you might see in the systemd journal or when running the script manually.

**A new archive is detected and monitored:**
```
INFO: New archive detected: /mnt/smbshare/plex/downloads/NewShow.S01E01.zip. Monitoring for stability.
```

**An archive is still being downloaded:**
```
INFO: File is still changing: /mnt/smbshare/plex/downloads/NewShow.S01E01.zip
```

**An archive becomes stable and is extracted:**
```
INFO: File is stable: /mnt/smbshare/plex/downloads/NewShow.S01E01.zip (stable for 125 seconds)
INFO: Found 1 stable archives to process for extraction.
INFO: Attempting to extract: /mnt/smbshare/plex/downloads/NewShow.S01E01.zip
INFO: Successfully extracted /mnt/smbshare/plex/downloads/NewShow.S01E01.zip to /mnt/smbshare/plex/downloads/NewShow.S01E01
```

**An old, extracted archive is cleaned up:**
```
INFO: Starting old archive cleanup process.
INFO: Deleting old archive: /mnt/smbshare/plex/downloads/OldMovie.rar (extracted on 2023-10-26)
INFO: Removed /mnt/smbshare/plex/downloads/OldMovie.rar and /mnt/smbshare/plex/downloads/OldMovie.rar.gemini_extracted_marker
INFO: Old archive cleanup process finished.
```

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
