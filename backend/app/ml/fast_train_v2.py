"""
DiaSense AI — Fast Production Training Script
Uses best-known GradientBoosting params (from CV comparison).
Skips full RandomizedSearchCV to complete in ~2 minutes.
Run: python backend/app/ml/fast_train_v2.py
"""
import os, json, pickle, warnings
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)

warnings.filterwarnings("ignore")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "india_diabetes_patient_dataset.csv")
PIPELINE_PATH = os.path.join(CURRENT_DIR, "diabetes_pipeline_v2.pkl")
METADATA_PATH = os.path.join(CURRENT_DIR, "model_metadata_v2.json")
IMPORTANCE_PATH = os.path.join(CURRENT_DIR, "feature_importance_v2.json")
COMPAT_PATH = os.path.join(CURRENT_DIR, "model_metrics.json")

RANDOM_SEED = 42
TARGET_COL = "Diabetes"

CATEGORICAL_FEATURES = ["Patient_Group", "Gender"]
BINARY_FEATURES = ["Family_History"]
NUMERICAL_FEATURES = [
    "Age", "BMI", "Physical_Activity_Hours", "Daily_Sugar_Intake",
    "Fast_Food_Frequency", "Sleep_Hours", "Blood_Pressure",
    "HbA1c", "Fasting_Glucose", "Monthly_Income", "Month"
]


def add_engineered_features(df):
    df = df.copy()
    df["BMI_Category"] = pd.cut(
        df["BMI"], bins=[0, 18.5, 25, 30, 35, 100],
        labels=["Underweight", "Normal", "Overweight", "Obese_I", "Obese_II"], right=False
    ).astype(str)
    df["HbA1c_Category"] = pd.cut(
        df["HbA1c"], bins=[0, 5.7, 6.5, 100],
        labels=["Normal", "Prediabetic", "Diabetic"], right=False
    ).astype(str)
    df["Glucose_Category"] = pd.cut(
        df["Fasting_Glucose"], bins=[0, 100, 126, 1000],
        labels=["Normal", "Impaired", "Diabetic"], right=False
    ).astype(str)
    df["Activity_Category"] = pd.cut(
        df["Physical_Activity_Hours"], bins=[-0.1, 2, 5, 100],
        labels=["Sedentary", "Moderate", "Active"]
    ).astype(str)
    df["Sugar_x_Activity"] = df["Daily_Sugar_Intake"] * (1.0 / df["Physical_Activity_Hours"].clip(lower=0.1))
    df["Age_x_BMI"] = df["Age"] * df["BMI"] / 1000.0
    df["FamilyHistory_x_Age"] = df["Family_History"].fillna(0) * df["Age"]
    return df


def compute_metrics(y_true, y_prob, threshold):
    pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, pred)
    tn, fp, fn, tp = cm.ravel()
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    return {
        "accuracy":    round(float(accuracy_score(y_true, pred)), 4),
        "precision":   round(float(precision_score(y_true, pred, zero_division=0)), 4),
        "recall":      round(float(recall_score(y_true, pred, zero_division=0)), 4),
        "specificity": round(float(spec), 4),
        "f1":          round(float(f1_score(y_true, pred, zero_division=0)), 4),
        "roc_auc":     round(float(roc_auc_score(y_true, y_prob)), 4),
        "pr_auc":      round(float(average_precision_score(y_true, y_prob)), 4),
        "confusion_matrix": cm.tolist(),
        "threshold_used": float(threshold),
    }


def find_best_threshold(y_val, y_prob):
    best_t, best_f1 = 0.5, -1
    for t in np.arange(0.25, 0.75, 0.01):
        preds = (y_prob >= t).astype(int)
        score = f1_score(y_val, preds, zero_division=0)
        if score > best_f1:
            best_f1, best_t = score, t
    print(f"  Optimal threshold (max-F1): {best_t:.2f}  F1={best_f1:.4f}")
    return round(float(best_t), 2)


