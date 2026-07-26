"""
train_model.py — Train a MobileNetV2 crop disease classifier.

What this script does
─────────────────────
1. Downloads a small labelled subset of PlantVillage via TensorFlow Datasets
   (public, no authentication required).  Falls back to images placed manually
   in backend/data/plantvillage/<class_name>/ if TF Datasets is unavailable.
2. Limits training to up to 4 crop types (Tomato, Corn/Maize, Potato, and
   Cassava if present) with at most MAX_IMAGES_PER_CLASS images each.
3. Loads MobileNetV2 (ImageNet weights, frozen base) and trains a custom head:
       GlobalAveragePooling2D → Dropout(0.3) → Dense(num_classes, softmax)
4. Trains for up to EPOCHS epochs with early stopping on val_accuracy.
5. Saves  backend/model.h5  and  backend/labels.json.

Usage
─────
    python backend/train_model.py

Expected time
─────────────
    30–90 minutes on a CPU, depending on dataset size and hardware.
    For better accuracy, train the full dataset (~42,000 images) in Google
    Colab with a GPU and drop the resulting model.h5 here — no code changes
    needed as long as labels.json class ordering stays the same.
"""

import os
import sys
import json
import logging
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH   = os.path.join(SCRIPT_DIR, "model.h5")
LABELS_PATH  = os.path.join(SCRIPT_DIR, "labels.json")
MANUAL_DATA  = os.path.join(SCRIPT_DIR, "data", "plantvillage")
TFDS_CACHE   = os.path.join(SCRIPT_DIR, "data", "tfds_cache")

# ── Hyper-parameters ────────────────────────────────────────────────────────
IMG_SIZE              = (224, 224)
BATCH_SIZE            = 16
MAX_IMAGES_PER_CLASS  = 300
EPOCHS                = 10
VALIDATION_SPLIT      = 0.2

# Crops to include (matched as substrings against lowercase class names)
TARGET_CROPS = {"tomato", "corn", "maize", "potato", "cassava"}


# ── Dataset helpers ─────────────────────────────────────────────────────────

def _load_via_tfds() -> tuple:
    """
    Attempt to download PlantVillage through tensorflow_datasets.
    Returns (ds, all_label_names) on success, (None, None) on failure.
    """
    try:
        import tensorflow_datasets as tfds
        logger.info("Downloading PlantVillage via TensorFlow Datasets…")
        ds, info = tfds.load(
            "plant_village",
            split="train",
            with_info=True,
            as_supervised=True,
            data_dir=TFDS_CACHE,
        )
        logger.info(
            "Source: TensorFlow Datasets (plant_village). "
            "Total classes in dataset: %d",
            info.features["label"].num_classes,
        )
        return ds, info.features["label"].names
    except Exception as exc:
        logger.warning("TensorFlow Datasets download failed: %s", exc)
        return None, None


def _filter_target_classes(all_names: list) -> list:
    """Keep only class names that belong to one of the target crops."""
    kept = []
    for name in all_names:
        name_lower = name.lower()
        if any(crop in name_lower for crop in TARGET_CROPS):
            kept.append(name)
    logger.info(
        "Using %d classes out of %d total (target crops only).",
        len(kept), len(all_names),
    )
    return kept


def _collect_from_tfds(ds, all_names: list, target_names: list):
    """
    Iterate through a tfds dataset and collect up to MAX_IMAGES_PER_CLASS
    images for each target class.

    Returns (X: ndarray, y: ndarray, class_names: list[str]).
    """
    import tensorflow as tf

    name_to_old_idx = {n: i for i, n in enumerate(all_names)}
    target_old_idxs = {name_to_old_idx[n] for n in target_names if n in name_to_old_idx}
    sorted_old_idxs = sorted(target_old_idxs)
    old_to_new       = {old: new for new, old in enumerate(sorted_old_idxs)}
    class_names      = [all_names[i] for i in sorted_old_idxs]

    counts = {i: 0 for i in sorted_old_idxs}
    X, y = [], []

    logger.info("Collecting images (up to %d per class)…", MAX_IMAGES_PER_CLASS)
    for image, label in ds:
        old_idx = int(label.numpy())
        if old_idx not in target_old_idxs:
            continue
        if counts[old_idx] >= MAX_IMAGES_PER_CLASS:
            continue

        img = tf.image.resize(image, IMG_SIZE).numpy().astype(np.float32) / 255.0
        X.append(img)
        y.append(old_to_new[old_idx])
        counts[old_idx] += 1

        total = sum(counts.values())
        if total % 200 == 0:
            logger.info("  Collected %d images so far…", total)

        if all(c >= MAX_IMAGES_PER_CLASS for c in counts.values()):
            break

    logger.info("Dataset ready: %d images across %d classes.", len(X), len(class_names))
    return np.array(X), np.array(y), class_names


