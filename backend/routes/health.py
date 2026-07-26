"""
Health check endpoints.

GET /api/health   — primary endpoint (spec-compliant)
GET /api/healthz  — alias for backwards compatibility with the api-server config
"""

from flask import Blueprint, jsonify
from model.inference import is_model_loaded

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """Return server health status and whether the AI model is loaded."""
    return jsonify({
        "status": "ok",
        "model_loaded": is_model_loaded(),
    })


@health_bp.route("/healthz", methods=["GET"])
def healthz():
    """Alias kept for backwards compatibility with the api-server health check."""
    return jsonify({
        "status": "ok",
        "model_loaded": is_model_loaded(),
    })
