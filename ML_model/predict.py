import pickle
from pathlib import Path

import pandas as pd

# import ml model
with (Path(__file__).resolve().parent / 'model.pkl').open('rb') as f:
    model=pickle.load(f)

# ML flow
MODEL_VERSION='1.0.0'


# Get class labels from model (important for matching probabilities to class names)
class_labels = model.classes_.tolist()

# confidence score
def predict_output(user_input: dict):
    input_df = pd.DataFrame([user_input])# send it in list
    predicted_class=model.predict(input_df)[0]
    # Get probabilities for all classes
    probabilities = model.predict_proba(input_df)[0]
    confidence = max(probabilities)
    
    # Create mapping: {class_name: probability}
    class_probs = dict(zip(class_labels, map(lambda p: round(p, 4), probabilities)))

    return {
        "predicted_category": predicted_class,
        "confidence": round(confidence, 4),
        "class_probabilities": class_probs
    }