import logging
import time
import uuid
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ML_model.predict import MODEL_VERSION, predict_output
from schema.prediction_response import PredictionResponse
from schema.user_input import UserInput

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("insurance_api")

app = FastAPI(
    title="Insurance Premium Prediction REST API",
    description="Machine Learning REST API predicting applicant insurance premium risk categories with confidence metrics.",
    version=MODEL_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_observability_middleware(request: Request, call_next):
    """Observability middleware to track latency, generate request IDs, and log transactions."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response: Response = await call_next(request)

    process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(process_time_ms)

    logger.info(
        f"request_id={request_id} method={request.method} path={request.url.path} "
        f"status={response.status_code} latency_ms={process_time_ms}"
    )
    return response


@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {
        "service": "Insurance Premium Prediction API",
        "status": "healthy",
        "model_version": MODEL_VERSION,
        "docs": "/docs",
    }


@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=200,
    summary="Predict Insurance Premium Category",
    description="Validates applicant details, performs automatic feature engineering, and returns risk category with confidence scores.",
)
def predict_premium(data: UserInput, request: Request):
    user_features: Dict[str, Any] = {
        "bmi": data.bmi,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupation": data.occupation,
    }

    req_id = getattr(request.state, "request_id", "unknown")

    try:
        prediction = predict_output(user_features)
        logger.info(
            f"request_id={req_id} inference_success=true "
            f"category={prediction['predicted_category']} confidence={prediction['confidence']}"
        )
        return prediction
    except Exception as e:
        logger.error(
            f"request_id={req_id} inference_error={str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Inference execution failed. Please verify input parameters or contact support.",
        )
