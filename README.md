# 🛡️ Insurance Premium Prediction REST API

An end-to-end Machine Learning web application and production-grade microservice that predicts an applicant's **Insurance Premium Category** (`Low`, `Medium`, or `High`) based on their health indicators, lifestyle habits, and demographic details.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.6.1-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI Tests](https://img.shields.io/badge/CI-Pytest%20Passing-brightgreen?style=flat-square&logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![Model Card](https://img.shields.io/badge/Governance-Model%20Card-blue?style=flat-square)](MODEL_CARD.md)

---

## 🧭 How It Works (Workflow Architecture)

```mermaid
flowchart LR
    User["👤 User"] --> UI["🖥️ Streamlit UI\n(frontend.py)"]
    UI -->|"HTTP POST /predict"| API["⚡ FastAPI Microservice\n(app.py)"]
    
    subgraph Quality ["🛡️ Quality & Observability Gate"]
        API --> Observability["⏱️ Request ID & Latency Logging\n(Structured Logs)"]
        Observability --> Validate["✅ Pydantic Validation\n+ Feature Engineering\n(BMI, Risk, Age Group)"]
    end

    subgraph Security ["🔒 Security & Inference"]
        Validate --> HashCheck["🔑 SHA-256 Checksum Gate"]
        HashCheck --> Model["🧠 Scikit-Learn Model\n(Random Forest Pipeline)"]
        Model --> Output["📊 Output:\nCategory + Confidence + Probs"]
    end
    
    Output -->|"JSON Response"| UI
    UI -->|"Display Result"| User
```

---

## 🔍 Core Components & AI Quality Features

### 1. 🧠 Machine Learning Model & Governance
* **Algorithm**: `RandomForestClassifier` inside an Scikit-Learn `Pipeline` with `ColumnTransformer`.
* **Target Classes**: Predicts premium risk category — `Low`, `Medium`, or `High`.
* **Deterministic Feature Engineering**: Automatic transformations via Pydantic (`schema/user_input.py`):
  - **BMI**: $\frac{\text{weight}}{\text{height}^2}$
  - **Lifestyle Risk**: Evaluated from BMI and smoking status (`high`, `medium`, `low`).
  - **Age Group**: Categorized into `young`, `adult`, `middle_aged`, or `senior`.
  - **City Tier**: Normalized and resolved from database into Tier 1, 2, or 3.
* **Model Card**: See [MODEL_CARD.md](MODEL_CARD.md) for ethical considerations, data constraints, and performance evaluation.

---

### 2. ⚡ FastAPI Backend & Observability
* **Asynchronous High Performance**: Built with FastAPI and `uvicorn`.
* **Distributed Tracing & Request IDs**: Every request is assigned a unique `X-Request-ID` and timestamped with `X-Process-Time-Ms` response headers.
* **Structured Logging**: Transactions are logged with method, path, status, latency, and prediction metrics for operational auditing.
* **Render-Ready Health Checks**: Dual `GET` and `HEAD` support on `/` and `/health` for zero-downtime platform health probes.
* **Interactive Documentation**:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

---

### 3. 🔒 Model Security & Integrity
* **Cryptographic Tamper-Proofing**: Before deserializing `model.pkl`, the system validates the file against a recorded **SHA-256 cryptographic checksum** (`ML_model/model.sha256`), preventing pickle deserialization injection vulnerabilities.

---

### 4. 🧪 Automated Testing & CI/CD Quality Gates
* **32 Automated Tests** covering:
  - **API Contract Tests** (`tests/test_api.py`): Verifies HTTP codes, headers, and schemas.
  - **Model Invariance & Sensitivity Tests** (`tests/test_model.py`): Directional testing confirming risk score sensitivities.
  - **Schema Boundary Tests** (`tests/test_schema.py`): Edge-case testing on heights, weights, age limits, and city normalization.
* **GitHub Actions CI** (`.github/workflows/ci.yml`): Runs automated quality checks and test suites on every pull request and push to `main`.

---

## 📁 Project Structure

```plaintext
Insurance_Premium_prediction/
├── .github/workflows/
│   └── ci.yml                 # Automated CI/CD Quality Gate
├── app.py                     # FastAPI backend with observability middleware
├── frontend.py                # Streamlit web UI
├── Dockerfile                 # Slim, production-ready container image
├── requirements.txt           # Production dependencies
├── pyproject.toml             # Project metadata and test configuration
├── MODEL_CARD.md              # AI Model Card (Mitchell et al. standard)
│
├── ML_model/
│   ├── model.pkl              # Trained Random Forest pipeline artifact
│   ├── model.sha256           # SHA-256 cryptographic checksum
│   └── predict.py             # Model verification and inference
│
├── schema/
│   ├── user_input.py          # Input validation & feature engineering
│   └── prediction_response.py # Output schema contract
│
├── config/
│   └── city_tier.py           # City categorization lists
│
└── tests/
    ├── test_api.py            # API integration & health tests
    ├── test_model.py          # AI model quality & directional tests
    └── test_schema.py         # Schema boundary and feature tests
```

---

## 🚀 Running the Project

### Running Automated Tests
```bash
pytest -v tests/
```

### Running with Docker (Recommended)
1. **Build the container:**
   ```bash
   docker build -t insurance-api .
   ```
2. **Run the container:**
   ```bash
   docker run -p 8000:8000 --name insurance-container insurance-api
   ```
3. Open `http://localhost:8000/docs` in your browser.

### Running Locally
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the FastAPI backend:**
   ```bash
   uvicorn app:app --reload --port 8000
   ```
3. **In a separate terminal, launch the Streamlit frontend:**
   ```bash
   streamlit run frontend.py
   ```

---

## 👤 Author
* **Author**: Arjit Katiyar
