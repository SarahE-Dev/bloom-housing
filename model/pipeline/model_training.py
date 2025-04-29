import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve,
    roc_auc_score, precision_recall_curve, average_precision_score
)
from xgboost import XGBClassifier
import shap
from sklearn.inspection import permutation_importance
import pandas as pd
import numpy as np
import os
import logging
import joblib  # For saving model and scaler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_processed_data(data_dir="data", filename="final_df.csv"):
    """Load processed data from CSV file."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "..", data_dir, filename)
        csv_path = os.path.normpath(data_path)
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Processed data not found at: {csv_path}")
            
        logger.info(f"Loading processed data from {csv_path}")
        return pd.read_csv(csv_path)
    
    except Exception as e:
        logger.error(f"Error loading processed data: {str(e)}")
        raise

def save_model_and_scaler(model, scaler, model_dir="app"):
    """Save trained model and scaler to specified directory."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.join(base_dir, "..", model_dir)
        target_dir = os.path.normpath(target_dir)
        
        # Create directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Save model
        model_path = os.path.join(target_dir, "xgboost_model.pkl")
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save scaler
        scaler_path = os.path.join(target_dir, "scaler.pkl")
        joblib.dump(scaler, scaler_path)
        logger.info(f"Scaler saved to {scaler_path}")
        
    except Exception as e:
        logger.error(f"Error saving model and scaler: {str(e)}")
        raise

def plot_confusion_matrix(y_true, y_pred):
    """Plot and save confusion matrix."""
    conf_matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Not at risk', 'At risk'],
                yticklabels=['Not at risk', 'At risk'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    
    # Create plots directory if not exists
    plots_dir = os.path.join(os.path.dirname(__file__), "..", "plots")
    os.makedirs(plots_dir, exist_ok=True)
    plt.savefig(os.path.join(plots_dir, "confusion_matrix.png"))
    plt.close()

def plot_roc_curve(y_true, y_pred_proba):
    """Plot and save ROC curve."""
    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    auc_score = roc_auc_score(y_true, y_pred_proba)
    
    plt.figure()
    plt.plot(fpr, tpr, label=f'XGBoost (AUC = {auc_score:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    
    plots_dir = os.path.join(os.path.dirname(__file__), "..", "plots")
    plt.savefig(os.path.join(plots_dir, "roc_curve.png"))
    plt.close()

def plot_feature_importance(model, features, X_train):
    """Plot and save SHAP feature importance."""
    explainer = shap.Explainer(model)
    shap_values = explainer(X_train)
    
    plt.figure()
    shap.summary_plot(shap_values, X_train, feature_names=features.columns, show=False)
    
    plots_dir = os.path.join(os.path.dirname(__file__), "..", "plots")
    plt.savefig(os.path.join(plots_dir, "shap_summary.png"))
    plt.close()

def main():
    """Main training pipeline."""
    try:
        # Load processed data
        final_df = load_processed_data()
        
        # Prepare data
        X = final_df.drop(columns=['at_risk'])
        y = final_df['at_risk']
        
        # Check class distribution
        logger.info(f"Class distribution:\n{y.value_counts()}")
        logger.info(f"Class ratio: {y.value_counts()[0]/y.value_counts()[1]:.2f}:1")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            eval_metric='logloss'
        )
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Generate reports
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        # Plot visualizations
        plot_confusion_matrix(y_test, y_pred)
        plot_roc_curve(y_test, y_pred_proba)
        plot_feature_importance(model, X, X_train_scaled)
        
        # Save model and scaler
        save_model_and_scaler(model, scaler)
        
        logger.info("Training pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Training pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()