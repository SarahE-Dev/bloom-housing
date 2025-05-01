import os
import pytest
import requests

# Base URL of your running Flask service
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:5000")
ENDPOINT = f"{BASE_URL}/predict"


def assert_valid_response(resp, threshold=0.5):
    # Must be HTTP 200
    assert resp.status_code == 200, f"{resp.status_code} / {resp.text}"
    data = resp.json()
    # Keys present
    assert set(data) >= {"probability", "prediction", "label"}
    prob = data["probability"]
    pred = data["prediction"]
    label = data["label"]

    # Probability is between 0 and 1
    assert isinstance(prob, (float, int))
    assert 0.0 <= prob <= 1.0

    # Prediction is 0 or 1
    assert pred in (0, 1)

    # Prediction matches threshold
    expected_pred = 1 if prob >= threshold else 0
    assert pred == expected_pred

    # Label matches prediction
    expected_label = "At risk" if pred else "Not at risk"
    assert label == expected_label


# 1) Missing required fields → 400
def test_missing_required_fields():
    resp = requests.post(ENDPOINT, json={})
    assert resp.status_code == 400
    assert "Missing fields" in resp.json().get("error", "")


# 2) Invalid types for each required field → 400
@pytest.mark.parametrize("payload", [
    {"age": "a", "income": 10000, "veteran": False, "benefits": True},
    {"age": 30, "income": "x", "veteran": False, "benefits": True},
    {"age": 30, "income": 10000, "veteran": "no", "benefits": True},
    {"age": 30, "income": 10000, "veteran": False, "benefits": "yes"},
])
def test_invalid_required_types(payload):
    resp = requests.post(ENDPOINT, json=payload)
    assert resp.status_code == 400
    assert resp.json() == {"error": "Invalid input types"}


# 3) Invalid threshold values → 400
@pytest.mark.parametrize("bad_thresh", [-0.1, 1.1, "foo", None])
def test_invalid_threshold(bad_thresh):
    payload = {
        "age": 30,
        "income": 50000,
        "veteran": True,
        "benefits": False,
        "threshold": bad_thresh
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert resp.status_code == 400
    assert "Invalid threshold" in resp.json().get("error", "")


# 4) Default threshold (0.5) → valid response
def test_default_threshold():
    payload = {"age": 50, "income": 20000, "veteran": False, "benefits": True}
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp, threshold=0.5)


# 5) Custom threshold above/below probability
def test_custom_threshold_logic():
    # threshold below 0.5 should still succeed
    p1 = requests.post(ENDPOINT, json={
        "age": 50, "income": 20000, "veteran": False, "benefits": True,
        "threshold": 0.1
    })
    assert_valid_response(p1, threshold=0.1)

    # threshold high should flip prediction if prob< threshold
    p2 = requests.post(ENDPOINT, json={
        "age": 50, "income": 20000, "veteran": False, "benefits": True,
        "threshold": 0.99
    })
    assert_valid_response(p2, threshold=0.99)


# 6) Optional: adult_kids only
def test_with_adult_kids_only():
    payload = {
        "age": 40, "income": 30000,
        "veteran": True, "benefits": False,
        "adult_kids": 3
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp)


# 7) Optional: disabled only
def test_with_disabled_only():
    payload = {
        "age": 40, "income": 30000,
        "veteran": True, "benefits": False,
        "disabled": True
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp)


# 8) Both optional fields present
def test_with_both_optionals():
    payload = {
        "age": 40, "income": 30000,
        "veteran": False, "benefits": True,
        "adult_kids": 2, "disabled": False
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp)


# 9) Extra fields should be ignored
def test_ignores_extra_fields():
    payload = {
        "age": 30, "income": 50000,
        "veteran": False, "benefits": True,
        "foo": "bar", "baz": 123
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp)


# 10) Numeric adult_kids casting
def test_adult_kids_casting():
    payload = {
        "age": 30, "income": 50000,
        "veteran": False, "benefits": True,
        "adult_kids": 2.7
    }
    resp = requests.post(ENDPOINT, json=payload)
    assert_valid_response(resp)