def _collect_from_directory() -> tuple:
    """
    Load images from MANUAL_DATA/<class_name>/ directories.
    Expects the user to have placed PlantVillage images there manually.
    """
    from PIL import Image as PILImage

    if not os.path.isdir(MANUAL_DATA) or not os.listdir(MANUAL_DATA):
        logger.error(
            "No images found in %s.\n"
            "  Option A: Let TensorFlow Datasets download them automatically "
            "(install tensorflow-datasets and re-run).\n"
            "  Option B: Manually download PlantVillage images and place them in\n"
            "            %s/<class_name>/  then re-run.",
            MANUAL_DATA, MANUAL_DATA,
        )
        sys.exit(1)

    all_names   = sorted(d for d in os.listdir(MANUAL_DATA)
                         if os.path.isdir(os.path.join(MANUAL_DATA, d)))
    class_names = _filter_target_classes(all_names)

    X, y = [], []
    for idx, cls in enumerate(class_names):
        cls_dir = os.path.join(MANUAL_DATA, cls)
        files   = [
            f for f in os.listdir(cls_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ][:MAX_IMAGES_PER_CLASS]

        logger.info("  Loading %d images for class '%s'…", len(files), cls)
        for fname in files:
            try:
                img = (
                    PILImage.open(os.path.join(cls_dir, fname))
                    .convert("RGB")
                    .resize(IMG_SIZE, PILImage.LANCZOS)
                )
                X.append(np.array(img, dtype=np.float32) / 255.0)
                y.append(idx)
            except Exception as exc:
                logger.warning("    Skipping %s: %s", fname, exc)

    return np.array(X), np.array(y), class_names


# ── Model builder ────────────────────────────────────────────────────────────

def build_model(num_classes: int):
    """
    MobileNetV2 feature extractor (frozen) + custom classification head.

    Architecture:
        MobileNetV2(include_top=False, weights='imagenet')
        → GlobalAveragePooling2D
        → Dropout(0.3)
        → Dense(num_classes, activation='softmax')
    """
    import tensorflow as tf

    base = tf.keras.applications.MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False   # freeze all base layers (transfer learning)

    model = tf.keras.Sequential([
        base,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(num_classes, activation="softmax"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


# ── Main training routine ────────────────────────────────────────────────────

def train() -> None:
    import tensorflow as tf

    logger.info("=" * 65)
    logger.info("  AI Crop Disease Detection — Model Training")
    logger.info("=" * 65)
    logger.info("  Up to %d images per class, max %d epochs.", MAX_IMAGES_PER_CLASS, EPOCHS)
    logger.info("  Expected time on CPU: 30–90 minutes.")
    logger.info("=" * 65)

    # 1. Load dataset
    ds, all_names = _load_via_tfds()
    if ds is not None:
        target_names    = _filter_target_classes(all_names)
        X, y, class_names = _collect_from_tfds(ds, all_names, target_names)
    else:
        logger.info("Falling back to manual directory: %s", MANUAL_DATA)
        X, y, class_names = _collect_from_directory()

    if len(X) == 0:
        logger.error("No images collected. Aborting.")
        sys.exit(1)

    num_classes = len(class_names)
    logger.info("\nClass summary:")
    for i, name in enumerate(class_names):
        logger.info("  [%d] %s — %d images", i, name, int(np.sum(y == i)))

    # 2. Shuffle and split
    rng     = np.random.default_rng(42)
    perm    = rng.permutation(len(X))
    X, y    = X[perm], y[perm]
    split   = int(len(X) * (1 - VALIDATION_SPLIT))
    X_tr, X_val = X[:split], X[split:]
    y_tr, y_val = y[:split], y[split:]
    logger.info("\nTrain: %d  |  Validation: %d", len(X_tr), len(X_val))

    # 3. Build model
    model = build_model(num_classes)
    model.summary(print_fn=logger.info)

    # 4. Train with early stopping
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=3,
            restore_best_weights=True,
            verbose=1,
        )
    ]

    logger.info("\nStarting training…\n")
    history = model.fit(
        X_tr, y_tr,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    # 5. Save artefacts
    model.save(MODEL_PATH)
    with open(LABELS_PATH, "w") as fh:
        json.dump(class_names, fh, indent=2)

    best_val_acc = max(history.history.get("val_accuracy", [0])) * 100

    logger.info("\n" + "=" * 65)
    logger.info("  Training complete!")
    logger.info("  Model saved   →  %s", MODEL_PATH)
    logger.info("  Labels saved  →  %s", LABELS_PATH)
    logger.info("  Best validation accuracy: %.1f%%", best_val_acc)
    logger.info("")
    logger.info("  NOTE: This is a small CPU-trained model, suitable for")
    logger.info("  demonstrating the working pipeline.")
    logger.info("  For defense-quality accuracy, train the full ~42,000-image")
    logger.info("  PlantVillage dataset in Google Colab with a GPU (30 epochs)")
    logger.info("  and replace backend/model.h5 — no other code changes needed")
    logger.info("  as long as labels.json class ordering stays the same.")
    logger.info("=" * 65)


if __name__ == "__main__":
    train()
