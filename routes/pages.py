# routes/pages.py

from flask import Blueprint, send_from_directory
import os
from config import STATIC_DIR

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    """Serve the main index.html page"""
    return send_from_directory(os.path.join(STATIC_DIR, 'pages'), 'index.html')

# You can add more page routes here later
@pages_bp.route('/split')
def split_page():
     return send_from_directory(os.path.join(STATIC_DIR, 'pages'), 'split.html')