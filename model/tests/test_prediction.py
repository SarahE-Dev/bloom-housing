import os
import pytest
import requests

# Base URL of the running Flask service
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:5000")
ENDPOINT = f"{BASE_URL}/predict"

def assert_valid_response(resp, threshold=0.4):
    """Assert the response is valid with the fixed threshold of 0.4."""
    assert resp.status_code == 200, f"{resp.status_code} / {resp.text}"
    data = resp.json()
    assert set(data) >= {"probability", "prediction", "label"}, f"Missing keys in {data}"
    prob = data["probability"]
    pred = data["prediction"]
    label = data["label"]

    # Probability is between 0 and 1
    assert isinstance(prob, (float, int)), f"Probability {prob} is not numeric"
    assert 0.0 <= prob <= 1.0, f"Probability {prob} out of range"

    # Prediction is 0 or 1
    assert pred in (0, 1), f"Prediction {pred} is not 0 or 1"

    # Prediction matches threshold
    expected_pred = 1 if prob >= threshold else 0
    assert pred == expected_pred, f"Prediction {pred} does not match threshold {threshold} (prob={prob})"

    # Label matches prediction
    expected_label = "At risk" if pred else "Not at risk"
    assert label == expected_label, f"Label {label} does not match prediction {pred}"

# 1) Missing required fields → 400
@pytest.mark.parametrize("payload", [
    {},
    {"age": 30, "income": 10000},  # Missing num_people, veteran, benefits
    {"age": 30, "num_people": 3, "veteran": False},  # Missing income, benefits
])
def test_missing_required_fields(payload):
    resp = requests.post(ENDPOINT, json=payload)
    assert resp.status_code == 400
    assert "Missing fields" in resp.json().get("error", ""), f"Error: {resp.json()}"

# 2) Invalid types for required fields
@pytest.mark.parametrize("payload,expected_error", [
    (
        {"age": "30", "income": 10000, "num_people": 3, "veteran": False, "benefits": True},
        None  # App casts string age
    ),
    (
        {"age": 30, "income": "10000", "num_people": 3, "veteran": False, "benefits": True},
        None  # App casts string income
    ),
    (
        {"age": 30, "income": 10000, "num_people": "3", "veteran": False, "benefits": True},
        None  # App casts string num_people
    ),
    (
        {"age": 30, "income": 10000, "num_people": 3, "veteran": "False", "benefits": True},
        "Invalid input types for veteran or benefits"
    ),
    (
        {"age": 30, "income": 10000, "num_people": 3, "veteran": False, "benefits": "True"},
        "Invalid input types for veteran or benefits"
    ),
])
def test_invalid_required_types(payload, expected_error):
    resp = requests.post(ENDPOINT, json=payload)
    if expected_error:
        assert resp.status_code == 400
        assert resp.json().get("error") == expected_error, f"Error: {resp.json()}"
    else:
        assert resp.status_code == 200
        assert_valid_response(resp)

# 3) Default threshold (0.4) → valid response
def test_default_threshold():
    payload = {"age": 50, "income": 20000, "num_people": 3, "veteran": False, "benefits": True}
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp, threshold=0.4)

# 4) Optional: disabled only
def test_with_disabled_only():
    payload = {
        "age": 40, "income": 30000,
        "num_people": 3, "veteran": True, "benefits": False,
        "disabled": True
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp, threshold=0.4)

# 5) Optional: disabled absent (defaults to False)
def test_without_disabled():
    payload = {
        "age": 40, "income": 30000,
        "num_people": 3, "veteran": True, "benefits": False
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp, threshold=0.4)

# 6) Extra fields should be ignored
def test_ignores_extra_fields():
    payload = {
        "age": 30, "income": 50000,
        "num_people": 3, "veteran": False, "benefits": True,
        "foo": "bar", "baz": 123
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp)

# 7) Numeric num_people casting
def test_num_people_casting():
    payload = {
        "age": 30, "income": 50000,
        "num_people": 2.7,  # Should cast to 3
        "veteran": False, "benefits": True
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp)

# 8) Issue #55: Test prediction for income=32000, num_people=3
def test_issue_55_prediction():
    payload = {
        "age": 35,
        "income": 32000,
        "num_people": 3,
        "veteran": False,
        "benefits": False,
        "disabled": False
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp, threshold=0.4)
    data = resp.json()
    assert data["prediction"] == 0, f"Expected 'Not at risk' for prob={data['probability']}"
    assert data["label"] == "Not at risk"