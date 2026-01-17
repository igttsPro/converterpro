# utils/file_utils.py

import os
import uuid
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS

def save_uploaded_files(files, upload_dir):
    """Save uploaded files to disk and return their names"""
    os.makedirs(upload_dir, exist_ok=True)
    filenames = []
    
    for file in files:
        if not file or not file.filename:
            continue
            
        # Validate file extension
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            continue
        
        # Generate unique filename to avoid duplicates
        original_name = file.filename
        unique_id = str(uuid.uuid4())[:8]  # Short unique ID
        name_part, ext_part = os.path.splitext(original_name)
        unique_filename = f"{name_part}_{unique_id}{ext_part}"
        
        # Save file with unique name
        save_path = os.path.join(upload_dir, unique_filename)
        file.save(save_path)
        
        # Verify file was saved
        if os.path.exists(save_path):
            filenames.append(unique_filename)
            print(f"Saved: {original_name} as {unique_filename}")
    
    return filenames
