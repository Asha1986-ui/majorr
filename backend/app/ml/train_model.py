import os
import json
import pickle
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, average_precision_score
)
from app.utils.logger import logger


CAT_COLS = ["Patient_Group", "Gender"]
NUM_COLS = [
    "Age", "BMI", "Physical_Activity_Hours", "Daily_Sugar_Intake",
    "Fast_Food_Frequency", "Sleep_Hours", "Family_History", "Blood_Pressure",
    "HbA1c", "Fasting_Glucose", "Monthly_Income", "Month",
    "HbA1c_FastingGlucose", "Glucose_BMI", "Age_BMI", "High_HbA1c", "High_Glucose", "Lifestyle_Index"
]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes clinically-grounded interaction factors and metabolic risk indices.
    """
    data = df.copy()

    # Numeric safeguards
    data["HbA1c"] = pd.to_numeric(data.get("HbA1c"), errors="coerce")
    data["Fasting_Glucose"] = pd.to_numeric(data.get("Fasting_Glucose"), errors="coerce")
    data["BMI"] = pd.to_numeric(data.get("BMI"), errors="coerce")
    data["Age"] = pd.to_numeric(data.get("Age"), errors="coerce")
    data["Daily_Sugar_Intake"] = pd.to_numeric(data.get("Daily_Sugar_Intake"), errors="coerce")
    data["Fast_Food_Frequency"] = pd.to_numeric(data.get("Fast_Food_Frequency"), errors="coerce")
    data["Physical_Activity_Hours"] = pd.to_numeric(data.get("Physical_Activity_Hours"), errors="coerce")

    data["HbA1c_FastingGlucose"] = data["HbA1c"] * data["Fasting_Glucose"]
    data["Glucose_BMI"] = data["Fasting_Glucose"] * data["BMI"]
    data["Age_BMI"] = data["Age"] * data["BMI"]
    data["High_HbA1c"] = (data["HbA1c"] >= 6.5).astype(float)
    data["High_Glucose"] = (data["Fasting_Glucose"] >= 126.0).astype(float)
    data["Lifestyle_Index"] = (data["Daily_Sugar_Intake"].fillna(30.0) + data["Fast_Food_Frequency"].fillna(2.0) * 5.0) / (data["Physical_Activity_Hours"].fillna(1.0) + 1.0)

    return data


def build_preprocessor() -> ColumnTransformer:
    """
    Builds an end-to-end ColumnTransformer with imputation and encoding.
    """
    cat_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    num_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    return ColumnTransformer(
        transformers=[
            ("cat", cat_transformer, CAT_COLS),
            ("num", num_transformer, NUM_COLS)
        ]
    )


def train_and_save_model(model_path: str):
    """
    Trains an XGBoost Classifier on the 25,500 Indian Diabetes Patient dataset.
    Saves a serialized Pipeline containing preprocessor + model.
    """
    logger.info("Training XGBoost Classifier on 25,500-sample India Diabetes Patient Dataset...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "india_diabetes_patient_dataset.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    logger.info(f"Loaded: {len(df)} samples, {int(df['Diabetes'].sum())} positive cases.")

    # Apply feature engineering
    df_feat = engineer_features(df)

    X = df_feat[CAT_COLS + NUM_COLS]
    y = df_feat["Diabetes"]

    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )

    preprocessor = build_preprocessor()

    clf = xgb.XGBClassifier(
        n_estimators=350,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.2,
        reg_lambda=1.2,
        scale_pos_weight=1.15,
        random_state=42,
        eval_metric="logloss",
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", clf)
    ])

    logger.info("Fitting end-to-end ML Pipeline (Preprocessor + XGBoost)...")
    pipeline.fit(X_train, y_train)

    # Evaluate on holdout test set
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    optimal_threshold = 0.45
    y_pred = (y_prob >= optimal_threshold).astype(int)

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    auc = float(roc_auc_score(y_test, y_prob))
    pr_auc = float(average_precision_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()

    tn, fp = int(cm[0][0]), int(cm[0][1])
    specificity = round(tn / (tn + fp), 4) if (tn + fp) > 0 else None

    # 5-fold cross validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="roc_auc")
    cv_mean = float(cv_scores.mean())
    cv_std = float(cv_scores.std())

    metrics = {
        "model_name": "DiaSense Indian Clinical Diabetes Risk Predictor",
        "model_version": "2.0",
        "dataset": "India Diabetes Patient Dataset (25,500 records)",
        "dataset_samples": len(df),
        "target": "Diabetes",
        "threshold": optimal_threshold,
        "accuracy": round(acc, 4),
        "accuracy_percentage": f"{acc * 100:.2f}%",
        "precision": round(prec, 4),
        "precision_percentage": f"{prec * 100:.2f}%",
        "recall": round(rec, 4),
        "recall_percentage": f"{rec * 100:.2f}%",
        "specificity": specificity,
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": cm,
        "cv_roc_auc_mean": round(cv_mean, 4),
        "cv_roc_auc_std": round(cv_std, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "predictors": {
            "categorical": CAT_COLS,
            "numerical": NUM_COLS
        }
    }

    logger.info("==================================================")
    logger.info(" DIASENSE AI — INDIA DATASET ML MODEL METRICS")
    logger.info(f" Dataset      : {metrics['dataset']}")
    logger.info(f" Accuracy     : {metrics['accuracy_percentage']}")
    logger.info(f" Precision    : {metrics['precision_percentage']}")
    logger.info(f" Recall       : {metrics['recall_percentage']}")
    logger.info(f" Specificity  : {metrics['specificity']}")
    logger.info(f" F1 Score     : {metrics['f1_score']}")
    logger.info(f" ROC AUC      : {metrics['roc_auc']}")
    logger.info(f" CV ROC-AUC   : {cv_mean:.4f} +/- {cv_std:.4f}")
    logger.info("==================================================")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)

    metrics_path = os.path.join(os.path.dirname(model_path), "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    logger.info(f"Pipeline saved to: {model_path}")
    logger.info(f"Metrics saved to : {metrics_path}")
    return pipeline, metrics


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_pkl = os.path.join(current_dir, "diabetes_model.pkl")
    train_and_save_model(target_pkl)
