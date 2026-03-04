#!/usr/bin/env python3

import os
import logging
import datetime
import json
import time
import patoolib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
DOWNLOAD_DIR = "/mnt/smbshare/plex/downloads"
MARKER_FILE_EXTENSION = ".gemini_extracted_marker"
ARCHIVE_CLEANUP_DAYS = 30
STATE_FILE = os.path.join(os.path.dirname(__file__), "file_states.json")
FILE_STABILITY_THRESHOLD_SECONDS = 120  # File size and mod time must be stable for this long

ARCHIVE_EXTENSIONS = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.tgz', '.tbz', '.xz']

def load_file_states():
    """Loads the file states from the JSON state file."""
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Error loading state file {STATE_FILE}: {e}")
        return {}

def save_file_states(states):
    """Saves the file states to the JSON state file."""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(states, f, indent=4)
    except IOError as e:
        logging.error(f"Error saving state file {STATE_FILE}: {e}")

def find_and_extract_archives(stable_archives):
    """
    Extracts a list of stable archive files.
    """
    logging.info(f"Found {len(stable_archives)} stable archives to process for extraction.")
    if not stable_archives:
        return

    for archive_path in stable_archives:
        marker_file = archive_path + MARKER_FILE_EXTENSION
        if os.path.exists(marker_file):
            logging.info(f"Skipping already extracted archive: {archive_path}")
            continue

        logging.info(f"Attempting to extract: {archive_path}")
        try:
            archive_basename = os.path.basename(archive_path)
            extraction_dir_name = os.path.splitext(archive_basename)[0]
            extraction_parent_dir = os.path.dirname(archive_path)
            destination_dir = os.path.join(extraction_parent_dir, extraction_dir_name)

            os.makedirs(destination_dir, exist_ok=True)
            
            patoolib.extract_archive(archive_path, outdir=destination_dir, verbosity=-1)
            
            with open(marker_file, 'w') as f:
                f.write(f"Extracted on {datetime.datetime.now().isoformat()}")
            
            logging.info(f"Successfully extracted {archive_path} to {destination_dir}")

        except patoolib.util.PatoolError as e:
            logging.error(f"Failed to extract {archive_path}: {e}")
            logging.warning("Ensure necessary unarchive tools (e.g., unzip, unrar, 7z) are installed.")
        except Exception as e:
            logging.error(f"An unexpected error occurred while extracting {archive_path}: {e}")

def cleanup_old_archives():
    """
    Removes old, extracted archive files from the download directory.
    """
    logging.info("Starting old archive cleanup process.")
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=ARCHIVE_CLEANUP_DAYS)
    
    for root, _, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            if any(file.lower().endswith(ext) for ext in ARCHIVE_EXTENSIONS):
                archive_path = os.path.join(root, file)
                marker_file = archive_path + MARKER_FILE_EXTENSION

                if os.path.exists(marker_file):
                    try:
                        marker_mod_timestamp = os.path.getmtime(marker_file)
                        marker_mod_datetime = datetime.datetime.fromtimestamp(marker_mod_timestamp)

                        if marker_mod_datetime < cutoff_date:
                            logging.info(f"Deleting old archive: {archive_path} (extracted on {marker_mod_datetime.strftime('%Y-%m-%d')})")
                            os.remove(archive_path)
                            os.remove(marker_file)
                            logging.info(f"Removed {archive_path} and {marker_file}")
                    except OSError as e:
                        logging.error(f"Error accessing file {archive_path} or {marker_file}: {e}")

    logging.info("Old archive cleanup process finished.")


def main():
    """
    Main function for the unzipper service.
    Scans for archives and extracts them if they are considered stable.
    """
    logging.info("Starting unzipper service (file stability check method)...")
    
    file_states = load_file_states()
    current_time = time.time()
    stable_archives_to_extract = []

    logging.info(f"Scanning {DOWNLOAD_DIR} for archives...")
    for root, _, files in os.walk(DOWNLOAD_DIR):
        for file in files:
            if not any(file.lower().endswith(ext) for ext in ARCHIVE_EXTENSIONS):
                continue
            
            file_path = os.path.join(root, file)
            marker_file = file_path + MARKER_FILE_EXTENSION
            if os.path.exists(marker_file):
                continue

            try:
                stat_info = os.stat(file_path)
                file_size = stat_info.st_size
                file_mod_time = stat_info.st_mtime
            except FileNotFoundError:
                logging.warning(f"File not found during scan, it may have been deleted: {file_path}")
                if file_path in file_states:
                    del file_states[file_path]
                continue

            if file_path not in file_states:
                # New file found, add it to state
                logging.info(f"New archive detected: {file_path}. Monitoring for stability.")
                file_states[file_path] = {
                    "size": file_size,
                    "mtime": file_mod_time,
                    "first_seen": current_time,
                    "last_changed": current_time
                }
            else:
                # Existing file, check for changes
                last_state = file_states[file_path]
                if file_size != last_state["size"] or file_mod_time > last_state["mtime"]:
                    logging.info(f"File is still changing: {file_path}")
                    last_state["size"] = file_size
                    last_state["mtime"] = file_mod_time
                    last_state["last_changed"] = current_time
                else:
                    # File size and mod time are unchanged, check how long it's been stable
                    stable_duration = current_time - last_state["last_changed"]
                    if stable_duration >= FILE_STABILITY_THRESHOLD_SECONDS:
                        logging.info(f"File is stable: {file_path} (stable for {stable_duration:.0f} seconds)")
                        stable_archives_to_extract.append(file_path)
                        
    # For files that are now stable, remove them from the state tracking
    for archive_path in stable_archives_to_extract:
        if archive_path in file_states:
             del file_states[archive_path]

    # Clean up state for files that no longer exist
    # This is a simple cleanup, more robust logic could be added
    for file_path in list(file_states.keys()):
        if not os.path.exists(file_path):
             logging.info(f"Removing non-existent file from state tracking: {file_path}")
             del file_states[file_path]

    save_file_states(file_states)

    if stable_archives_to_extract:
        find_and_extract_archives(stable_archives_to_extract)
    else:
        logging.info("No new stable archives to extract this run.")

    cleanup_old_archives()

    logging.info("Unzipper service finished.")

if __name__ == "__main__":
    main()
