import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory paths
UPLOAD_DIR = os.path.join(BASE_DIR, "incoming")
OUTPUT_DIR = os.path.join(BASE_DIR, "processed")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# FFmpeg configuration
FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

# Task management
TASKS = {}  # In-memory task store (for simple deployment)

# Cleanup settings
CLEANUP_INTERVAL_MINUTES = 1
FILE_LIFETIME_MINUTES = 5

# Video compression settings
COMPRESSION_SETTINGS = {
    "libx264": {"crf": "32", "preset": "slow"},
    "libx265": {"crf": "28", "preset": "slow"}
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}