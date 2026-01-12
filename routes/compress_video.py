# routes/compress_video.py

from flask import Blueprint, request, jsonify, send_from_directory
import uuid
import threading
from config import UPLOAD_DIR, OUTPUT_DIR, TASKS
from services.ffmpeg_service import compress_video_files
from utils.file_utils import save_uploaded_files
import os

compress_bp = Blueprint('compress', __name__)

@compress_bp.route("/start", methods=["POST"])
def start_compression():
    """Start video compression task"""
    files = request.files.getlist("videos")
    codec = request.form.get("codec", "libx264")
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No files uploaded"}), 400
    
    # Save uploaded files - ONLY ONCE
    filenames = save_uploaded_files(files, UPLOAD_DIR)
    
    if not filenames:
        return jsonify({"error": "No valid video files uploaded"}), 400
    
    # Create task entry
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {
        "status": "pending",
        "current": 0,
        "total": len(filenames),
        "file": "",
        "percent": 0,
        "files": []
    }
    
    # Start compression in background thread
    threading.Thread(
        target=compress_video_files,
        args=(task_id, filenames, codec, UPLOAD_DIR, OUTPUT_DIR),
        daemon=True
    ).start()
    
    return jsonify({"task_id": task_id})

@compress_bp.route("/status/<task_id>")
def status(task_id):
    """Get compression task status"""
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@compress_bp.route("/download/<filename>")
def download(filename):
    """Download compressed file"""
    # Validate filename for security
    if not filename or '..' in filename or filename.startswith('/'):
        return jsonify({"error": "Invalid filename"}), 400
    
    if not os.path.exists(os.path.join(OUTPUT_DIR, filename)):
        return jsonify({"error": "File not found"}), 404
    
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)