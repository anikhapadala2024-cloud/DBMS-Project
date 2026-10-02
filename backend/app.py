import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.database import init_db, db
from backend.routes import (
    auth_bp,
    farmer_bp,
    field_bp,
    crop_bp,
    batch_bp,
    activity_bp,
    analytics_bp,
    user_bp,
    assistant_bp,
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

def create_app():
    """Application factory for AgriTech portal."""
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
    app.config.from_object(Config)

    # Enable CORS for all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize Database (MySQL or fallback)
    db_engine = init_db(app)
    app.config["ACTIVE_DB_ENGINE"] = db_engine

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(farmer_bp)
    app.register_blueprint(field_bp)
    app.register_blueprint(crop_bp)
    app.register_blueprint(batch_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(assistant_bp)

    # System Health API
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "online",
            "service": "AgriTech Backend API",
            "database_engine": app.config.get("ACTIVE_DB_ENGINE", "unknown"),
            "version": "1.0.0"
        })

    # Serve Frontend Single-Page and Static Assets
    @app.route("/", methods=["GET"])
    def serve_root():
        if (FRONTEND_DIR / "dashboard.html").exists():
            return send_from_directory(str(FRONTEND_DIR), "index.html")
        return "AgriTech Backend Running"

    @app.route("/<path:path>", methods=["GET"])
    def serve_frontend_files(path):
        if (FRONTEND_DIR / path).exists():
            return send_from_directory(str(FRONTEND_DIR), path)
        return jsonify({"error": "Resource not found", "path": path}), 404

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "API endpoint or file not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({"success": False, "message": "An internal server error occurred"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    print("=" * 65)
    print("🌱 AgriTech – Crop Batch Management & Analytics Portal")
    print(f"🚀 Server running at: http://127.0.0.1:{port}")
    print(f"📦 Database Engine: {app.config.get('ACTIVE_DB_ENGINE')}")
    print("=" * 65)
    app.run(host="0.0.0.0", port=port, debug=True)
