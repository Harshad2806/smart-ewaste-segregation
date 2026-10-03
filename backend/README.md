# Smart E-Waste Segregation System — Backend

AI-powered FastAPI backend for classifying e-waste images and recommending recycling streams.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, endpoints, lifespan
│   ├── model.py             # YOLO classifier loading & inference
│   ├── decision_engine.py   # Recycling stream mapping & thresholds
│   └── schemas.py           # Pydantic request/response models
├── models/
│   ├── ewaste_classifier.pt # Primary classifier (5 classes)
│   └── xbat_detector.pt     # Experimental — not used in /predict
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the server

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The model loads automatically at startup. You will see:

```
Classifier loaded. Classes: {0: 'electrical_cables', 1: 'electronic_chips', ...}
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

### 3. Add `--reload` during development

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## API Endpoints

### `GET /health`

Returns service status and model readiness.

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### `POST /predict`

Upload an image to classify. Accepts `image/jpeg`, `image/png`, `image/webp`, `image/bmp`, `image/tiff`.

**Request:** `multipart/form-data` with field `file`.

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -F "file=@photo.jpg"
```

**Response (200):**

```json
{
  "success": true,
  "result": {
    "predicted_class": "laptops",
    "confidence": 0.9213,
    "recycling_stream": "Computer / Electronics Recycling",
    "is_confident": true
  },
  "message": null
}
```

**Error (400):** invalid file type or corrupt image.

### Interactive docs

Visit **http://127.0.0.1:8000/docs** for the auto-generated Swagger UI.

## E-Waste Classes & Recycling Streams

| Class               | Recycling Stream                  |
|---------------------|-----------------------------------|
| `electrical_cables` | Cable / Electronics Recycling     |
| `electronic_chips`  | Electronic Component Recycling    |
| `laptops`           | Computer / Electronics Recycling  |
| `small_appliances`  | Small Appliance Recycling         |
| `smartphones`       | Mobile / Electronics Recycling    |

Predictions below **55% confidence** are flagged with `is_confident: false`.
