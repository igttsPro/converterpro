# routes/slit_video.py


from flask import Blueprint, request, jsonify, render_template, send_from_directory, current_app
import os
from utils.file_utils import save_uploaded_files
from services.ffmpeg_service import split_video as ffmpeg_split_video

split_bp = Blueprint("split_bp", __name__)

# Folders (already exist in your project)
UPLOAD_FOLDER = "incoming"
OUTPUT_FOLDER = "processed"


# -------------------------------
# PAGE ROUTE (renders split.html)
# -------------------------------
#@split_bp.route("/split", methods=["GET"])
#def split_page():
#    return render_template("pages/split.html")


# -------------------------------
# API: Split Video
# -------------------------------
@split_bp.route("/split-video", methods=["POST"])
def split_video():
    video = request.files.get("video")
    start = request.form.get("start")
    end = request.form.get("end")

    if not video:
        return jsonify({"error": "No video uploaded"}), 400

    if start is None or end is None:
        return jsonify({"error": "Start and end times are required"}), 400

    # Validate numeric times
    try:
        start_float = float(start)
        end_float = float(end)
        if end_float <= start_float:
            return jsonify({"error": "End time must be greater than start time"}), 400
    except ValueError:
        return jsonify({"error": "Invalid time values"}), 400

    # Ensure folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Save uploaded video using existing utility function
    saved_files = save_uploaded_files([video], UPLOAD_FOLDER)

    if not saved_files:
        return jsonify({"error": "Failed to save uploaded video"}), 400

    input_filename = saved_files[0]
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)

    # Output file name
    output_filename = f"split_{input_filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Perform the split using FFmpeg
    try:
        ffmpeg_split_video(input_path, output_path, start_float, end_float)
    except Exception as e:
        current_app.logger.exception("Error splitting video")
        return jsonify({"error": "Failed to split video"}), 500

    return jsonify({
        "status": "done",
        "file": output_filename
    })


# -------------------------------
# DOWNLOAD ROUTE
# -------------------------------
@split_bp.route("/download-split/<filename>", methods=["GET"])
def download_split(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
