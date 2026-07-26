# AI-Powered Crop Disease Detection and Recommendation System
## Full Implementation Prompt (React + Flask + Real Trained Model — No Mocks)

Paste the boxed prompt below directly into Replit AI. It specifies a real, runnable
training script (not a placeholder), the Flask API, the database, and the React
frontend. The only thing Replit AI cannot do for you is guarantee high accuracy —
CPU training on a small dataset will be slower and less accurate than the GPU/Colab
training your Chapter 3 describes — but every piece will be genuinely functional,
with no fake or mocked data anywhere.

---

## Before you paste the prompt: one unavoidable fact

Training on Replit's free CPU tier will take real time — realistically 30–90 minutes
for a small fine-tuning run, depending on dataset size. This is not a limitation of
the prompt; it's a limitation of not having a GPU. If you want the same accuracy your
Chapter 3 describes (trained on the full ~42,000-image dataset), you still need to
run the full training in Google Colab with a GPU and drop the resulting `model.h5`
into the Replit project afterward — the prompt below builds you a system that works
correctly with either your CPU-trained small model or a Colab-trained full model,
without changing any code.

---

## THE PROMPT

```
Build a full-stack web application called "AI-Powered Crop Disease Detection and Recommendation System" with this exact architecture: React frontend, Flask REST API backend, MobileNetV2 model via TensorFlow/Keras, SQLite database.

PART 1 — DATA AND MODEL TRAINING (must be real, not mocked):

Create a script train_model.py that:
1. Downloads a small labeled subset of the PlantVillage dataset directly from a public source (e.g. the "plantvillage-dataset" on Kaggle via kagglehub, or the public GitHub mirror at github.com/spMohanty/PlantVillage-Dataset if Kaggle credentials aren't available). If neither is reachable in this environment, fall back to downloading a smaller labeled leaf-disease dataset that is genuinely public and directly downloadable without authentication, and clearly print which source was used.
2. Limits the training run to a manageable size for CPU training: a maximum of 4 crop classes (tomato, maize, cassava, potato) with up to ~300 images per class, split 80/20 train/validation.
3. Loads MobileNetV2 pretrained on ImageNet (include_top=False), freezes the base layers, and adds a classification head: GlobalAveragePooling2D -> Dropout(0.3) -> Dense(num_classes, activation='softmax').
4. Compiles with the Adam optimizer and categorical cross-entropy loss, trains for a small number of epochs (5-10) with early stopping, and prints training/validation accuracy after each epoch so progress is visible.
5. Saves the trained model as model.h5 and saves the class label mapping as labels.json.
6. This must be a real, runnable training script — no synthetic data, no hardcoded fake weights, no placeholder logic pretending to be training.

Print a clear final message stating the achieved validation accuracy and reminding the user that this is a small CPU-trained model suitable for demonstrating the working pipeline, and that a full GPU-trained model (per their Chapter 3 methodology) will perform better.

PART 2 — FLASK BACKEND:

- POST /api/predict — accepts a multipart image upload and an optional crop_type field
  - Validates JPEG/PNG, max 5MB
  - Preprocesses: resize to 224x224, convert to RGB array, normalize to [0,1]
  - Loads model.h5 and labels.json (if they don't exist yet because train_model.py hasn't been run, return a clear JSON error telling the user to run train_model.py first — do not silently fall back to fake predictions)
  - Runs inference, gets top class and confidence
  - If confidence >= 65%: query SQLite for the matching disease record and its recommendations, return full diagnosis + recommendations JSON
  - If confidence < 65%: return a JSON response indicating the result is uncertain, advising the user to consult an agricultural expert, with no recommendations
  - Logs every prediction (disease_id, confidence, timestamp) to the image_logs table
- GET /api/health — returns { "status": "ok", "model_loaded": true/false }
- Enable CORS for the React frontend's origin

SQLite schema (diseases.db), created by a setup script:
- diseases(disease_id INTEGER PRIMARY KEY AUTOINCREMENT, disease_name TEXT, crop_type TEXT, description TEXT, symptoms TEXT)
- recommendations(recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT, disease_id INTEGER REFERENCES diseases(disease_id), category TEXT CHECK(category IN ('chemical','biological','cultural','preventive')), recommendation_text TEXT)
- image_logs(image_id INTEGER PRIMARY KEY AUTOINCREMENT, predicted_disease_id INTEGER, confidence REAL, timestamp TEXT)

Seed script (seed_db.py) populating diseases/recommendations for:
- Tomato: early blight, late blight, leaf mould, bacterial spot, healthy
- Maize: common rust, northern leaf blight, grey leaf spot, healthy
- Cassava: cassava mosaic disease, cassava brown streak, healthy
- Potato: early blight, late blight, healthy
Each non-healthy disease needs at least one realistic, plain-language recommendation per category (chemical, biological, cultural, preventive), written for smallholder farmers.

The seed_db.py class names must exactly match the class names produced by train_model.py's labels.json, so predictions map correctly to database records.

PART 3 — REACT FRONTEND (Vite):

- Upload view: file input, optional crop-type dropdown (Tomato/Maize/Cassava/Potato/Any), submit button, loading spinner while waiting on the API
- Results view: disease name, crop, confidence percentage, plain-language description, four labeled recommendation sections (chemical/biological/cultural/preventive). Show a positive message if "healthy." Show a cautionary "consult an expert" message with no recommendations if confidence was below threshold.
- If the API returns the "model not trained yet" error, show a clear message in the UI telling the developer to run train_model.py first — don't show a fake result.
- axios for API calls, clean mobile-friendly layout, plain language throughout

PART 4 — DOCUMENTATION:

- README.md explaining, in order: (1) how to run train_model.py and roughly how long it will take, (2) how to run seed_db.py, (3) how to start the Flask backend, (4) how to start the React frontend, (5) how to replace model.h5 with a properly GPU-trained model from Google Colab later, keeping the same labels.json class ordering
- Comment the code clearly throughout, since a final-year student needs to explain this system during their project defense
- Do not use localStorage or sessionStorage anywhere
- Organize code into separate files: routes, model/preprocessing logic, database logic, training script — do not put everything in one file
```

---

## What to do after Replit AI finishes

1. **Run `train_model.py` first, before anything else.** Watch it actually download data and print per-epoch accuracy. If it errors out on the dataset download (rate limits, auth walls are common), tell Replit AI the specific error message and ask it to switch to a different public dataset source — don't let it quietly swap in fake data to "fix" the error.
2. **Test `/api/predict` directly** (curl or Postman) with a real leaf photo before touching the frontend, so you know the model and database are wired correctly on their own.
3. **Only then** wire up and test the React frontend end-to-end.
4. **Afterward, if you want real accuracy for your defense**, run the full training in Google Colab per your Chapter 3 methodology (full ~42,000-image dataset, GPU, 30 epochs) and swap in that `model.h5` — no other code changes needed as long as `labels.json` class names stay the same.
5. **Be ready to explain**, in your own words: what MobileNetV2 does, why transfer learning was used instead of training from scratch, what the 65% confidence threshold means, and how the recommendation lookup works. These are the most likely defense questions regardless of who wrote the code.
