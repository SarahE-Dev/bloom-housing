from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load model
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    raise Exception("Model file not found")

@app.route("/model", methods=["POST"])
def predict():
    try:
        # Get JSON data
        data = request.get_json()
        if not data or "features" not in data:
            return jsonify({"error": "Missing 'features' in request body"}), 400

        feature_dict = data["features"]
        
        # These can obviously be changed to match the model's expected input
        # This are just the mock features I used to train the model
        expected_features = [
            "income",
            "household_size",
            "housing_status",
            "income_vouchers",
            "household_expecting_changes",
            "household_student"
        ]

        # Validate input
        missing = [key for key in expected_features if key not in feature_dict]
        if missing:
            return jsonify({"error": f"Missing keys: {missing}"}), 400

        df = pd.DataFrame([feature_dict], columns=expected_features)
        input_data = df.to_numpy()


        # Make prediction
        risk_score = model.predict_proba(input_data)[0][1]  # Probability of high risk (class 1)

        return jsonify({
            "risk_score": float(risk_score),
            "message": "Risk score represents likelihood of being unhoused (0 to 1, higher is riskier)"
        })

    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)