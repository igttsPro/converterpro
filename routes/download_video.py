from flask import Blueprint, request, jsonify, render_template, send_from_directory
import os
from services.downloader_service import extract_video_info, download_selected_format

download_bp = Blueprint("download_bp", __name__)

OUTPUT_FOLDER = "processed"


# -------------------------------
# PAGE ROUTE
# -------------------------------
@download_bp.route("/download", methods=["GET"])
def download_page():
    return render_template("pages/download.html")


# -------------------------------
# API: Fetch formats
# -------------------------------
@download_bp.route("/fetch-formats", methods=["POST"])
def fetch_formats():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        info = extract_video_info(url)
        return jsonify(info)
    except Exception as e:
        print("YT-DLP ERROR:", e)
        return jsonify({"error": str(e)}), 500



# -------------------------------
# API: Download selected format
# -------------------------------
@download_bp.route("/download-video", methods=["POST"])
def download_video():
    data = request.get_json()
    url = data.get("url")
    format_id = data.get("format_id")

    if not url or not format_id:
        return jsonify({"error": "Missing URL or format ID"}), 400

    try:
        filename = download_selected_format(url, format_id, OUTPUT_FOLDER)
        
        # Check if filename is valid
        if not filename:
            return jsonify({"error": "Download failed - no file created"}), 500
            
        return jsonify({"status": "done", "file": filename})
        
    except Exception as e:
        print("YT-DLP DOWNLOAD ERROR:", str(e))  # Convert exception to string
        error_msg = str(e) if str(e) else "Unknown download error"
        return jsonify({"error": error_msg}), 500

# -------------------------------
# DOWNLOAD ROUTE
# -------------------------------
@download_bp.route("/download-file/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
