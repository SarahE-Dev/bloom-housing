import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve, confusion_matrix
from imblearn.combine import SMOTEENN
from imblearn.pipeline import Pipeline as ImbPipeline
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt

# 1) Load & clean
df = pd.read_csv('ahs2023n.csv')
# keep only valid HIHMLESSNESS codes and map to 0/1
df = df[df['HIHMLESSNESS'].isin(["'0'","'1'","'2'"])]
df['HIHMLESSNESS'] = df['HIHMLESSNESS'].map({"'0'":0,"'1'":1,"'2'":1}).astype(int)

# convert any string‐encoded numerics
def convert_to_numeric(s):
    return pd.to_numeric(s.str.strip("'")
                           .replace(['-6','-9',''], np.nan),
                           errors='coerce')

for col in ['HINCP','TOTHCAMT','HHAGE','HINUMOVE']:
    if col in df.columns and df[col].dtype == object:
        df[col] = convert_to_numeric(df[col])

# 1a) Group sparse HHRACE categories into 'Other'
race_counts = df['HHRACE'].value_counts()
small = race_counts[race_counts < 100].index
df['HHRACE'] = df['HHRACE'].replace(small, 'Other')

# features & target
features = ['HINCP','TOTHCAMT','HHAGE','TENURE','HHRACE',
            'DISHH','FS','PERPOVLVL','HINUMOVE','HIBEHINDFRQ']
features = [f for f in features if f in df.columns]
X = df[features]
y = df['HIHMLESSNESS']

# 2) Split
X_train_val, X_test, y_train_val, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_val, y_train_val, test_size=0.2, stratify=y_train_val, random_state=42)

# 3) Preprocessor
numeric_feats = [c for c in ['HINCP','TOTHCAMT','HHAGE','HINUMOVE'] if c in X.columns]
categorical_feats = [c for c in features if c not in numeric_feats]

num_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])
cat_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])
preprocessor = ColumnTransformer([
    ('num', num_pipe, numeric_feats),
    ('cat', cat_pipe, categorical_feats)
])

# 4) Build imbalanced‐learn pipeline
smoteenn = SMOTEENN(random_state=42)
xgb_clf = xgb.XGBClassifier(objective='binary:logistic', use_label_encoder=False, eval_metric='logloss')

imb_pipeline = ImbPipeline([
    ('preprocessor', preprocessor),
    ('smoteenn', smoteenn),
    ('xgb', xgb_clf)
])

# 5) Hyperparameter tuning
param_dist = {
    'xgb__n_estimators': [100, 200, 300],
    'xgb__max_depth': [2, 3, 5],
    'xgb__learning_rate': [0.01, 0.05, 0.1],
    'xgb__subsample': [0.6, 0.8, 1.0],
    'xgb__colsample_bytree': [0.6, 0.8, 1.0],
    'xgb__gamma': [0, 1, 5],
    'xgb__reg_alpha': [0, 1, 3],
    'xgb__reg_lambda': [1, 3, 5]
}
search = RandomizedSearchCV(
    imb_pipeline,
    param_distributions=param_dist,
    n_iter=20,
    scoring='roc_auc',
    cv=5,
    verbose=2,
    random_state=42,
    n_jobs=-1
)
search.fit(X_train, y_train)
print("Best params:", search.best_params_)

# 6) Threshold optimization on validation set
best_pipe = search.best_estimator_
# get validation probs
val_probs = best_pipe.predict_proba(X_val)[:,1]
prec, rec, thresh = precision_recall_curve(y_val, val_probs)
f1 = 2*prec*rec/(prec+rec+1e-9)
best_thresh = thresh[np.argmax(f1)]
print("Best threshold (F1):", best_thresh)

# 7) Final evaluation on test set
test_probs = best_pipe.predict_proba(X_test)[:,1]
y_pred = (test_probs >= best_thresh).astype(int)

print("Test AUC-ROC:", roc_auc_score(y_test, test_probs))
print("Classification Report @ thresh=", best_thresh)
print(classification_report(y_test, y_pred, zero_division=0))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 8) Fairness by HHRACE
# re-transform test features with preprocessor only
X_test_prep = best_pipe.named_steps['preprocessor'].transform(X_test)
feat_names = best_pipe.named_steps['preprocessor'].get_feature_names_out()
X_test_df = pd.DataFrame(X_test_prep, columns=feat_names, index=X_test.index)
y_test_idxed = y_test.reset_index(drop=True)
y_pred_idxed = pd.Series(y_pred, index=y_test.index).reset_index(drop=True)

for col in feat_names:
    if col.startswith('cat__HHRACE'):
        mask = X_test_df[col] == 1
        if mask.sum() > 20:
            print(f"--- Metrics for {col} (n={mask.sum()}):")
            print(classification_report(y_test_idxed[mask], y_pred_idxed[mask], zero_division=0))

# 9) Save artifacts
joblib.dump(best_pipe.named_steps['preprocessor'], 'preprocessor.joblib')
joblib.dump(best_pipe.named_steps['xgb'], 'xgb_classifier.joblib')
print("Saved preprocessor and model.")
