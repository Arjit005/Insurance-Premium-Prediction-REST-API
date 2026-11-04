import hashlib
import logging
import pickle
from pathlib import Path
from typing import Any, Dict

import pandas as pd

logger = logging.getLogger("insurance_api.model")

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "model.pkl"
CHECKSUM_PATH = MODEL_DIR / "model.sha256"
MODEL_VERSION = "1.0.0"


def _verify_model_integrity(model_path: Path, checksum_path: Path) -> None:
    """Verifies that the model artifact matches the known SHA-256 hash.

    Guards against corrupted or tampered pickled models before deserialization.
    """
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}")

    if checksum_path.exists():
        expected_hash = checksum_path.read_text(encoding="utf-8").strip().lower()
        hasher = hashlib.sha256()
        with model_path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        actual_hash = hasher.hexdigest().lower()

        if actual_hash != expected_hash:
            raise ValueError(
                f"Security alert: Model checksum mismatch! "
                f"Expected {expected_hash}, got {actual_hash}"
            )
        logger.info("Model integrity verified successfully via SHA-256.")


# Verify and load model artifact safely
_verify_model_integrity(MODEL_PATH, CHECKSUM_PATH)
with MODEL_PATH.open("rb") as f:
    model = pickle.load(f)

# Extract class labels for probability mapping
class_labels = model.classes_.tolist()


def predict_output(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """Runs model inference on engineered input features.

    Returns:
        dict: predicted_category, confidence (float), class_probabilities (dict)
    """
    input_df = pd.DataFrame([user_input])
    predicted_class = str(model.predict(input_df)[0])

    probabilities = model.predict_proba(input_df)[0]
    confidence = float(max(probabilities))

    class_probs = {
        label: round(float(prob), 4)
        for label, prob in zip(class_labels, probabilities)
    }

    return {
        "predicted_category": predicted_class,
        "confidence": round(confidence, 4),
        "class_probabilities": class_probs,
    }
