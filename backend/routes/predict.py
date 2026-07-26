"""
POST /api/predict

Accepts a multipart/form-data upload with:
  - image  (required) — JPEG or PNG, max 5 MB
  - crop_type (optional) — hint for the user; not used in inference

Returns one of three JSON shapes:
  1. model_not_trained  (503) — run train_model.py first
  2. diagnosed          (200) — confident prediction with disease + recommendations
  3. uncertain          (200) — confidence below threshold; advise expert
"""

from flask import Blueprint, request, jsonify
from model.inference import get_prediction, is_model_loaded
from database.queries import get_disease_by_name, log_prediction

predict_bp = Blueprint("predict", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_BYTES = 5 * 1024 * 1024          # 5 MB
CONFIDENCE_THRESHOLD = 0.65               # 65 %


def _allowed(filename: str) -> bool:
    """Return True if the file extension is JPEG or PNG."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@predict_bp.route("/predict", methods=["POST"])
def predict():
    # ── 1. Guard: model must be trained ────────────────────────────────────
    if not is_model_loaded():
        return jsonify({
            "error": "model_not_trained",
            "message": (
                "The AI model has not been trained yet. "
                "Please run  python backend/train_model.py  first, "
                "then restart the server."
            ),
        }), 503

    # ── 2. Validate upload ──────────────────────────────────────────────────
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]

    if not file.filename:
        return jsonify({"error": "No file selected."}), 400

    if not _allowed(file.filename):
        return jsonify({"error": "Only JPEG and PNG images are supported."}), 400

    image_bytes = file.read()
    if len(image_bytes) > MAX_FILE_BYTES:
        return jsonify({"error": "File size exceeds the 5 MB limit."}), 400

    # ── 3. Run inference ────────────────────────────────────────────────────
    result = get_prediction(image_bytes)
    if result is None:
        return jsonify({"error": "Image processing failed. Please try again."}), 500

    predicted_class, confidence = result

    # Log every prediction regardless of confidence
    log_prediction(predicted_class, confidence)

    confidence_pct = round(confidence * 100, 1)

    # ── 4a. Low confidence — advise expert ──────────────────────────────────
    if confidence < CONFIDENCE_THRESHOLD:
        return jsonify({
            "status": "uncertain",
            "predicted_class": predicted_class,
            "confidence": confidence_pct,
            "message": (
                f"The model is not confident enough to make a reliable diagnosis "
                f"(confidence: {confidence_pct}%). "
                "Please consult a local agricultural extension officer or expert."
            ),
        })

    # ── 4b. Confident — look up disease record ──────────────────────────────
    disease = get_disease_by_name(predicted_class)
    if disease is None:
        return jsonify({
            "status": "uncertain",
            "predicted_class": predicted_class,
            "confidence": confidence_pct,
            "message": (
                f"Detected '{predicted_class}' but no database record was found. "
                "Please run  python backend/seed_db.py  to populate the database, "
                "then try again."
            ),
        })

    return jsonify({
        "status": "diagnosed",
        "disease_id": disease["disease_id"],
        "disease_name": disease["disease_name"],
        "crop_type": disease["crop_type"],
        "confidence": confidence_pct,
        "description": disease["description"],
        "symptoms": disease["symptoms"],
        "is_healthy": "healthy" in disease["disease_name"].lower(),
        "recommendations": disease["recommendations"],
    })
