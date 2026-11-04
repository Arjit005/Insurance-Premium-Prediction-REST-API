import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestInsuranceAPI:
    def test_root_endpoint_get(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_version" in data

    def test_root_endpoint_head(self):
        response = client.head("/")
        assert response.status_code == 200

    def test_health_endpoint_get(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_endpoint_head(self):
        response = client.head("/health")
        assert response.status_code == 200

    def test_predict_success(self):
        payload = {
            "age": 32,
            "weight": 72.5,
            "height": 1.78,
            "income_lpa": 14.5,
            "smoker": False,
            "city": "Mumbai",
            "occupation": "private_job",
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "predicted_category" in data
        assert "confidence" in data
        assert "class_probabilities" in data

        # Check observability headers
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time-Ms" in response.headers

    def test_predict_validation_error_invalid_age(self):
        payload = {
            "age": -5,  # Invalid
            "weight": 70.0,
            "height": 1.75,
            "income_lpa": 10.0,
            "smoker": False,
            "city": "Delhi",
            "occupation": "private_job",
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_validation_error_missing_field(self):
        payload = {
            "age": 28,
            "height": 1.75,
            # Missing weight, smoker, etc.
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
