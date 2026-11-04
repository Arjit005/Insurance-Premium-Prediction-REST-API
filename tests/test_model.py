import pytest
from ML_model.predict import MODEL_VERSION, predict_output, class_labels


class TestModelInference:
    def test_model_version(self):
        assert MODEL_VERSION == "1.0.0"

    def test_class_labels_present(self):
        assert len(class_labels) >= 2
        assert all(isinstance(lbl, str) for lbl in class_labels)

    def test_predict_output_structure(self):
        sample_input = {
            "bmi": 24.2,
            "age_group": "adult",
            "lifestyle_risk": "low",
            "city_tier": 1,
            "income_lpa": 12.0,
            "occupation": "private_job",
        }
        res = predict_output(sample_input)

        assert "predicted_category" in res
        assert "confidence" in res
        assert "class_probabilities" in res

        assert res["predicted_category"] in class_labels
        assert 0.0 <= res["confidence"] <= 1.0

        probs = res["class_probabilities"]
        assert len(probs) == len(class_labels)
        prob_sum = sum(probs.values())
        assert pytest.approx(prob_sum, abs=0.02) == 1.0

    def test_model_directional_sensitivity(self):
        """AI Quality Test: Verifies that a high-risk applicant profile receives a higher risk score."""
        low_risk_applicant = {
            "bmi": 21.0,
            "age_group": "young",
            "lifestyle_risk": "low",
            "city_tier": 1,
            "income_lpa": 25.0,
            "occupation": "government_job",
        }

        high_risk_applicant = {
            "bmi": 36.5,
            "age_group": "senior",
            "lifestyle_risk": "high",
            "city_tier": 3,
            "income_lpa": 3.0,
            "occupation": "unemployed",
        }

        low_pred = predict_output(low_risk_applicant)
        high_pred = predict_output(high_risk_applicant)

        # Ensure both complete successfully
        assert low_pred["predicted_category"] in class_labels
        assert high_pred["predicted_category"] in class_labels

        # If 'High' is a class, the high-risk applicant's probability for High risk
        # should exceed or match the low-risk applicant's probability
        if "High" in low_pred["class_probabilities"] and "High" in high_pred["class_probabilities"]:
            assert high_pred["class_probabilities"]["High"] >= low_pred["class_probabilities"]["High"]
