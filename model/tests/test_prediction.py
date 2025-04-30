import os
import sys
import pytest
import json
import requests

# Ensure project root is on PYTHONPATH so that `app` package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Flask app and relevant objects from your application
import app.main as app_module
from app.main import app as flask_app, FEATURE_ORDER

# Helper to create dummy artifacts
def create_dummy_artifacts():
    class DummyScaler:
        feature_names_in_ = FEATURE_ORDER
        def transform(self, X):
            return X  # no scaling

    class DummyModel:
        def predict_proba(self, X):
            # Always return probability 0.8 for class 1
            return [[0.2, 0.8]]  # Adjusted to match test expectations

    return DummyModel(), DummyScaler()

@pytest.fixture
def client(monkeypatch):
    # Monkey-patch the real model & scaler in the app_module
    dummy_model, dummy_scaler = create_dummy_artifacts()
    monkeypatch.setattr(app_module, 'model', dummy_model)
    monkeypatch.setattr(app_module, 'scaler', dummy_scaler)

    # Provide Flask test client
    with flask_app.test_client() as client:
        yield client

# Unit Tests

def test_missing_fields(client):
    resp = client.post('/predict', json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data
    assert 'Missing fields' in data['error']

def test_invalid_types(client):
    payload = {
        'age': 'thirty',
        'income': 'fifty thousand',
        'veteran': 'no',
        'benefits': 'yes'
    }
    resp = client.post('/predict', json=payload)
    assert resp.status_code == 400
    assert resp.get_json() == {'error': 'Invalid input types'}

def test_success_default_threshold(client):
    payload = {
        'age': 30,
        'income': 50000,
        'veteran': False,
        'benefits': True
    }
    resp = client.post('/predict', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['probability'] == 0.8  
    assert data['prediction'] == 1
    assert data['label'] == 'At risk'

def test_success_custom_threshold(client):
    payload = {
        'age': 30,
        'income': 50000,
        'veteran': False,
        'benefits': True,
        'threshold': 0.9
    }
    resp = client.post('/predict', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['probability'] == 0.8 
    assert data['prediction'] == 0
    assert data['label'] == 'Not at risk'

def test_predict_invalid_data(client):
    payload = {
        'age': 'thirty',
        'income': 'fifty thousand',
        'veteran': 'no',
        'benefits': 'yes'
    }
    response = client.post('/predict', json=payload)
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid input types'}

def test_predict_missing_fields(client):
    response = client.post('/predict', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Missing fields' in data['error']


# Real HTTP request tests (integration tests)

def test_predict_with_requests():
    payload = {
        'age': 30,
        'income': 50000,
        'veteran': False,
        'benefits': True
    }

    # Make a real HTTP request to the Flask app
    response = requests.post('http://127.0.0.1:5000/predict', json=payload)

    # Check the status code and response data
    assert response.status_code == 200
    data = response.json()
    assert 'probability' in data
    assert 'prediction' in data
    assert 'label' in data

def test_predict_invalid_types_with_requests():
    payload = {
        'age': 'thirty',
        'income': 'fifty thousand',
        'veteran': 'no',
        'benefits': 'yes'
    }

    # Make a real HTTP request to the Flask app
    response = requests.post('http://127.0.0.1:5000/predict', json=payload)

    # Check the status code and response data
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data
    assert 'Invalid input types' in data['error']

def test_predict_missing_fields_with_requests():
    # Send an empty payload to trigger the missing fields error
    response = requests.post('http://127.0.0.1:5000/predict', json={})

    # Check the status code and response data
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data
    assert 'Missing fields' in data['error']

def test_predict_invalid_threshold_with_requests():
    # Send a payload with an invalid threshold (e.g., a value > 1 or < 0)
    payload = {
        'age': 30,
        'income': 50000,
        'veteran': False,
        'benefits': True,
        'threshold': 1.5  # Invalid threshold
    }

    # Make a real HTTP request to the Flask app
    response = requests.post('http://127.0.0.1:5000/predict', json=payload)

    # Check the status code and response data
    assert response.status_code == 400
    data = response.json()
    assert 'error' in data
    assert 'Invalid threshold' in data['error']
