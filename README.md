# AI-Powered Crop Disease Detection and Recommendation System

A full-stack web application that uses a MobileNetV2 deep learning model to identify
crop diseases from leaf photographs and provide plain-language recommendations for
smallholder farmers.

**Stack:** React (Vite) frontend · Flask REST API · TensorFlow/Keras (MobileNetV2) ·
SQLite database

---

## Quick-start guide

Follow these steps in order. Each must complete before the next.

### 1 — Train the model (30–90 minutes on CPU)

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run the training script
python backend/train_model.py
```

The script will:
- Download a small PlantVillage subset via TensorFlow Datasets (no credentials needed)
- Fine-tune MobileNetV2 on up to 300 images per class for Tomato, Corn, and Potato
- Print per-epoch training and validation accuracy
- Save `backend/model.h5` and `backend/labels.json`

A final message will show the achieved validation accuracy and a reminder that this
is a CPU-trained demonstration model.

### 2 — Seed the disease database

```bash
python backend/seed_db.py
```

This populates the SQLite database (`backend/diseases.db`) with disease descriptions
and plain-language recommendations in four categories: chemical, biological, cultural,
and preventive. The script is idempotent — safe to run multiple times.

> **Important:** The database must exist before running this script. Start the Flask
> server at least once first (step 3), then run the seed script.

### 3 — Start the Flask backend

In the Replit workspace the API server workflow starts automatically. To start it
manually:

```bash
cd backend
python app.py
```

The server listens on the PORT set by the Replit workflow config (default 8080) and
serves all routes under `/api`.

Check the server is up:
```
curl localhost:80/api/health
# → {"model_loaded": true, "status": "ok"}
```

### 4 — Start the React frontend

In the Replit workspace the frontend workflow starts automatically. To verify it is
working, select the **Crop Disease Detection** artifact in the preview dropdown.

To build the frontend manually:
```bash
pnpm --filter @workspace/crop-disease-app run dev
```

### 5 — End-to-end test

Test the prediction API directly before using the UI:
```bash
curl -X POST http://localhost:80/api/predict \
  -F "image=@/path/to/leaf.jpg" \
  -F "crop_type=Tomato"
```

A successful response will include `disease_name`, `confidence`, `description`,
`symptoms`, and `recommendations` grouped by category.

---

## Replacing the model with a GPU-trained version

1. Train the full PlantVillage dataset (~42,000 images) in Google Colab with a GPU
   for 30 epochs following your Chapter 3 methodology.
2. Download the resulting `model.h5` and `labels.json` from Colab.
3. Replace `backend/model.h5` and `backend/labels.json` in this project.
4. Restart the Flask server — no other code changes are needed.

> **Keep the same class ordering in `labels.json`.** The model output index must
> map to the same class name as during training. If you add or reorder classes,
> also re-run `seed_db.py` to update the database disease names.

---

## Confidence threshold

The API uses a 65% confidence threshold. Below that, the response advises the user
to consult an agricultural expert and does not return recommendations. This threshold
is set in `backend/routes/predict.py` (`CONFIDENCE_THRESHOLD = 0.65`) and can be
adjusted.

---

## Likely project-defence questions

- **What does MobileNetV2 do?** — A lightweight convolutional neural network
  pre-trained on 1.2 million ImageNet images that acts as a feature extractor.
- **Why transfer learning?** — Training from scratch requires millions of labelled
  images and weeks of GPU time. Transfer learning reuses low-level visual features
  already learned on ImageNet and only trains the final classification head on your
  smaller dataset.
- **What does the 65% threshold mean?** — The softmax output of the model gives
  probabilities for each class. If the top class probability is below 65%, the model
  is not confident enough for a reliable diagnosis and the system advises expert
  consultation instead of showing potentially wrong recommendations.
- **How does the recommendation lookup work?** — The predicted class name is matched
  against the `disease_name` column in the SQLite database. The Flask API then fetches
  all recommendations for that disease and returns them grouped by category.
