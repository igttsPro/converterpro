# services/ffmpeg_service.py

import os
import subprocess
from config import TASKS, COMPRESSION_SETTINGS, FFMPEG, FFPROBE

def get_video_duration(file_path):
    """Get video duration using ffprobe"""
    try:
        probe = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            capture_output=True, text=True
        )
        return float(probe.stdout.strip())
    except:
        return 0

def compress_single_video(input_path, output_path, codec, task_id, file_index, total_files, filename):
    """Compress a single video file"""
    settings = COMPRESSION_SETTINGS.get(codec, COMPRESSION_SETTINGS["libx264"])
    
    duration = get_video_duration(input_path)
    if duration == 0:
        duration = 1  # Prevent division by zero
    
    cmd = [
        FFMPEG, "-y",
        "-i", input_path,
        "-c:v", codec,
        "-preset", settings["preset"],
        "-crf", settings["crf"],
        "-c:a", "aac",
        "-b:a", "160k",
        "-progress", "pipe:1",
        "-nostats",
        output_path
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
    
    for line in process.stdout:
        line = line.strip()
        if line.startswith("out_time_ms="):
            try:
                ms = int(line.split("=")[1])
                # Calculate percentage with bounds
                percent = min(int((ms / 1_000_000) / duration * 100), 100)
                percent = max(percent, 0)  # Ensure not negative
            except:
                percent = 0
            
            # Update task status
            if task_id in TASKS:
                TASKS[task_id].update({
                    "status": "processing",
                    "current": file_index,
                    "total": total_files,
                    "file": filename,
                    "percent": percent
                })
    
    process.wait()
    return True

def compress_video_files(task_id, filenames, codec, input_dir, output_dir):
    """Compress multiple video files"""
    compressed_files = []
    total = len(filenames)
    
    # Set initial status
    if task_id in TASKS:
        TASKS[task_id].update({
            "status": "processing",
            "current": 0,
            "total": total,
            "file": "",
            "percent": 0
        })
    
    for idx, filename in enumerate(filenames, start=1):
        input_path = os.path.join(input_dir, filename)
        output_filename = f"compressed_{filename}"
        output_path = os.path.join(output_dir, output_filename)
        
        # Check if input file exists
        if not os.path.exists(input_path):
            continue
        
        # Compress the video
        compress_single_video(input_path, output_path, codec, task_id, idx, total, filename)
        
        # Add to compressed files list
        if os.path.exists(output_path):
            compressed_files.append(output_filename)
        
        # Delete input file immediately after compression (FIX 3)
        try:
            os.remove(input_path)
        except Exception as e:
            print(f"Error deleting {input_path}: {e}")
    
    # Mark task as done
    if task_id in TASKS:
        TASKS[task_id].update({
            "status": "done",
            "files": compressed_files,
            "percent": 100,
            "file": "",
            "current": total
        })



# Video Slider
def split_video(input_path, output_path, start, end):
    duration = float(end) - float(start)

    command = [
        "ffmpeg",
        "-i", input_path,
        "-ss", str(start),
        "-t", str(duration),
        "-c", "copy",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Delete input file immediately after compression (FIX 3)
    try:
        os.remove(input_path)
    except Exception as e:
        print(f"Error deleting {input_path}: {e}")

