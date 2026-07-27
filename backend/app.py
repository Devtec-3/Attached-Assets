
"""
app.py — Flask application factory and entry point.

Reads PORT from the environment (Replit sets this via the workflow config).
All API routes are mounted under /api to match the proxy path in artifact.toml.

Usage (from workspace root):
    python backend/app.py
"""

import os
import sys
import logging

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from flask import Flask
from flask_cors import CORS

from database.setup import init_db
from routes.predict import predict_bp
from routes.health import health_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db()

    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")

    return app


app = create_app()

if __name__ == "__main__":
    raw_port = os.environ.get("PORT", "8080")
    try:
        port = int(raw_port)
    except ValueError:
        logger.error("Invalid PORT value: %r", raw_port)
        sys.exit(1)

    logger.info("Starting Flask server on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=False)
