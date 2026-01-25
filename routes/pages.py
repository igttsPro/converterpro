# routes/pages.py

from flask import Blueprint, send_from_directory
import os
from config import STATIC_DIR

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    """Serve the main index.html page"""
    return send_from_directory(os.path.join(STATIC_DIR, 'pages'), 'index.html')

# You can add more page routes here
@pages_bp.route('/split')
def split_page():
     return send_from_directory(os.path.join(STATIC_DIR, 'pages'), 'split.html')

@pages_bp.route('/download')
def download_page():
     return send_from_directory(os.path.join(STATIC_DIR, 'pages'), 'download.html')

@pages_bp.route("/ida")
@pages_bp.route("/remove-bg")
@pages_bp.route("/video-ops")
@pages_bp.route("/video_ops")
def video_ops_page():
     return send_from_directory(os.path.join(STATIC_DIR, 'pages'), "video_ops.html")


# @pages_bp.route("/chat")
# def chat_page(): 
#      return send_from_directory(PAGES_DIR, "chatbot.html") 
     
     