# 📋 Model Card: Insurance Premium Risk Classifier

An industry-standard Model Card (conforming to the framework proposed by *Mitchell et al.*) documenting the model details, intended usage, performance metrics, ethical considerations, and security constraints.

---

## 1. 🔍 Model Details

* **Model Name**: Insurance Premium Category Predictor
* **Model Version**: `1.0.0`
* **Model Type**: Multi-class Classification
* **Architecture**: Scikit-Learn Pipeline (`ColumnTransformer` OneHotEncoder + `RandomForestClassifier`)
* **Framework**: `scikit-learn==1.6.1`, `pandas>=2.2.0`, `Python 3.11`
* **Artifact Path**: `ML_model/model.pkl`
* **Artifact SHA-256**: `cbd301fa177cd72b74c5bb301423575d59963dff7db25a98292195085ba00459`
* **Owner/Maintainer**: Arjit Katiyar

---

## 2. 🎯 Intended Use

### Primary Use Case
* Real-time risk tier classification (`Low`, `Medium`, `High`) for health and life insurance applicants during preliminary digital onboarding.
* Provides probability vectors and confidence scores to power triage systems.

### Out-of-Scope / Prohibited Uses
* **Automated Denial**: Must **not** be used as an autonomous denial engine without human-underwriter oversight.
* **Underage Applicants**: Strictly restricted to adults aged 18 to 119.
* **Clinical Diagnostic Claims**: The model's computed `bmi` and `lifestyle_risk` are insurance actuarial proxies and must not be interpreted as medical diagnoses.

---

## 3. 🧪 Factors & Feature Engineering

Input features provided by the applicant undergo deterministic transformations via Pydantic (`schema/user_input.py`):

| Raw Input | Validation Boundary | Engineered Feature | Transformation Logic |
| :--- | :--- | :--- | :--- |
| `weight` (kg), `height` (m) | `weight > 0`, `0 < height < 2.5` | `bmi` | $\frac{\text{weight}}{\text{height}^2}$ |
| `smoker` (bool), `bmi` | `smoker in {True, False}` | `lifestyle_risk` | `high` if smoker & BMI > 30; `medium` if smoker or BMI > 27; else `low` |
| `age` (int) | `1 <= age < 120` | `age_group` | `<25: young`, `<45: adult`, `<60: middle_aged`, `else: senior` |
| `city` (str) | Stripped & Title-cased | `city_tier` | Tier 1 (Metros: Mumbai, Delhi, etc.), Tier 2 (State capitals / hubs), Tier 3 (others) |
| `income_lpa` (float) | `> 0` | `income_lpa` | Direct pass-through |
| `occupation` (str) | Fixed Literal enum (7 values) | `occupation` | Categorical encoding via pipeline |

---

## 4. 📊 Performance & Confidence Calibration

* **Classes**: `Low`, `Medium`, `High`
* **Outputs**:
  - `predicted_category`: Argmax class label.
  - `confidence`: Highest class probability (bounded between `0.0` and `1.0`).
  - `class_probabilities`: Probability distribution across all target classes.
* **Human-in-the-Loop Threshold**:
  - If `confidence < 0.60`, the prediction should be flagged for secondary review by a human underwriter.

---

## 5. ⚖️ Ethical Considerations & Fairness

### Proxy Discrimination & Fairness Risks
1. **City Tier & Income**: Geographic location and income level may correlate with socioeconomic status and protected classes.
2. **Age Group**: Age is an actuarial risk factor for health, but must comply with jurisdictional age-discrimination regulations.

### Mitigations
* All API responses return complete class probability distributions, enabling transparent auditing.
* Production deployments should periodically compute **Disparate Impact Ratio (DIR)** across demographic slices to detect unintended bias.

---

## 6. 🔒 Security & Deserialization Integrity

* Python's `pickle` serialization format can pose security risks if modified.
* **Integrity Gate**: Before loading `model.pkl`, the system executes an automated SHA-256 hash check against `ML_model/model.sha256`. If the artifact is tampered with or corrupted, startup fails immediately with a `ValueError`.
