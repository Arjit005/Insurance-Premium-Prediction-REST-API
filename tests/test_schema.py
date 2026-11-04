import pytest
from pydantic import ValidationError

from schema.user_input import UserInput


class TestUserInputSchema:
    def test_valid_user_input(self):
        payload = {
            "age": 28,
            "weight": 70.0,
            "height": 1.75,
            "income_lpa": 12.0,
            "smoker": False,
            "city": "mumbai",
            "occupation": "private_job",
        }
        user = UserInput(**payload)
        assert user.age == 28
        assert user.city == "Mumbai"
        assert round(user.bmi, 2) == round(70.0 / (1.75**2), 2)
        assert user.city_tier == 1
        assert user.lifestyle_risk == "low"
        assert user.age_group == "adult"

    @pytest.mark.parametrize(
        "age,expected_group",
        [
            (18, "young"),
            (24, "young"),
            (25, "adult"),
            (44, "adult"),
            (45, "middle_aged"),
            (59, "middle_aged"),
            (60, "senior"),
            (85, "senior"),
        ],
    )
    def test_age_group_classification(self, age, expected_group):
        user = UserInput(
            age=age,
            weight=65.0,
            height=1.70,
            income_lpa=8.0,
            smoker=False,
            city="Pune",
            occupation="student",
        )
        assert user.age_group == expected_group

    @pytest.mark.parametrize(
        "smoker,weight,height,expected_risk",
        [
            (True, 100.0, 1.70, "high"),    # BMI ~ 34.6 (>30) and smoker
            (True, 60.0, 1.75, "medium"),   # BMI ~ 19.6 (<27) but smoker
            (False, 90.0, 1.75, "medium"),  # BMI ~ 29.4 (>27) non-smoker
            (False, 65.0, 1.75, "low"),     # BMI ~ 21.2 (<27) non-smoker
        ],
    )
    def test_lifestyle_risk_evaluation(self, smoker, weight, height, expected_risk):
        user = UserInput(
            age=30,
            weight=weight,
            height=height,
            income_lpa=10.0,
            smoker=smoker,
            city="Delhi",
            occupation="freelancer",
        )
        assert user.lifestyle_risk == expected_risk

    @pytest.mark.parametrize(
        "city_input,expected_tier",
        [
            ("  mumbai  ", 1),
            ("Bangalore", 1),
            ("Jaipur", 2),
            ("Lucknow", 2),
            ("SmallTownUnknown", 3),
        ],
    )
    def test_city_tier_mapping(self, city_input, expected_tier):
        user = UserInput(
            age=30,
            weight=65.0,
            height=1.70,
            income_lpa=6.0,
            smoker=False,
            city=city_input,
            occupation="private_job",
        )
        assert user.city_tier == expected_tier

    def test_invalid_age_bounds(self):
        with pytest.raises(ValidationError):
            UserInput(
                age=0,
                weight=65.0,
                height=1.70,
                income_lpa=5.0,
                smoker=False,
                city="Pune",
                occupation="student",
            )

        with pytest.raises(ValidationError):
            UserInput(
                age=150,
                weight=65.0,
                height=1.70,
                income_lpa=5.0,
                smoker=False,
                city="Pune",
                occupation="student",
            )

    def test_invalid_height_bounds(self):
        with pytest.raises(ValidationError):
            UserInput(
                age=25,
                weight=65.0,
                height=0.0,
                income_lpa=5.0,
                smoker=False,
                city="Pune",
                occupation="student",
            )

        with pytest.raises(ValidationError):
            UserInput(
                age=25,
                weight=65.0,
                height=3.0,
                income_lpa=5.0,
                smoker=False,
                city="Pune",
                occupation="student",
            )

    def test_invalid_occupation_fails(self):
        with pytest.raises(ValidationError):
            UserInput(
                age=25,
                weight=65.0,
                height=1.70,
                income_lpa=5.0,
                smoker=False,
                city="Pune",
                occupation="astronaut",
            )
