from flask import Flask
from config import BASE_DIR, UPLOAD_DIR, OUTPUT_DIR, STATIC_DIR
from workers.cleanup_worker import start_cleanup_worker

# Import blueprints
from routes.pages import pages_bp
from routes.compress_video import compress_bp

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Create necessary directories
    import os
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, "pages"), exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(compress_bp)
    
    # Serve static files
    @app.route('/static/<path:path>')
    def serve_static(path):
        return app.send_static_file(path)
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    # Start background cleanup worker
    start_cleanup_worker()
    
    # Start Flask app
    app.run(debug=True, host="0.0.0.0", port=5000)