import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve,
    roc_auc_score, precision_recall_curve, average_precision_score
)
from xgboost import XGBClassifier
import shap
from sklearn.inspection import permutation_importance
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import joblib
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set random seed for reproducibility
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Get the directory of the current script
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / ".." / "data"
OUTPUT_DIR = SCRIPT_DIR / ".." / "model_outputs"
MODEL_DIR = SCRIPT_DIR / ".." / "app"
MODEL_PATH = MODEL_DIR / "xgboost_risk_model.pkl"
PLOT_DIR = OUTPUT_DIR / "plots"

def load_data(file_path: Path) -> pd.DataFrame:
    """Load the processed dataset and validate columns."""
    try:
        df = pd.read_csv(file_path)
        expected_cols = ["HINCP", "AGE", "NUMPEOPLE", "DISHH", "MILHH", "gov_assistance", "at_risk"]
        if not all(col in df.columns for col in expected_cols):
            missing = [col for col in expected_cols if col not in df.columns]
            logger.error(f"Missing columns: {missing}")
            raise ValueError(f"Missing columns: {missing}")
        logger.info(f"Loaded data from {file_path} with shape {df.shape}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def prepare_features_and_target(df: pd.DataFrame) -> tuple:
    """Split data into features and target, and identify column types."""
    try:
        # Check for NaN values
        if df.isna().any().any():
            logger.warning(f"NaN values found in data: {df.isna().sum()}")
        
        # Validate target
        X = df.drop(columns=['at_risk'])
        y = df['at_risk']
        if not y.isin([0, 1]).all():
            logger.error("Target 'at_risk' contains non-binary values")
            raise ValueError("Target 'at_risk' must be binary (0 or 1)")
        
        # Log class distribution
        class_dist = y.value_counts(normalize=True).to_dict()
        logger.info(f"Class distribution: {class_dist}")
        
        continuous_cols = ['HINCP', 'AGE', 'NUMPEOPLE']
        cat_cols = [col for col in X.columns if col not in continuous_cols]
        cat_idx = [X.columns.get_loc(col) for col in cat_cols]
        logger.info(f"Categorical columns: {cat_cols}")
        logger.info(f"Categorical indices: {cat_idx}")
        return X, y, continuous_cols, cat_cols
    except Exception as e:
        logger.error(f"Error preparing features and target: {str(e)}")
        raise

def create_pipeline(continuous_cols: list) -> Pipeline:
    """Create the preprocessing and model pipeline."""
    try:
        preprocessor = ColumnTransformer(
            [('num', RobustScaler(), continuous_cols)],
            remainder='passthrough'
        )
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            (
                "classifier",
                XGBClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    scale_pos_weight=2.5,
                    random_state=RANDOM_SEED,
                    objective="binary:logistic",
                    eval_metric=["logloss", "auc"],
                ),
            ),
        ])
        logger.info(f"Created model pipeline with scale_pos_weight={scale_pos_weight:.2f}")
        return pipeline
    except Exception as e:
        logger.error(f"Error creating pipeline: {str(e)}")
        raise

def evaluate_model(model: Pipeline, X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, y_test: pd.DataFrame, thresholds: list = [0.3, 0.4, 0.5]) -> dict:
    """Evaluate the model and generate metrics and plots."""
    try:
        # Training set evaluation
        y_train_pred_proba = model.predict_proba(X_train)[:, 1]
        train_roc_auc = roc_auc_score(y_train, y_train_pred_proba)
        logger.info(f"Training ROC AUC: {train_roc_auc:.2f}")
        
        # Test set predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Evaluate multiple thresholds
        reports = {}
        for threshold in thresholds:
            y_pred_custom = (y_pred_proba > threshold).astype(int)
            report = classification_report(y_test, y_pred_custom, output_dict=True)
            print(f"\nClassification Report (threshold={threshold}):")
            print(classification_report(y_test, y_pred_custom))
            reports[threshold] = report
            
            # Confusion matrix (only for default threshold 0.4)
            if threshold == 0.4:
                conf_matrix = confusion_matrix(y_test, y_pred_custom)
                PLOT_DIR.mkdir(parents=True, exist_ok=True)
                plt.figure(figsize=(8, 6))
                sns.set_style("whitegrid")
                sns.heatmap(
                    conf_matrix,
                    annot=True,
                    fmt="d",
                    cmap="Blues",
                    xticklabels=["Not at risk", "At risk"],
                    yticklabels=["Not at risk", "At risk"],
                )
                plt.xlabel("Predicted")
                plt.ylabel("Actual")
                plt.title("Confusion Matrix - 40% Threshold")
                plt.savefig(PLOT_DIR / "confusion_matrix.png")
                plt.close()
                logger.info(f"Saved confusion matrix plot to {PLOT_DIR / 'confusion_matrix.png'}")

        # ROC Curve
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend(loc='lower right')
        plt.savefig(PLOT_DIR / "roc_curve.png")
        plt.close()
        logger.info(f"Saved ROC curve plot to {PLOT_DIR / 'roc_curve.png'}")

        # Precision-Recall Curve
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        avg_precision = average_precision_score(y_test, y_pred_proba)
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, label=f'PR curve (AP = {avg_precision:.2f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve')
        plt.legend(loc='lower left')
        plt.savefig(PLOT_DIR / "pr_curve.png")
        plt.close()
        logger.info(f"Saved Precision-Recall curve plot to {PLOT_DIR / 'pr_curve.png'}")

        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc')
        logger.info(f"Cross-validation ROC AUC scores: {cv_scores}")
        logger.info(f"Mean CV ROC AUC: {cv_scores.mean():.2f} (+/- {cv_scores.std() * 2:.2f})")

        return {
            'classification_reports': reports,
            'roc_auc': roc_auc,
            'avg_precision': avg_precision,
            'cv_scores': cv_scores,
            'train_roc_auc': train_roc_auc
        }
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise

