import os
import subprocess
import threading
import time
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask import render_template


app = Flask(__name__)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "compressed"
FFMPEG = "ffmpeg"  # or "ffmpeg.exe" on Windows

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# In-memory task store
# -------------------------------
tasks = {}  # task_id -> {"status":..., "current":..., "total":..., "file":..., "percent":..., "files":[...]}  

# -------------------------------
# Cleanup compressed folder every 5 min
# -------------------------------
def cleanup_compressed_folder(interval_minutes=5, file_lifetime_minutes=30):
    while True:
        now = datetime.now()
        for filename in os.listdir(OUTPUT_DIR):
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(filepath):
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if now - modified_time > timedelta(minutes=file_lifetime_minutes):
                    try:
                        os.remove(filepath)
                        print(f"Deleted old compressed file: {filename}")
                    except:
                        pass
        time.sleep(interval_minutes * 60)

threading.Thread(target=cleanup_compressed_folder, daemon=True).start()

# -------------------------------
# Compression worker
# -------------------------------
def compress_worker(task_id, filenames, codec):
    total = len(filenames)
    compressed_files = []

    for idx, file in enumerate(filenames, start=1):
        in_path = os.path.join(UPLOAD_DIR, file)
        out_path = os.path.join(OUTPUT_DIR, f"compressed_{file}")

        # Get duration
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", in_path],
            capture_output=True, text=True
        )
        duration = float(probe.stdout.strip())

        cmd = [
            FFMPEG, "-y",
            "-i", in_path,
            "-c:v", codec,
            "-preset", "slow",
            "-crf", "28" if codec == "libx265" else "32",
            "-c:a", "aac",
            "-b:a", "160k",
            "-progress", "pipe:1",
            "-nostats",
            out_path
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

        for line in process.stdout:
            line = line.strip()
            if line.startswith("out_time_ms="):
                try:
                    ms = int(line.split("=")[1])
                    percent = min(int((ms / 1_000_000) / duration * 100), 100)
                except:
                    percent = 0

                tasks[task_id].update({
                    "status": "processing",
                    "current": idx,
                    "total": total,
                    "file": file,
                    "percent": percent
                })

        process.wait()
        compressed_files.append(f"compressed_{file}")

        # Delete input file after compression
        try:
            os.remove(in_path)
        except:
            pass

    # Mark task done
    tasks[task_id].update({
        "status": "done",
        "files": compressed_files,
        "percent": 100,
        "file": ""
    })

# -------------------------------
# Routes
# -------------------------------
@app.route("/start", methods=["POST"])
def start_compression():
    files = request.files.getlist("videos")
    codec = request.form.get("codec", "libx264")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    # Save uploads
    filenames = []
    for file in files:
        filename = file.filename
        file.save(os.path.join(UPLOAD_DIR, filename))
        filenames.append(filename)

    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "current": 0, "total": len(filenames),
                      "file": "", "percent": 0, "files": []}

    threading.Thread(target=compress_worker, args=(task_id, filenames, codec), daemon=True).start()

    return jsonify({"task_id": task_id})

@app.route("/")
def index():
    return app.send_static_file("index.html")  # or render_template("index.html")

@app.route("/status/<task_id>")
def status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
