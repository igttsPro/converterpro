import yt_dlp
import os
import uuid
import time  # Add this import for retry logic

def extract_video_info(url):
    """Extract metadata + useful formats only."""
    
    # Universal ydl_opts that work for most sites
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "socket_timeout": 30,
        
        # Add HTTP headers to avoid 403 Forbidden errors
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        },
    }
    
    # Only add YouTube-specific settings for YouTube URLs
    if "youtube.com" in url or "youtu.be" in url:
        ydl_opts["extractor_args"] = {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["webpage"]
            }
        }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    title = info.get("title")
    thumbnail = info.get("thumbnail")
    formats = info.get("formats", [])

    useful_formats = []

    for f in formats:
        # Skip video-only or audio-only DASH fragments
        if f.get("acodec") == "none" and f.get("vcodec") != "none":
            continue  # video-only (needs merging)
        if f.get("vcodec") == "none" and f.get("acodec") != "none":
            # audio-only (allowed)
            pass

        ext = f.get("ext")
        if ext not in ["mp4", "webm", "m4a", "mp3", "m4v", "flv"]:
            continue

        resolution = f.get("height") or "Audio"
        filesize = f.get("filesize") or f.get("filesize_approx")
        
        # NEW: Format file size for display
        if filesize:
            if filesize < 1024:
                size_str = f"{filesize} B"
            elif filesize < 1024 * 1024:
                size_str = f"{filesize / 1024:.1f} KB"
            elif filesize < 1024 * 1024 * 1024:
                size_str = f"{filesize / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{filesize / (1024 * 1024 * 1024):.1f} GB"
        else:
            size_str = "Unknown size"

        # Format description for display
        format_note = f.get("format_note", "")
        display_resolution = f"{resolution}p" if resolution != "Audio" else "Audio"
        
        if format_note:
            display_resolution = f"{display_resolution} ({format_note})"

        useful_formats.append({
            "format_id": f.get("format_id"),
            "ext": ext,
            "resolution": resolution,  # Keep original for sorting
            "display_resolution": display_resolution,  # For display
            "filesize": filesize,  # Original size in bytes
            "size_str": size_str,  # NEW: Formatted size string
            "format_note": format_note,
        })

    # Sort by resolution (highest first)
    useful_formats.sort(key=lambda x: (
        0 if x["resolution"] == "Audio" 
        else int(str(x["resolution"]).split('p')[0]) 
        if 'p' in str(x["resolution"]) 
        else 0
    ), reverse=True)

    return {
        "title": title,
        "thumbnail": thumbnail,
        "formats": useful_formats
    }



def download_selected_format(url, format_id, output_folder):
    """Download the selected format."""
    os.makedirs(output_folder, exist_ok=True)

    unique_name = f"download_{uuid.uuid4().hex[:8]}.mp4"
    output_path = os.path.join(output_folder, unique_name)

    # Universal download options
    ydl_opts = {
        "format": format_id,
        "outtmpl": output_path,
        "quiet": True,
        
        # HTTP headers to prevent 403 Forbidden
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        },
        
        # Retry logic
        "retries": 3,
        "fragment_retries": 3,
        "ignoreerrors": True,
        "no_warnings": True,
        "socket_timeout": 30,
    }
    
    # Only add YouTube-specific settings for YouTube URLs
    if "youtube.com" in url or "youtu.be" in url:
        ydl_opts.update({
            "merge_output_format": "mp4",
            "postprocessors": [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"],
                    "player_skip": ["webpage", "js"]
                }
            }
        })
    else:
        # For non-YouTube sites, use simpler approach
        ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Check if file was actually downloaded
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception("Downloaded file is empty or doesn't exist")
        
        return unique_name
    except Exception as e:
        # Clean up empty file if it exists
        if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
            os.remove(output_path)
        raise e