def compute_feature_importance(model: Pipeline, X_test: pd.DataFrame, y_test: pd.DataFrame, feature_names: list) -> None:
    """Compute and save feature importance using SHAP and permutation importance."""
    try:
        # SHAP values
        explainer = shap.TreeExplainer(model.named_steps['classifier'])
        X_test_transformed = model.named_steps['preprocessor'].transform(X_test)
        shap_values = explainer.shap_values(X_test_transformed)
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test_transformed, feature_names=feature_names, show=False)
        plt.savefig(PLOT_DIR / "shap_summary.png")
        plt.close()
        logger.info(f"Saved SHAP summary plot to {PLOT_DIR / 'shap_summary.png'}")

        # Permutation importance
        perm_importance = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=RANDOM_SEED)
        perm_df = pd.DataFrame({
            'feature': feature_names,
            'importance': perm_importance.importances_mean,
            'std': perm_importance.importances_std
        }).sort_values('importance', ascending=False)
        perm_df.to_csv(OUTPUT_DIR / "permutation_importance.csv", index=False)
        logger.info(f"Saved permutation importance to {OUTPUT_DIR / 'permutation_importance.csv'}")
        logger.info(f"Top 3 features by permutation importance:\n{perm_df.head(3)}")
    except Exception as e:
        logger.error(f"Error computing feature importance: {str(e)}")
        raise

def save_model(model: Pipeline, model_path: Path) -> None:
    """Save the trained model to disk."""
    try:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
        logger.info(f"Saved model to {model_path}")
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise

def main():
    """Main function to orchestrate model training and evaluation."""
    try:
        # Load data
        final_df = load_data(DATA_DIR / "final_df-v2.csv")

        # Prepare features and target
        X, y, continuous_cols, cat_cols = prepare_features_and_target(final_df)

        # Calculate scale_pos_weight based on class imbalance
        class_ratio = (y == 0).sum() / (y == 1).sum()
        logger.info(f"Class imbalance ratio: {class_ratio:.2f}")

        # Create and train pipeline
        model_pipeline = create_pipeline(continuous_cols)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
        )
        logger.info(f"Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")
        model_pipeline.fit(X_train, y_train)
        logger.info("Model training completed")

        # Evaluate model
        metrics = evaluate_model(model_pipeline, X_train, y_train, X_test, y_test, thresholds=[0.3, 0.4, 0.5])

        # Compute feature importance
        compute_feature_importance(model_pipeline, X_test, y_test, X.columns)

        # Save model
        save_model(model_pipeline, MODEL_PATH)

        # Save metrics
        metrics_df = pd.DataFrame({
            'metric': ['ROC AUC', 'Average Precision', 'Mean CV ROC AUC', 'Training ROC AUC'],
            'value': [metrics['roc_auc'], metrics['avg_precision'], metrics['cv_scores'].mean(), metrics['train_roc_auc']]
        })
        metrics_df.to_csv(OUTPUT_DIR / "model_metrics.csv", index=False)
        logger.info(f"Saved model metrics to {OUTPUT_DIR / 'model_metrics.csv'}")

    except Exception as e:
        logger.error(f"Error in main pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()
