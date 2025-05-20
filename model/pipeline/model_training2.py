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
    """Load the processed dataset."""
    try:
        df = pd.read_csv(file_path)
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
        X = df.drop(columns=['at_risk'])
        y = df['at_risk']
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
                    scale_pos_weight=1.5,
                    random_state=RANDOM_SEED,
                    objective="binary:logistic",
                    eval_metric=["logloss", "auc"],
                ),
            ),
        ])
        logger.info("Created model pipeline")
        return pipeline
    except Exception as e:
        logger.error(f"Error creating pipeline: {str(e)}")
        raise

def evaluate_model(model: Pipeline, X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, y_test: pd.DataFrame, threshold: float = 0.4) -> dict:
    """Evaluate the model and generate metrics and plots."""
    try:
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        y_pred_custom = (y_pred_proba > threshold).astype(int)

        # Classification report
        report = classification_report(y_test, y_pred_custom, output_dict=True)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred_custom))

        # Confusion matrix
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
            'classification_report': report,
            'roc_auc': roc_auc,
            'avg_precision': avg_precision,
            'cv_scores': cv_scores
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
    except Exception as e:
        logger.error(f"Error computing feature importance: {str(e)}")
        raise

def save_model(model: Pipeline, model_path: Path) -> None:
    """Save the trained model to disk."""
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
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

        # Create and train pipeline
        model_pipeline = create_pipeline(continuous_cols)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
        )
        logger.info(f"Training set shape: {X_train.shape}, Test set shape: {X_test.shape}")
        model_pipeline.fit(X_train, y_train)
        logger.info("Model training completed")

        # Evaluate model
        metrics = evaluate_model(model_pipeline, X_train, y_train, X_test, y_test)

        # Compute feature importance
        compute_feature_importance(model_pipeline, X_test, y_test, X.columns)

        # Save model
        save_model(model_pipeline, MODEL_PATH)

        # Save metrics
        metrics_df = pd.DataFrame({
            'metric': ['ROC AUC', 'Average Precision', 'Mean CV ROC AUC'],
            'value': [metrics['roc_auc'], metrics['avg_precision'], metrics['cv_scores'].mean()]
        })
        metrics_df.to_csv(OUTPUT_DIR / "model_metrics.csv", index=False)
        logger.info(f"Saved model metrics to {OUTPUT_DIR / 'model_metrics.csv'}")

    except Exception as e:
        logger.error(f"Error in main pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()