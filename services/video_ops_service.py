import os
import uuid
import cv2
import mediapipe as mp
from mediapipe.tasks.python.vision import ImageSegmenter
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import RunningMode
import numpy as np
import subprocess
import urllib.request


def process_video_background(
    input_path: str,
    bg_source: dict | None,
    threshold: float,
    output_folder: str,
    remove_voice: bool = False,
) -> str:
    os.makedirs(output_folder, exist_ok=True)

    model_path = os.path.join(output_folder, 'selfie_segmenter.tflite')
    if not os.path.exists(model_path):
        url = 'https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite'
        urllib.request.urlretrieve(url, model_path)

    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    temp_video = os.path.join(output_folder, f"temp_{uuid.uuid4().hex[:8]}.avi")
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

    # Prepare background
    bg_frame = None
    bg_video_cap = None

    if bg_source:
        if bg_source["type"] == "color":
            color = bg_source["value"].lstrip("#")
            r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            bg_frame = np.full((height, width, 3), (b, g, r), dtype=np.uint8)

        elif bg_source["type"] == "image":
            img = cv2.imread(bg_source["value"])
            bg_frame = cv2.resize(img, (width, height))

        elif bg_source["type"] == "video":
            bg_video_cap = cv2.VideoCapture(bg_source["value"])

    options = ImageSegmenter.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=RunningMode.IMAGE
    )

    with ImageSegmenter.create_from_options(options) as segmenter:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = segmenter.segment(mp_image)
            mask = result.confidence_masks[0].numpy_view()
            mask = (mask > threshold).astype(np.uint8)

            if bg_video_cap:
                ret2, bg = bg_video_cap.read()
                if not ret2:
                    bg_video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret2, bg = bg_video_cap.read()
                bg = cv2.resize(bg, (width, height))
            else:
                bg = bg_frame if bg_frame is not None else np.zeros_like(frame)

            blended = frame * mask[:, :, None] + bg * (1 - mask[:, :, None])
            blended = blended.astype(np.uint8)

            writer.write(blended)

    cap.release()
    writer.release()
    if bg_video_cap:
        bg_video_cap.release()

    # Final MP4 output
    output_name = f"bg_removed_{uuid.uuid4().hex[:8]}.mp4"
    output_path = os.path.join(output_folder, output_name)

    # Build ffmpeg command depending on remove_voice
    if remove_voice:
        # video only, no audio
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_video,
            "-c:v", "libx264",
            "-preset", "fast",
            "-an",
            output_path,
        ]
    else:
        # keep audio from original
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_video,
            "-i", input_path,
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            "-shortest",
            output_path,
        ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(temp_video)

    return output_name
