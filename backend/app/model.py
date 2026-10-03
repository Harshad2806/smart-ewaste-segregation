"""
Model loading and inference for the e-waste classifier.

The YOLO classification model is loaded once and reused across requests.
"""

import logging
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

logger = logging.getLogger(__name__)

# Resolve the models directory relative to *this* file's location.
# backend/app/model.py → backend/models/
_MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
_CLASSIFIER_PATH = _MODELS_DIR / "ewaste_classifier.pt"


class EWasteClassifier:
    """Thin wrapper around the YOLO classification model."""

    def __init__(self) -> None:
        self._model: YOLO | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load the model weights from disk (call once at startup)."""
        if not _CLASSIFIER_PATH.exists():
            raise FileNotFoundError(
                f"Classifier weights not found at {_CLASSIFIER_PATH}"
            )
        logger.info("Loading e-waste classifier from %s …", _CLASSIFIER_PATH)
        self._model = YOLO(str(_CLASSIFIER_PATH))
        logger.info("Classifier loaded. Classes: %s", self._model.names)

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, image_bytes: bytes) -> tuple[str, float]:
        """
        Run classification on raw image bytes.

        Returns
        -------
        (predicted_class, confidence)
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load() first.")

        # Decode the uploaded bytes into an OpenCV BGR image.
        np_arr = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Could not decode the uploaded file as an image.")

        # Run inference (mirrors the opencv_test.py pipeline exactly).
        result = self._model.predict(source=image, verbose=False)[0]

        class_id = int(result.probs.top1)
        confidence = float(result.probs.top1conf)
        predicted_class = result.names[class_id]

        return predicted_class, confidence


# Module-level singleton – imported by main.py and shared across the app.
classifier = EWasteClassifier()
