import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, roc_auc_score
from xgboost import XGBClassifier
import pandas as pd
import numpy as np
import os
import logging
import joblib
import shap

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_processed_data(data_dir="data", filename="final_df.csv"):
    """Load processed data."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.normpath(os.path.join(base_dir, "..", data_dir, filename))
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Processed data not found at: {csv_path}")
        logger.info(f"Loading processed data from {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"Columns in final_df.csv: {list(df.columns)}")
        return df
    except Exception as e:
        logger.error(f"Error loading processed data: {str(e)}")
        raise

def save_model_and_scaler(model, scaler, model_dir="app"):
    """Save model and scaler."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.normpath(os.path.join(base_dir, "..", model_dir))
        os.makedirs(target_dir, exist_ok=True)
        
        model_path = os.path.join(target_dir, "xgboost_model.pkl")
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        scaler_path = os.path.join(target_dir, "scaler.pkl")
        joblib.dump(scaler, scaler_path)
        logger.info(f"Scaler saved to {scaler_path}")
    except Exception as e:
        logger.error(f"Error saving model and scaler: {str(e)}")
        raise

def plot_confusion_matrix(y_true, y_pred, plots_dir):
    """Plot confusion matrix."""
    conf_matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Not at risk', 'At risk'],
                yticklabels=['Not at risk', 'At risk'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig(os.path.join(plots_dir, "confusion_matrix.png"))
    plt.close()

def plot_roc_curve(y_true, y_pred_proba, plots_dir):
    """Plot ROC curve."""
    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    auc_score = roc_auc_score(y_true, y_pred_proba)
    
    plt.figure()
    plt.plot(fpr, tpr, label=f'XGBoost (AUC = {auc_score:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.savefig(os.path.join(plots_dir, "roc_curve.png"))
    plt.close()

def plot_shap_summary(model, X_test_scaled, X_test, plots_dir):
    """Plot SHAP summary."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test_scaled)
    shap.summary_plot(shap_values, X_test, plot_type="bar")
    plt.savefig(os.path.join(plots_dir, "shap_summary.png"))
    plt.close()

def predict_household_risk(input_data, feature_cols, model_dir="app", threshold=0.5):
    """Predict household risk."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.normpath(os.path.join(base_dir, "..", model_dir, "xgboost_model.pkl"))
        scaler_path = os.path.normpath(os.path.join(base_dir, "..", model_dir, "scaler.pkl"))
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        logger.info("Model and scaler loaded")
        
        # Create input_df with exact feature_cols order
        input_df = pd.DataFrame(columns=feature_cols, index=[0])
        input_df['AGE'] = input_data['age']
        input_df['NUMPEOPLE'] = input_data['household_size']
        income = input_data['income']
        # Map income to bins
        if income <= 40000:
            input_df['income_low'] = 1
            input_df['income_medium'] = 0
            input_df['income_high'] = 0
        elif income <= 80000:
            input_df['income_low'] = 0
            input_df['income_medium'] = 1
            input_df['income_high'] = 0
        else:
            input_df['income_low'] = 0
            input_df['income_medium'] = 0
            input_df['income_high'] = 1
        input_df['disabled_yes'] = 1 if input_data['disabled'] else 0
        input_df['disabled_no'] = 0 if input_data['disabled'] else 1
        
        # Updated: Simplified military/veteran status to binary
        input_df['no_veteran'] = 0 if input_data['veteran'] else 1
        input_df['has_veteran'] = 1 if input_data['veteran'] else 0
        
        input_df['no_assistance_flag'] = 0 if input_data['benefits'] else 1
        input_df['assistance'] = 1 if input_data['benefits'] else 0
        input_df['high_risk_age'] = 1 if (18 <= input_data['age'] <= 24 or input_data['age'] >= 65) else 0
        
        logger.info(f"Input DataFrame columns: {list(input_df.columns)}")
        input_scaled = scaler.transform(input_df)
        prediction_proba = model.predict_proba(input_scaled)[0]
        prediction = (prediction_proba[1] > threshold).astype(int)
        
        logger.info(f"Prediction: {'At risk' if prediction == 1 else 'Not at risk'}")
        logger.info(f"Probability (Not at risk, At risk): {prediction_proba}")
        
        # SHAP explanation
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(input_scaled)
        shap.initjs()
        shap.force_plot(explainer.expected_value, shap_values[0], input_df.iloc[0], matplotlib=True)
        plt.savefig(os.path.join(os.path.dirname(__file__), "..", "plots", "shap_force_plot.png"))
        plt.close()
        
        return prediction, prediction_proba
    
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise

def main():
    """Main training pipeline."""
    try:
        final_df = load_processed_data()
        
        X = final_df.drop(columns=['at_risk_household'])
        y = final_df['at_risk_household']
        
        feature_cols = list(X.columns)
        logger.info(f"Training feature columns: {feature_cols}")
        logger.info(f"Class distribution:\n{y.value_counts()}")
        
        # Split into train/test/holdout
        X_temp, X_holdout, y_temp, y_holdout = train_test_split(
            X, y, test_size=0.1, random_state=42, stratify=y
        )
        X_train, X_test, y_train, y_test = train_test_split(
            X_temp, y_temp, test_size=0.2222, random_state=42, stratify=y_temp
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        X_holdout_scaled = scaler.transform(X_holdout)
        
        # Hyperparameter tuning
        param_grid = {
            'n_estimators': [50],
            'max_depth': [3, 5],
            'learning_rate': [0.1, 0.3],
            'subsample': [0.6],
            'colsample_bytree': [0.6]
        }
        model = XGBClassifier(
            random_state=42,
            eval_metric='logloss',
            scale_pos_weight=len(y_train[y_train == 0]) / len(y_train[y_train == 1]) * 1.5,
            gamma=5,
            min_child_weight=25
        )
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='f1_macro', n_jobs=-1)
        grid_search.fit(X_train_scaled, y_train)
        model = grid_search.best_estimator_
        logger.info(f"Best parameters: {grid_search.best_params_}")
        
        # Cross-validation
        scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='f1_macro')
        logger.info(f"Cross-validation F1 scores: {scores.mean():.2f} ± {scores.std():.2f}")
        
        # Evaluate on test set
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        logger.info("\nClassification Report (Test Set):")
        logger.info(classification_report(y_test, y_pred))
        
        # Evaluate on holdout set
        y_holdout_pred_proba = model.predict_proba(X_holdout_scaled)[:, 1]
        y_holdout_pred = (y_holdout_pred_proba > 0.5).astype(int)
        
        logger.info("\nClassification Report (Holdout Set):")
        logger.info(classification_report(y_holdout, y_holdout_pred))
        
        plots_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "plots"))
        os.makedirs(plots_dir, exist_ok=True)
        plot_confusion_matrix(y_test, y_pred, plots_dir)
        plot_roc_curve(y_test, y_pred_proba, plots_dir)
        plot_shap_summary(model, X_test_scaled, X_test, plots_dir)
        
        save_model_and_scaler(model, scaler)
        
        # Test cases
        test_cases = [
            {
                "name": "Original",
                "data": {"age": 40, "income": 30000, "veteran": False, "benefits": True, "household_size": 2, "disabled": False}
            },
            {
                "name": "Veteran=True",
                "data": {"age": 40, "income": 30000, "veteran": True, "benefits": True, "household_size": 2, "disabled": False}
            },
            {
                "name": "Age=18",
                "data": {"age": 18, "income": 30000, "veteran": False, "benefits": True, "household_size": 2, "disabled": False}
            },
            {
                "name": "Age=70",
                "data": {"age": 70, "income": 30000, "veteran": False, "benefits": True, "household_size": 2, "disabled": False}
            },
            {
                "name": "Benefits=False",
                "data": {"age": 40, "income": 30000, "veteran": False, "benefits": False, "household_size": 2, "disabled": False}
            },
            {
                "name": "High Income",
                "data": {"age": 40, "income": 80000, "veteran": False, "benefits": True, "household_size": 2, "disabled": False}
            },
            {
                "name": "Disabled=True",
                "data": {"age": 40, "income": 30000, "veteran": False, "benefits": True, "household_size": 2, "disabled": True}
            },
            {
                "name": "Medium Income",
                "data": {"age": 40, "income": 50000, "veteran": False, "benefits": True, "household_size": 2, "disabled": False}
            },
            {
                "name": "Only benefits",
                "data": {"age": 40, "income": 60000, "veteran": False, "benefits": False, "household_size": 1, "disabled": False}
            },
            {
                "name": "Debbie",
                "data": {"age": 39, "income": 34000, "veteran": False, "benefits": False, "household_size": 3, "disabled": False}
            }
        ]
        
        for case in test_cases:
            prediction, prediction_proba = predict_household_risk(case['data'], feature_cols, threshold=0.5)
            print(f"Prediction for {case['name']}: {'At risk' if prediction == 1 else 'Not at risk'}")
            print(f"Probability (Not at risk, At risk): {prediction_proba}")
        
        logger.info("Training pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Error in training pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()