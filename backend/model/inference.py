"""
Model loading and inference.

The Keras model and label list are loaded once at server startup and cached
in module-level variables so every request does not hit the filesystem.
"""

import os
import gc
import json
import logging
import numpy as np

from model.preprocess import preprocess_image

logger = logging.getLogger(__name__)

# Paths — both files live in the backend/ directory
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BACKEND_DIR, "model.h5")
LABELS_PATH = os.path.join(_BACKEND_DIR, "labels.json")

_model = None   # tf.keras.Model loaded at startup
_labels = None  # list[str] mapping class index → class name string


def _load_model() -> bool:
    """
    Attempt to load model.h5 and labels.json from the backend directory.
    Returns True on success, False if either file is missing or load fails.
    Called automatically when this module is first imported.
    """
    global _model, _labels

    if not os.path.exists(MODEL_PATH):
        logger.warning(
            "model.h5 not found at %s — run 'python backend/train_model.py' first.",
            MODEL_PATH,
        )
        return False

    if not os.path.exists(LABELS_PATH):
        logger.warning(
            "labels.json not found at %s — run 'python backend/train_model.py' first.",
            LABELS_PATH,
        )
        return False

    try:
        # Import TensorFlow here so the module can be imported safely even
        # before TF is installed (the pip install runs at startup time).
        import tensorflow as tf  # noqa: F401

        _model = tf.keras.models.load_model(MODEL_PATH)
        with open(LABELS_PATH, "r") as f:
            _labels = json.load(f)  # list of class name strings
        logger.info("Model loaded. Classes: %s", _labels)
        return True

    except Exception as exc:
        logger.error("Failed to load model: %s", exc)
        return False


# Load model on module import (happens once when Flask starts)
_load_model()


def is_model_loaded() -> bool:
    """Return True if both the model and label list are ready for inference."""
    return _model is not None and _labels is not None


def get_prediction(image_bytes: bytes) -> tuple[str, float] | None:
    """
    Preprocess raw image bytes and run a single forward pass.

    Returns:
        (class_name, confidence) tuple where confidence is in [0, 1], or
        None if the model is not loaded or an error occurs during inference.
    """
    if not is_model_loaded():
        return None

    try:
        arr = preprocess_image(image_bytes)          # (1, 224, 224, 3)
        preds = _model.predict(arr, verbose=0)       # (1, num_classes)
        idx = int(np.argmax(preds[0]))
        confidence = float(preds[0][idx])
        gc.collect()
        return _labels[idx], confidence

    except Exception as exc:
        logger.error("Inference error: %s", exc)
        return None
