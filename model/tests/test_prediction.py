import os
import sys
import pytest
import json

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
            # always return probability 0.8 for class 1
            return [[1 - 0.8, 0.8]]

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

