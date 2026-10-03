"""
FastAPI application for the Smart E-Waste Segregation System.

Endpoints
---------
GET  /health   – readiness check
POST /predict  – classify an uploaded e-waste image
"""

import logging
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.decision_engine import is_confident
from app.intelligence_engine import intelligence
from app.model import classifier
from app.schemas import (
    ErrorResponse,
    HealthResponse,
    IntelligenceAssessment,
    PredictionResponse,
    VisionResult,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Accepted MIME types for image uploads.
_ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
}


# ------------------------------------------------------------------
# Application lifespan (startup / shutdown)
# ------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the classifier model and intelligence engine once at startup."""
    classifier.load()
    intelligence.load()
    logger.info("Application startup complete.")
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title="Smart E-Waste Segregation System",
    description="AI-powered e-waste classification and recycling stream recommendation API.",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
)
async def health():
    """Return service health and model readiness status."""
    return HealthResponse(
        status="ok",
        model_loaded=classifier.is_loaded,
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid upload"},
        500: {"model": ErrorResponse, "description": "Inference failure"},
    },
    summary="Classify an e-waste image",
)
async def predict(file: UploadFile = File(..., description="Image file to classify")):
    """
    Accept an uploaded image, run the e-waste classifier, and return the
    vision result together with an intelligence-engine recovery assessment.
    """

    # --- Validate content type -------------------------------------------
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                f"Accepted types: {', '.join(sorted(_ALLOWED_CONTENT_TYPES))}"
            ),
        )

    # --- Read image bytes ------------------------------------------------
    try:
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    finally:
        await file.close()

    # --- Run inference ---------------------------------------------------
    try:
        predicted_class, confidence = classifier.predict(image_bytes)
    except ValueError as exc:
        # Could not decode image (corrupt / wrong format).
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Inference failed")
        raise HTTPException(status_code=500, detail=f"Inference error: {exc}")

    # --- Vision result ---------------------------------------------------
    vision = VisionResult(
        predicted_class=predicted_class,
        confidence=round(confidence, 4),
        is_confident=is_confident(confidence),
    )

    # --- Intelligence assessment -----------------------------------------
    assessment_raw = await intelligence.assess_async(predicted_class, confidence)
    assessment = IntelligenceAssessment(**assessment_raw)

    return PredictionResponse(
        success=True,
        vision=vision,
        intelligence=assessment,
    )


# ------------------------------------------------------------------
# Global exception handler for unexpected errors
# ------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Internal server error.").model_dump(),
    )
