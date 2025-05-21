import os
import logging
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
import joblib

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
    "HINCP",
    "AGE",
    "NUMPEOPLE",
    "DISHH",
    "MILHH",
    "gov_assistance",
]

# Load model
def load_model(model_path):
    if not os.path.isfile(model_path):
        logger.error(f"Model file not found at {model_path}")
        raise FileNotFoundError(model_path)
    model = joblib.load(model_path)
    logger.info(f"Loaded model from {model_path}")
    return model

# Prepare applicant features
def prepare_features(age, income, num_people, veteran, benefits, disabled: bool = False):
    """
    Prepare features for prediction, matching the training data structure.
    age: Age of the applicant
    income: Household income
    num_people: Number of people in the household
    veteran: Whether the household has a veteran (True/False)
    benefits: Whether the household receives government assistance (True/False)
    disabled: Whether someone in the household is disabled (default False)
    """
    feat = {
        "HINCP": income,
        "AGE": age,
        "NUMPEOPLE": num_people,
        "DISHH": 1 if disabled else 0,
        "MILHH": 1 if veteran else 0,
        "gov_assistance": 1 if benefits else 0,
    }
    df = pd.DataFrame([feat], columns=FEATURE_ORDER)
    return df

# Predict function
def predict_risk(model, df, threshold=0.4):
    try:
        prob = model.predict_proba(df)[0][1]  # Probability of high risk (class 1)
        pred = int(prob >= threshold)
        label = "At risk" if pred else "Not at risk"
        return dict(prediction=pred, probability=round(float(prob), 4), label=label)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load model on startup
def init_model():
    model_path = os.getenv('XGBOOST_MODEL_PATH', os.path.join(BASE_DIR, '..', 'app', 'xgboost_risk_model.pkl'))
    return load_model(model_path)

try:
    model = init_model()
except Exception as e:
    logger.critical(f"Failed to load model: {e}")
    raise

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    try:
        data = request.get_json(force=True)
        required = ['age', 'income', 'num_people', 'veteran', 'benefits']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({'error': f"Missing fields: {missing}"}), 400

        # Validate input types
        try:
            age = int(data['age'])
            income = float(data['income'])
            num_people = int(data['num_people'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid input types for age, income, or num_people'}), 400

        # Validate boolean inputs
        if not isinstance(data['veteran'], bool) or not isinstance(data['benefits'], bool):
            return jsonify({'error': 'Invalid input types for veteran or benefits'}), 400
        veteran = data['veteran']
        benefits = data['benefits']

        # Optional field
        disabled = bool(data.get('disabled', False))

        # Build features and predict
        df = prepare_features(age, income, num_people, veteran, benefits, disabled)
        result = predict_risk(model, df, threshold=0.4)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': 'Prediction error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    logger.info(f"Starting Flask app on port {port}...")