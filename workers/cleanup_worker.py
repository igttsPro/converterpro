# workers/cleanup_worker.py

import os
import time
import threading
from datetime import datetime, timedelta
from config import OUTPUT_DIR, CLEANUP_INTERVAL_MINUTES, FILE_LIFETIME_MINUTES

def cleanup_processed_folder():
    """Periodically clean up old files in processed folder"""
    while True:
        now = datetime.now()
        for filename in os.listdir(OUTPUT_DIR):
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(filepath):
                try:
                    modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if now - modified_time > timedelta(minutes=FILE_LIFETIME_MINUTES):
                        os.remove(filepath)
                        print(f"Deleted old processed file: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
        time.sleep(CLEANUP_INTERVAL_MINUTES * 30)

def start_cleanup_worker():
    """Start the cleanup worker in a background thread"""
    worker = threading.Thread(target=cleanup_processed_folder, daemon=True)
    worker.start()
    return worker
