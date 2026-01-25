# routes/video_ops.py

from flask import Blueprint, request, jsonify, send_from_directory
import os
from services.video_ops_service import process_video_background

video_ops_bp = Blueprint("video_ops_bp", __name__)

INCOMING_FOLDER = "incoming"
PROCESSED_FOLDER = "processed"
PREDEFINED_BG_FOLDER = os.path.join("static", "images", "backgrounds")  # you can change this


@video_ops_bp.route("/api/video-ops/process", methods=["POST"])
def process_video_ops():
    try:
        os.makedirs(INCOMING_FOLDER, exist_ok=True)
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)

        video_file = request.files.get("video_file")
        threshold = float(request.form.get("threshold", 0.5))
        background_color = request.form.get("background_color")
        background_image = request.files.get("background_image")
        background_video = request.files.get("background_video")
        predefined_bg_image = request.form.get("predefined_bg_image")
        predefined_bg_video = request.form.get("predefined_bg_video")
        remove_voice = request.form.get("remove_voice") == "true"

        if not video_file:
            return jsonify({"error": "No video file provided"}), 400

        input_path = os.path.join(INCOMING_FOLDER, video_file.filename)
        video_file.save(input_path)

        bg_source = None

        if background_color:
            bg_source = {"type": "color", "value": background_color}

        elif background_image:
            bg_path = os.path.join(INCOMING_FOLDER, background_image.filename)
            background_image.save(bg_path)
            bg_source = {"type": "image", "value": bg_path}

        elif background_video:
            bg_path = os.path.join(INCOMING_FOLDER, background_video.filename)
            background_video.save(bg_path)
            bg_source = {"type": "video", "value": bg_path}

        elif predefined_bg_image:
            bg_source = {
                "type": "image",
                "value": os.path.join(PREDEFINED_BG_FOLDER, predefined_bg_image),
            }

        elif predefined_bg_video:
            bg_source = {
                "type": "video",
                "value": os.path.join(PREDEFINED_BG_FOLDER, predefined_bg_video),
            }

        output_file = process_video_background(
            input_path=input_path,
            bg_source=bg_source,
            threshold=threshold,
            output_folder=PROCESSED_FOLDER,
            remove_voice=remove_voice,
        )

        return jsonify({
            "status": "done",
            "file": output_file,
            "download_url": f"/download-file/{output_file}",
        })

    except Exception as e:
        print("VIDEO BG ERROR:", e)
        return jsonify({"error": str(e)}), 500