def train():
    print("=" * 60)
    print("DiaSense AI v2 — Fast Production Training")
    print("Model: GradientBoosting (best-known params from CV)")
    print("=" * 60)

    # Load & clean
    df = pd.read_csv(DATASET_PATH)
    df = df.drop_duplicates()
    df.loc[df["BMI"] > 60, "BMI"] = np.nan
    print(f"Dataset: {df.shape[0]} rows | Positive rate: {df[TARGET_COL].mean()*100:.1f}%")

    # Feature engineering
    df = add_engineered_features(df)
    feature_cols = [c for c in df.columns if c != TARGET_COL]
    X, y = df[feature_cols], df[TARGET_COL]

    # Split: 70 train / 15 val / 15 test
    X_tv, X_test, y_tv, y_test = train_test_split(X, y, test_size=0.15, random_state=RANDOM_SEED, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_tv, y_tv, test_size=0.15/0.85, random_state=RANDOM_SEED, stratify=y_tv)
    print(f"Split — Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")

    # Build preprocessor (fit on train ONLY)
    cat_cols = [c for c in CATEGORICAL_FEATURES + ["BMI_Category","HbA1c_Category","Glucose_Category","Activity_Category"] if c in X_train.columns]
    bin_cols = [c for c in BINARY_FEATURES if c in X_train.columns]
    num_cols = [c for c in X_train.columns if c not in cat_cols + bin_cols]

    preprocessor = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num_cols),
        ("bin", Pipeline([("imp", SimpleImputer(strategy="most_frequent"))]), bin_cols),
        ("cat", Pipeline([
            ("imp", SimpleImputer(strategy="most_frequent")),
            ("enc", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
        ]), cat_cols),
    ], remainder="drop")

    # Build pipeline with best-known GradientBoosting params
    pipeline = Pipeline([
        ("pre", preprocessor),
        ("clf", GradientBoostingClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.8,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features="sqrt",
            random_state=RANDOM_SEED,
        ))
    ])

    print("\nTraining GradientBoosting on train set...")
    pipeline.fit(X_train, y_train)

    # Threshold optimisation on val set
    print("\nOptimising threshold on validation set...")
    y_prob_val = pipeline.predict_proba(X_val)[:, 1]
    threshold = find_best_threshold(y_val, y_prob_val)

    # 5-fold CV on train+val for honest reporting
    print("\nRunning 5-fold CV on train+val...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    cv_res = cross_validate(pipeline, X_tv, y_tv, cv=cv,
                            scoring=["accuracy","f1","roc_auc","average_precision"])
    cv_roc = float(cv_res["test_roc_auc"].mean())
    cv_f1  = float(cv_res["test_f1"].mean())
    print(f"  CV ROC-AUC: {cv_roc:.4f} | CV F1: {cv_f1:.4f}")

    # Refit on full train+val
    print("\nRefitting on full train+val data...")
    pipeline.fit(X_tv, y_tv)

    # Final test-set evaluation
    print("\nEvaluating on held-out TEST SET...")
    y_prob_test = pipeline.predict_proba(X_test)[:, 1]
    m = compute_metrics(y_test, y_prob_test, threshold)

    print(f"\n{'='*55}")
    print("  FINAL TEST METRICS (untouched hold-out)")
    print(f"{'='*55}")
    print(f"  Accuracy    : {m['accuracy']:.4f}  ({m['accuracy']*100:.2f}%)")
    print(f"  Precision   : {m['precision']:.4f}")
    print(f"  Recall      : {m['recall']:.4f}")
    print(f"  Specificity : {m['specificity']:.4f}")
    print(f"  F1 Score    : {m['f1']:.4f}")
    print(f"  ROC-AUC     : {m['roc_auc']:.4f}")
    print(f"  PR-AUC      : {m['pr_auc']:.4f}")
    print(f"  Threshold   : {threshold}")
    print(f"  Confusion   : {m['confusion_matrix']}")
    print(f"{'='*55}")

    # Feature importance
    imp = pipeline.named_steps["clf"].feature_importances_
    try:
        out_names = preprocessor.get_feature_names_out()
        fi = {str(out_names[i]).split("__")[-1]: round(float(imp[i]), 5) for i in range(len(imp))}
    except Exception:
        fi = {f"feature_{i}": round(float(v), 5) for i, v in enumerate(imp)}

    top10 = dict(sorted(fi.items(), key=lambda x: x[1], reverse=True)[:10])
    print("\nTop 10 Feature Importances:")
    for name, val in top10.items():
        print(f"  {name:<35} {val:.5f}")

    # Save pipeline bundle
    bundle = {
        "pipeline": pipeline,
        "decision_threshold": threshold,
        "feature_cols": feature_cols,
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "binary_features": BINARY_FEATURES,
    }
    with open(PIPELINE_PATH, "wb") as f:
        pickle.dump(bundle, f)
    print(f"\nPipeline saved: {PIPELINE_PATH}")

    # Save feature importances
    with open(IMPORTANCE_PATH, "w") as f:
        json.dump(fi, f, indent=2)

    # Save full metadata
    metadata = {
        "model_version": "v2",
        "training_date": datetime.now().isoformat(),
        "dataset_name": "india_diabetes_patient_dataset.csv",
        "dataset_url": "https://www.kaggle.com/datasets/sridevilavanyacse/india-diabetes-patient-dataset",
        "rows_after_cleaning": int(df.shape[0]),
        "positive_cases": int(y.sum()),
        "positive_rate_pct": round(float(y.mean() * 100), 1),
        "feature_names": feature_cols,
        "target_name": TARGET_COL,
        "train_size": int(len(X_tv)),
        "val_size": int(len(X_val)),
        "test_size": int(len(X_test)),
        "selected_model": "GradientBoostingClassifier",
        "model_params": {
            "n_estimators": 300, "max_depth": 4, "learning_rate": 0.08,
            "subsample": 0.8, "min_samples_split": 5, "min_samples_leaf": 2,
            "max_features": "sqrt"
        },
        "cv_roc_auc_mean": round(cv_roc, 4),
        "cv_f1_mean": round(cv_f1, 4),
        "decision_threshold": threshold,
        "threshold_strategy": "max-F1 on validation set",
        "final_test_metrics": m,
        "feature_importance_top10": top10,
        "random_seed": RANDOM_SEED,
        "important_disclaimer": (
            "This model is a health risk SCREENING tool only. "
            "Results must not be presented as a medical diagnosis. "
            "Always recommend consulting a qualified healthcare professional."
        ),
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    # Backward-compat model_metrics.json
    compat = {
        "model_name": "DiaSense India Diabetes Classifier (GradientBoosting) v2",
        "dataset": "India Diabetes Patient Dataset — 25,010 records",
        "dataset_samples": int(df.shape[0]),
        "accuracy": m["accuracy"],
        "accuracy_percentage": f"{m['accuracy']*100:.2f}%",
        "precision": m["precision"],
        "precision_percentage": f"{m['precision']*100:.2f}%",
        "recall": m["recall"],
        "recall_percentage": f"{m['recall']*100:.2f}%",
        "specificity": m["specificity"],
        "f1_score": m["f1"],
        "roc_auc": m["roc_auc"],
        "pr_auc": m["pr_auc"],
        "confusion_matrix": m["confusion_matrix"],
        "decision_threshold": threshold,
        "cv_roc_auc_mean": round(cv_roc, 4),
        "feature_importances": top10,
        "train_samples": int(len(X_tv)),
        "test_samples": int(len(X_test)),
    }
    with open(COMPAT_PATH, "w") as f:
        json.dump(compat, f, indent=2)

    print(f"\nAll artifacts saved. Training complete.")
    return metadata


if __name__ == "__main__":
    train()
