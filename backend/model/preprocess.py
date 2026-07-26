"""
Image preprocessing utilities for MobileNetV2 inference.

Converts raw image bytes to the 4D float32 array the model expects.
"""

import io
import numpy as np
from PIL import Image

TARGET_SIZE = (224, 224)


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess raw image bytes for MobileNetV2:
      1. Decode using Pillow (supports JPEG and PNG)
      2. Convert to RGB (drops alpha channel if present)
      3. Resize to 224x224 with high-quality Lanczos resampling
      4. Normalise pixel values from [0, 255] to [0.0, 1.0]
      5. Add a batch dimension → shape (1, 224, 224, 3)

    Returns a float32 numpy array ready for model.predict().
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(TARGET_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)  # (1, 224, 224, 3)
