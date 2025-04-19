import pandas as pd
import xgboost as xgb
import joblib

# Load preprocessor and feature names
preprocessor = joblib.load('preprocessor.joblib')
feature_names = joblib.load('feature_names.joblib')

# Load the model (Booster object)
model = xgb.Booster()
model.load_model('model.xgb')

# Function to predict risk for a new applicant
def predict_risk(applicant_data):
    # Validate input
    required_keys = ['HINCP', 'TOTHCAMT', 'HHAGE', 'TENURE', 'HHRACE', 'DISHH', 'FS', 'PERPOVLVL']
    if 'HINUMOVE' in preprocessor.feature_names_in_:
        required_keys.append('HINUMOVE')
    if 'HIBEHINDFRQ' in preprocessor.feature_names_in_:
        required_keys.append('HIBEHINDFRQ')
    if not all(key in applicant_data for key in required_keys):
        raise ValueError(f"Missing required keys: {set(required_keys) - set(applicant_data.keys())}")
    
    # Convert applicant data to DataFrame
    new_applicant = pd.DataFrame([applicant_data])
    
    # Preprocess the data
    new_applicant_preprocessed = preprocessor.transform(new_applicant)
    
    # Convert to DMatrix for prediction
    dmatrix = xgb.DMatrix(new_applicant_preprocessed)
    
    # Predict risk and probability
    risk_probability = model.predict(dmatrix)[0]
    risk_prediction = 1 if risk_probability > 0.2 else 0  # Match threshold=0.2
    
    return {
        'predicted_risk': int(risk_prediction),
        'probability': float(risk_probability)
    }

# Example usage
if __name__ == "__main__":
    applicant = {
        'HINCP': 20000,
        'TOTHCAMT': 1000,
        'HHAGE': 40,
        'TENURE': "'1'",  # AHS code: '1'=owned, '2'=rented
        'HHRACE': "'01'",  # AHS code: '01'=white
        'DISHH': "'1'",  # AHS code: '1'=yes, '2'=no
        'FS': "'1'",  # AHS code: '1'=yes, '2'=no
        'PERPOVLVL': "'1'",  # AHS code: '1'=below, '2'=at/above
        'HINUMOVE': 2,
        'HIBEHINDFRQ': "'1'"  # AHS code: '1'=often, '2'=sometimes, '3'=never
    }
    result = predict_risk(applicant)
    print(f"Predicted Risk (0=Low, 1=High): {result['predicted_risk']}")
    print(f"Probability of High Risk: {result['probability']}")

    # Test cases for robustness
    test_cases = [
        {'HINCP': 10000, 'TOTHCAMT': 1500, 'HHAGE': 30, 'TENURE': "'2'", 'HHRACE': "'01'", 'DISHH': "'2'", 'FS': "'1'", 'PERPOVLVL': "'1'", 'HINUMOVE': 3, 'HIBEHINDFRQ': "'1'"},
        {'HINCP': 100000, 'TOTHCAMT': 500, 'HHAGE': 50, 'TENURE': "'1'", 'HHRACE': "'02'", 'DISHH': "'1'", 'FS': "'2'", 'PERPOVLVL': "'2'", 'HINUMOVE': 0, 'HIBEHINDFRQ': "'3'"}
    ]
    for i, case in enumerate(test_cases):
        result = predict_risk(case)
        print(f"Test Case {i+1}: Risk={result['predicted_risk']}, Probability={result['probability']}")

# For microservice integration (e.g., with FastAPI):
# from fastapi import FastAPI
# app = FastAPI()
# @app.post("/predict")
# async def predict(applicant: dict):
#     return predict_risk(applicant)