import os
import argparse
import logging
import pandas as pd
import joblib

# Setup logging
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logger()

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
    # one-hot init
    feat = {f: 0 for f in FEATURE_ORDER}
    # numeric
    feat["AGE"] = raw["AGE"]
    feat["HINCP"] = raw["HINCP"]
    feat["HHADLTKIDS"] = raw["HHADLTKIDS"]
    # disabled
    if raw["DISHH"] == 1:
        feat["disabled_person_in_household_yes"] = 1
    else:
        feat["disabled_person_in_household_no"] = 1
    # military mapping
    mil_map = {
        1: "military_1person_active",
        2: "military_1person_veteran",
        3: "military_2plus_active_no_veterans",
        4: "military_2plus_veterans",
        5: "military_2plus_mix_active_veterans",
        6: "military_no_service",
    }
    mil_key = mil_map.get(raw["MILHH"])
    feat[mil_key] = 1
    # government assistance
    if raw["FS"] == 1 or raw["PAP"] > 0:
        feat["government_assistance"] = 1
    else:
        feat["no_government_assistance"] = 1
    # return DataFrame
    df = pd.DataFrame([feat], columns=FEATURE_ORDER)
    return df

# Predict function
def predict_risk(model, scaler, df, threshold=0.5):
    # Reorder and align DataFrame to scaler's expected feature names
    try:
        feature_names = getattr(scaler, 'feature_names_in_', None)
        if feature_names is not None:
            df = df.reindex(columns=feature_names)
        X = df.to_numpy()
    except Exception as e:
        logger.error(f"Error aligning features for scaler: {e}")
        raise

    # Scale features
    X_scaled = scaler.transform(X)
    # Predict probability for positive class
    prob = model.predict_proba(X_scaled)[0][1]
    # Apply threshold to determine label
    pred = int(prob >= threshold)
    label = "At risk" if pred else "Not at risk"
    return dict(prediction=pred, probability=round(float(prob),4), label=label)

# CLI entry point
def main():
    parser = argparse.ArgumentParser(description="Predict risk based on applicant data.")
    parser.add_argument("--age", type=int, required=True, help="Applicant age")
    parser.add_argument("--income", type=float, required=True, help="Annual household income")
    parser.add_argument("--veteran", action="store_true", help="Flag if applicant is a veteran")
    parser.add_argument("--benefits", action="store_true", help="Flag if applicant receives benefits")
    parser.add_argument("--threshold", type=float, default=0.5, help="Classification threshold")
    parser.add_argument("--model", type=str, default="xgboost_model.pkl", help="Path to model file")
    parser.add_argument("--scaler", type=str, default="scaler.pkl", help="Path to scaler file")
    args = parser.parse_args()

    model, scaler = load_artifacts(args.model, args.scaler)
    df = prepare_features(args.age, args.income, args.veteran, args.benefits)
    result = predict_risk(model, scaler, df, threshold=args.threshold)
    print(result)

if __name__ == "__main__":
    main()