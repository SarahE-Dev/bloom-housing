import os
import logging
import joblib
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

# Setup logging
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logger()

# Base directory of this script (for reliable file paths)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define feature order matching the trained model
FEATURE_ORDER = [
    "AGE",
    "HINCP",
    "HHADLTKIDS",
    "disabled_person_in_household_yes",
    "disabled_person_in_household_no",
    "military_1person_active",
    "military_1person_veteran",
    "military_2plus_active_no_veterans",
    "military_2plus_veterans",
    "military_2plus_mix_active_veterans",
    "military_no_service",
    "no_government_assistance",
    "government_assistance",
]

# Load model and scaler
def load_artifacts(model_path, scaler_path):
    if not os.path.isfile(model_path):
        logger.error(f"Model file not found at {model_path}")
        raise FileNotFoundError(model_path)
    if not os.path.isfile(scaler_path):
        logger.error(f"Scaler file not found at {scaler_path}")
        raise FileNotFoundError(scaler_path)

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    logger.info(f"Loaded model from {model_path}")
    logger.info(f"Loaded scaler from {scaler_path}")
    return model, scaler

# Prepare applicant features
def prepare_features(age, income, veteran, benefits):
    raw = {
        "AGE": age,
        "HINCP": income,
        "HHADLTKIDS": 0,            # default
        "DISHH": 0,                 # assume no disabled
        "MILHH": 2 if veteran else 6,
        "FS": 1 if benefits else 0,
        "PAP": 0,
    }
    feat = {f: 0 for f in FEATURE_ORDER}
    feat["AGE"] = raw["AGE"]
    feat["HINCP"] = raw["HINCP"]
    feat["HHADLTKIDS"] = raw["HHADLTKIDS"]
    if raw["DISHH"] == 1:
        feat["disabled_person_in_household_yes"] = 1
    else:
        feat["disabled_person_in_household_no"] = 1
    mil_map = {
        1: "military_1person_active",
        2: "military_1person_veteran",
        3: "military_2plus_active_no_veterans",
        4: "military_2plus_veterans",
        5: "military_2plus_mix_active_veterans",
        6: "military_no_service",
    }
    feat[mil_map.get(raw["MILHH"])] = 1
    if raw["FS"] == 1 or raw["PAP"] > 0:
        feat["government_assistance"] = 1
    else:
        feat["no_government_assistance"] = 1
    df = pd.DataFrame([feat], columns=FEATURE_ORDER)
    return df

# Predict function
def predict_risk(model, scaler, df, threshold=0.5):
    try:
        feature_names = getattr(scaler, 'feature_names_in_', None)
        if feature_names is not None:
            df = df.reindex(columns=feature_names)
        X = df.to_numpy()
    except Exception as e:
        logger.error(f"Error aligning features for scaler: {e}")
        raise
    X_scaled = scaler.transform(X)
    prob = model.predict_proba(X_scaled)[0][1]
    pred = int(prob >= threshold)
    label = "At risk" if pred else "Not at risk"
    return dict(prediction=pred, probability=round(float(prob),4), label=label)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load artifacts on startup
def init_model():
    model_path = os.getenv('XGBOOST_MODEL_PATH', os.path.join(BASE_DIR, 'xgboost_model.pkl'))
    scaler_path = os.getenv('SCALER_PATH', os.path.join(BASE_DIR, 'scaler.pkl'))
    return load_artifacts(model_path, scaler_path)

try:
    model, scaler = init_model()
except Exception as e:
    logger.critical(f"Failed to load model/scaler: {e}")
    raise

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    try:
        data = request.get_json(force=True)
        required = ['age', 'income', 'veteran', 'benefits']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f"Missing fields: {missing}"}), 400
        age = int(data['age'])
        income = float(data['income'])
        veteran = bool(data['veteran'])
        benefits = bool(data['benefits'])
        threshold = float(data.get('threshold', 0.5))
        df = prepare_features(age, income, veteran, benefits)
        result = predict_risk(model, scaler, df, threshold)
        return jsonify(result)
    except ValueError as ve:
        logger.error(f"Invalid input types: {ve}")
        return jsonify({'error': 'Invalid input types'}), 400
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': 'Prediction error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
