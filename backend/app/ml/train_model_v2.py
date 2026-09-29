"""
DiaSense AI — Production ML Training Pipeline v2
Dataset: India Diabetes Patient Dataset (25,500 records)
Author: DiaSense AI Engineering
Date: 2026-09-26

This script trains, evaluates, and saves a production-quality binary
classification pipeline for diabetes risk screening.

IMPORTANT: This is a SCREENING tool. Results must never be presented
as clinical diagnosis. Always recommend consulting a healthcare professional.
"""

import os
import json
import pickle
import warnings
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.model_selection import (
    train_test_split, StratifiedKFold, cross_validate,
    RandomizedSearchCV
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier, ExtraTreesClassifier,
    GradientBoostingClassifier, HistGradientBoostingClassifier,
    VotingClassifier
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve
)
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb

warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, "india_diabetes_patient_dataset.csv")
PIPELINE_PATH = os.path.join(CURRENT_DIR, "diabetes_pipeline_v2.pkl")
METADATA_PATH = os.path.join(CURRENT_DIR, "model_metadata_v2.json")
IMPORTANCE_PATH = os.path.join(CURRENT_DIR, "feature_importance_v2.json")

RANDOM_SEED = 42
TARGET_COL = "Diabetes"


# ─── Feature Definitions ──────────────────────────────────────────────────────
CATEGORICAL_FEATURES = ["Patient_Group", "Gender"]
BINARY_FEATURES = ["Family_History"]          # strictly 0/1
NUMERICAL_FEATURES = [
    "Age", "BMI", "Physical_Activity_Hours", "Daily_Sugar_Intake",
    "Fast_Food_Frequency", "Sleep_Hours", "Blood_Pressure",
    "HbA1c", "Fasting_Glucose", "Monthly_Income", "Month"
]
# Month is treated as numeric ordinal (1-12); correlates weakly so kept but not categorical
ALL_FEATURES = NUMERICAL_FEATURES + BINARY_FEATURES + CATEGORICAL_FEATURES


# ─── 1. Load & Profile Dataset ────────────────────────────────────────────────
def load_and_clean_dataset(path: str) -> pd.DataFrame:
    print("=" * 60)
    print("STEP 1: Loading and profiling dataset...")
    df = pd.read_csv(path)
    print(f"  Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"  Duplicates: {df.duplicated().sum()} — dropping them")
    df = df.drop_duplicates()

    # Clip extreme BMI outliers (78 values > 60 — physiologically implausible for valid data)
    bmi_before = (df["BMI"] > 60).sum()
    df.loc[df["BMI"] > 60, "BMI"] = np.nan   # treat as missing → imputed safely
    print(f"  Clipped {bmi_before} BMI values > 60 (set to NaN for imputation)")

    print(f"  Final shape after dedup/clip: {df.shape[0]} rows")
    print(f"  Target: {df[TARGET_COL].value_counts().to_dict()} | "
          f"Positive rate: {df[TARGET_COL].mean()*100:.1f}%")
    return df


# ─── 2. Feature Engineering ───────────────────────────────────────────────────
def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add clinically sensible interaction/category features.
    NOTE: All are computed from raw inputs — no leakage.
    """
    df = df.copy()

    # Ensure all numerical columns are float so None becomes np.nan (safe for pd.cut)
    num_cols = [
        "Age", "BMI", "Physical_Activity_Hours", "Daily_Sugar_Intake",
        "Fast_Food_Frequency", "Sleep_Hours", "Blood_Pressure",
        "HbA1c", "Fasting_Glucose", "Monthly_Income", "Month", "Family_History"
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # BMI categories (WHO standard)
    df["BMI_Category"] = pd.cut(
        df["BMI"],
        bins=[0, 18.5, 25, 30, 35, 100],
        labels=["Underweight", "Normal", "Overweight", "Obese_I", "Obese_II"],
        right=False
    ).astype(str)

    # HbA1c clinical categories
    df["HbA1c_Category"] = pd.cut(
        df["HbA1c"],
        bins=[0, 5.7, 6.5, 100],
        labels=["Normal", "Prediabetic", "Diabetic"],
        right=False
    ).astype(str)

    # Fasting glucose categories (ADA thresholds)
    df["Glucose_Category"] = pd.cut(
        df["Fasting_Glucose"],
        bins=[0, 100, 126, 1000],
        labels=["Normal", "Impaired", "Diabetic"],
        right=False
    ).astype(str)

    # Activity category
    df["Activity_Category"] = pd.cut(
        df["Physical_Activity_Hours"],
        bins=[-0.1, 2, 5, 100],
        labels=["Sedentary", "Moderate", "Active"]
    ).astype(str)

    # Key interaction: sugar × activity (lifestyle combo risk)
    df["Sugar_x_Activity"] = df["Daily_Sugar_Intake"] * (1.0 / (df["Physical_Activity_Hours"].clip(lower=0.1)))

    # Age × BMI interaction
    df["Age_x_BMI"] = df["Age"] * df["BMI"] / 1000.0   # normalized

    # Family_History × Age
    df["FamilyHistory_x_Age"] = df["Family_History"].fillna(0) * df["Age"]

    return df


# ─── 3. Build Preprocessing Pipeline ─────────────────────────────────────────
def build_preprocessor(X_train: pd.DataFrame):
    """
    All transformers are fitted on X_train only — zero leakage.
    """
    # Identify column groups in the training set
    cat_cols = [c for c in CATEGORICAL_FEATURES + ["BMI_Category", "HbA1c_Category",
                "Glucose_Category", "Activity_Category"] if c in X_train.columns]
    bin_cols = [c for c in BINARY_FEATURES if c in X_train.columns]
    num_cols = [c for c in X_train.columns if c not in cat_cols + bin_cols]

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    # For binary, use mode imputation (0 or 1)
    bin_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipeline, num_cols),
        ("bin", bin_pipeline, bin_cols),
        ("cat", cat_pipeline, cat_cols),
    ], remainder="drop")

    return preprocessor, num_cols, bin_cols, cat_cols


# ─── 4. Metric Helper ─────────────────────────────────────────────────────────
def compute_metrics(y_true, y_pred, y_prob, threshold=0.5) -> dict:
    pred_label = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, pred_label)
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    return {
        "accuracy":    round(float(accuracy_score(y_true, pred_label)), 4),
        "precision":   round(float(precision_score(y_true, pred_label, zero_division=0)), 4),
        "recall":      round(float(recall_score(y_true, pred_label, zero_division=0)), 4),
        "specificity": round(float(specificity), 4),
        "f1":          round(float(f1_score(y_true, pred_label, zero_division=0)), 4),
        "roc_auc":     round(float(roc_auc_score(y_true, y_prob)), 4),
        "pr_auc":      round(float(average_precision_score(y_true, y_prob)), 4),
        "confusion_matrix": cm.tolist(),
        "threshold_used": threshold,
    }


# ─── 5. Threshold Optimisation ───────────────────────────────────────────────
def find_best_threshold(y_val, y_prob_val, strategy="f1") -> float:
    """
    Search for the threshold that maximises F1 (balanced recall/precision).
    For a risk-screening application we do NOT blindly maximise recall at the
    cost of useless false-positive alerts.
    """
    thresholds = np.arange(0.25, 0.75, 0.01)
    best_t, best_score = 0.5, -1
    for t in thresholds:
        preds = (y_prob_val >= t).astype(int)
        score = f1_score(y_val, preds, zero_division=0)
        if score > best_score:
            best_score = score
            best_t = t
    print(f"  Optimal threshold (max-F1 on val set): {best_t:.2f}  F1={best_score:.4f}")
    return round(float(best_t), 2)


# ─── 6. Main Training Function ───────────────────────────────────────────────
def train_and_save_pipeline(dataset_path: str = DATASET_PATH,
                             pipeline_path: str = PIPELINE_PATH,
                             metadata_path: str = METADATA_PATH) -> dict:

    # ── Load ────────────────────────────────────────────────────────────────
    df_raw = load_and_clean_dataset(dataset_path)

    # ── Engineer features ───────────────────────────────────────────────────
    print("\nSTEP 2: Engineering features...")
    df = add_engineered_features(df_raw)

    feature_cols = [c for c in df.columns if c != TARGET_COL]
    X = df[feature_cols]
    y = df[TARGET_COL]

    # ── Split: 70% train  |  15% val  |  15% test  (stratified) ────────────
    print("\nSTEP 3: Stratified train/val/test split (70/15/15)...")
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=0.15, random_state=RANDOM_SEED, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=0.15 / 0.85,
        random_state=RANDOM_SEED, stratify=y_trainval
    )
    print(f"  Train: {len(X_train)}  Val: {len(X_val)}  Test: {len(X_test)}")

    # ── Build preprocessor (fit ONLY on train) ──────────────────────────────
    print("\nSTEP 4: Building & fitting preprocessor on training data only...")
    preprocessor, num_cols, bin_cols, cat_cols = build_preprocessor(X_train)
    preprocessor.fit(X_train, y_train)
    all_feature_names = num_cols + bin_cols + cat_cols
    print(f"  Features fed to models: {len(all_feature_names)}")

    # ── Model comparison with 5-fold CV ─────────────────────────────────────
    print("\nSTEP 5: Comparing candidate models (5-fold stratified CV)...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc", "average_precision"]

    candidates = {
        "LogisticRegression": Pipeline([
            ("pre", preprocessor),
            ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=RANDOM_SEED))
        ]),
        "RandomForest": Pipeline([
            ("pre", preprocessor),
            ("clf", RandomForestClassifier(n_estimators=200, random_state=RANDOM_SEED, n_jobs=-1))
        ]),
        "ExtraTrees": Pipeline([
            ("pre", preprocessor),
            ("clf", ExtraTreesClassifier(n_estimators=200, random_state=RANDOM_SEED, n_jobs=-1))
        ]),
        "GradientBoosting": Pipeline([
            ("pre", preprocessor),
            ("clf", GradientBoostingClassifier(n_estimators=200, random_state=RANDOM_SEED))
        ]),
        "HistGradientBoosting": Pipeline([
            ("pre", preprocessor),
            ("clf", HistGradientBoostingClassifier(max_iter=200, random_state=RANDOM_SEED))
        ]),
        "XGBoost": Pipeline([
            ("pre", preprocessor),
            ("clf", xgb.XGBClassifier(
                n_estimators=200, max_depth=6, learning_rate=0.1,
                subsample=0.8, colsample_bytree=0.8,
                eval_metric="logloss", random_state=RANDOM_SEED,
                use_label_encoder=False
            ))
        ]),
    }

    cv_results_summary = {}
    print(f"\n  {'Model':<25} {'Acc':>6} {'Prec':>6} {'Rec':>6} {'F1':>6} {'ROC-AUC':>8} {'PR-AUC':>7}")
    print("  " + "-" * 65)
    for name, pipe in candidates.items():
        try:
            cv_res = cross_validate(pipe, X_trainval, y_trainval, cv=cv,
                                    scoring=scoring, n_jobs=-1)
            row = {
                "accuracy_mean":   round(float(cv_res["test_accuracy"].mean()), 4),
                "accuracy_std":    round(float(cv_res["test_accuracy"].std()), 4),
                "precision_mean":  round(float(cv_res["test_precision"].mean()), 4),
                "recall_mean":     round(float(cv_res["test_recall"].mean()), 4),
                "f1_mean":         round(float(cv_res["test_f1"].mean()), 4),
                "roc_auc_mean":    round(float(cv_res["test_roc_auc"].mean()), 4),
                "pr_auc_mean":     round(float(cv_res["test_average_precision"].mean()), 4),
            }
            cv_results_summary[name] = row
            print(f"  {name:<25} {row['accuracy_mean']:>6.4f} {row['precision_mean']:>6.4f} "
                  f"{row['recall_mean']:>6.4f} {row['f1_mean']:>6.4f} "
                  f"{row['roc_auc_mean']:>8.4f} {row['pr_auc_mean']:>7.4f}")
        except Exception as e:
            print(f"  {name:<25} FAILED: {e}")

    # ── Select best model by ROC-AUC ────────────────────────────────────────
    # ROC-AUC balances sensitivity/specificity without being skewed by class imbalance
    best_name = max(cv_results_summary, key=lambda k: cv_results_summary[k]["roc_auc_mean"])
    print(f"\n  => Best model by ROC-AUC: {best_name} "
          f"({cv_results_summary[best_name]['roc_auc_mean']:.4f})")

    # ── Hyperparameter tuning on winner ─────────────────────────────────────
    print(f"\nSTEP 6: Hyperparameter tuning for {best_name}...")
    if "XGBoost" in best_name:
        param_dist = {
            "clf__n_estimators":    [200, 300, 400],
            "clf__max_depth":       [4, 5, 6, 7],
            "clf__learning_rate":   [0.05, 0.08, 0.1, 0.12],
            "clf__subsample":       [0.7, 0.8, 0.9],
            "clf__colsample_bytree":[0.7, 0.8, 0.9],
            "clf__min_child_weight":[1, 3, 5],
            "clf__gamma":           [0, 0.1, 0.2],
            "clf__reg_alpha":       [0, 0.1, 0.5],
            "clf__reg_lambda":      [1.0, 1.5, 2.0],
        }
    elif "HistGradientBoosting" in best_name:
        param_dist = {
            "clf__max_iter":        [150, 200, 300],
            "clf__max_depth":       [None, 5, 7],
            "clf__learning_rate":   [0.05, 0.1, 0.15],
            "clf__min_samples_leaf":[20, 30, 50],
            "clf__l2_regularization":[0.0, 0.1, 0.5],
        }
    elif "GradientBoosting" in best_name:
        param_dist = {
            "clf__n_estimators":    [200, 300, 400],
            "clf__max_depth":       [3, 4, 5, 6],
            "clf__learning_rate":   [0.05, 0.08, 0.1, 0.12],
            "clf__subsample":       [0.7, 0.8, 0.9, 1.0],
            "clf__min_samples_split":[2, 5, 10],
            "clf__min_samples_leaf":[1, 2, 4],
            "clf__max_features":    ["sqrt", "log2", None],
        }
    elif "RandomForest" in best_name or "ExtraTrees" in best_name:
        param_dist = {
            "clf__n_estimators":    [200, 300, 400],
            "clf__max_depth":       [None, 10, 15, 20],
            "clf__min_samples_split":[2, 5, 10],
            "clf__min_samples_leaf":[1, 2, 4],
            "clf__max_features":    ["sqrt", "log2"],
        }
    elif "LogisticRegression" in best_name:
        param_dist = {"clf__C": [0.01, 0.1, 1, 5, 10]}
    else:
        param_dist = {}

    base_pipe = candidates[best_name]
    search = RandomizedSearchCV(
        base_pipe, param_dist, n_iter=30, cv=cv,
        scoring="roc_auc", n_jobs=-1, random_state=RANDOM_SEED, verbose=0
    )
    search.fit(X_trainval, y_trainval)
    best_pipe = search.best_estimator_
    print(f"  Best params: {search.best_params_}")
    print(f"  Best CV ROC-AUC: {search.best_score_:.4f}")

    # ── Threshold optimisation on validation set ─────────────────────────────
    print("\nSTEP 7: Optimising decision threshold on validation set...")
    best_pipe.fit(X_train, y_train)   # refit on train only
    y_prob_val = best_pipe.predict_proba(X_val)[:, 1]
    decision_threshold = find_best_threshold(y_val, y_prob_val)

    # ── Final model: refit on ALL trainval data ──────────────────────────────
    print("\nSTEP 8: Refitting final model on full train+val data...")
    final_pipe = search.best_estimator_
    final_pipe.fit(X_trainval, y_trainval)

    # ── Evaluation on held-out test set ─────────────────────────────────────
    print("\nSTEP 9: Final evaluation on HELD-OUT TEST SET (never seen during training)...")
    y_prob_test = final_pipe.predict_proba(X_test)[:, 1]
    test_metrics = compute_metrics(y_test, None, y_prob_test, decision_threshold)

    print(f"\n  {'='*55}")
    print(f"  FINAL TEST METRICS (untouched hold-out)")
    print(f"  {'='*55}")
    print(f"  Accuracy    : {test_metrics['accuracy']:.4f}  ({test_metrics['accuracy']*100:.2f}%)")
    print(f"  Precision   : {test_metrics['precision']:.4f}")
    print(f"  Recall      : {test_metrics['recall']:.4f}")
    print(f"  Specificity : {test_metrics['specificity']:.4f}")
    print(f"  F1 Score    : {test_metrics['f1']:.4f}")
    print(f"  ROC-AUC     : {test_metrics['roc_auc']:.4f}")
    print(f"  PR-AUC      : {test_metrics['pr_auc']:.4f}")
    print(f"  Threshold   : {decision_threshold}")
    print(f"  Confusion   : {test_metrics['confusion_matrix']}")
    print(f"  {'='*55}")

    # ── Feature importances ──────────────────────────────────────────────────
    print("\nSTEP 10: Extracting feature importances...")
    feature_importance_dict = {}
    clf_step = final_pipe.named_steps.get("clf")
    if hasattr(clf_step, "feature_importances_"):
        raw_imp = clf_step.feature_importances_
        # map back to column names
        pre_step = final_pipe.named_steps.get("pre")
        try:
            # Get output feature names from ColumnTransformer
            out_names = pre_step.get_feature_names_out()
            feature_importance_dict = {
                str(out_names[i]).replace("num__", "").replace("bin__", "").replace("cat__", ""): round(float(raw_imp[i]), 5)
                for i in range(min(len(raw_imp), len(out_names)))
            }
        except Exception:
            feature_importance_dict = {f"feature_{i}": round(float(v), 5)
                                        for i, v in enumerate(raw_imp)}
        top10 = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        print("  Top 10 Features:")
        for fname, fimp in top10:
            print(f"    {fname:<35} {fimp:.5f}")

    # ── Save pipeline ────────────────────────────────────────────────────────
    print("\nSTEP 11: Saving production pipeline...")
    os.makedirs(CURRENT_DIR, exist_ok=True)
    with open(pipeline_path, "wb") as f:
        pickle.dump({
            "pipeline": final_pipe,
            "decision_threshold": decision_threshold,
            "feature_cols": feature_cols,
            "categorical_features": CATEGORICAL_FEATURES,
            "numerical_features": NUMERICAL_FEATURES,
            "binary_features": BINARY_FEATURES,
        }, f)
    print(f"  Pipeline saved: {pipeline_path}")

    # ── Save feature importances ─────────────────────────────────────────────
    with open(IMPORTANCE_PATH, "w") as f:
        json.dump(feature_importance_dict, f, indent=2)

    # ── Build & save metadata ────────────────────────────────────────────────
    metadata = {
        "model_version": "v2",
        "training_date": datetime.now().isoformat(),
        "dataset_name": "india_diabetes_patient_dataset.csv",
        "dataset_url": "https://www.kaggle.com/datasets/sridevilavanyacse/india-diabetes-patient-dataset",
        "total_rows_raw": int(df_raw.shape[0]) + int(df_raw.duplicated().sum()),
        "rows_after_dedup_and_cleaning": int(df.shape[0]),
        "positive_cases": int(y.sum()),
        "negative_cases": int((y == 0).sum()),
        "positive_rate_pct": round(float(y.mean() * 100), 1),
        "feature_names": feature_cols,
        "target_name": TARGET_COL,
        "train_size": int(len(X_trainval)),
        "val_size": int(len(X_val)),
        "test_size": int(len(X_test)),
        "selected_model": best_name,
        "best_cv_params": str(search.best_params_),
        "best_cv_roc_auc": round(float(search.best_score_), 4),
        "decision_threshold": decision_threshold,
        "threshold_strategy": "max-F1 on validation set",
        "cv_results_per_model": cv_results_summary,
        "final_test_metrics": test_metrics,
        "feature_importance_top10": dict(sorted(
            feature_importance_dict.items(), key=lambda x: x[1], reverse=True
        )[:10]),
        "random_seed": RANDOM_SEED,
        "important_disclaimer": (
            "This model is a health risk SCREENING tool only. "
            "It is not a clinical diagnostic device. "
            "Results must not be presented as a medical diagnosis. "
            "Always recommend consulting a qualified healthcare professional."
        ),
        "sklearn_version": "1.9.0",
        "xgboost_version": "3.4.1",
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata saved: {metadata_path}")

    # ── Also produce a backward-compat model_metrics.json ────────────────────
    compat_metrics = {
        "model_name": f"DiaSense India Diabetes Classifier ({best_name}) v2",
        "dataset": "India Diabetes Patient Dataset — 25,500 records",
        "dataset_samples": int(df.shape[0]),
        "accuracy": test_metrics["accuracy"],
        "accuracy_percentage": f"{test_metrics['accuracy']*100:.2f}%",
        "precision": test_metrics["precision"],
        "precision_percentage": f"{test_metrics['precision']*100:.2f}%",
        "recall": test_metrics["recall"],
        "recall_percentage": f"{test_metrics['recall']*100:.2f}%",
        "specificity": test_metrics["specificity"],
        "f1_score": test_metrics["f1"],
        "roc_auc": test_metrics["roc_auc"],
        "pr_auc": test_metrics["pr_auc"],
        "confusion_matrix": test_metrics["confusion_matrix"],
        "decision_threshold": decision_threshold,
        "cv_roc_auc_mean": cv_results_summary.get(best_name, {}).get("roc_auc_mean", None),
        "feature_importances": dict(sorted(
            feature_importance_dict.items(), key=lambda x: x[1], reverse=True
        )[:12]),
        "train_samples": int(len(X_trainval)),
        "test_samples": int(len(X_test)),
    }

    compat_path = os.path.join(CURRENT_DIR, "model_metrics.json")
    with open(compat_path, "w") as f:
        json.dump(compat_metrics, f, indent=2)

    print(f"\n{'='*60}")
    print("  TRAINING COMPLETE")
    print(f"  Artifacts:")
    print(f"    {pipeline_path}")
    print(f"    {metadata_path}")
    print(f"    {IMPORTANCE_PATH}")
    print(f"    {compat_path}")
    print(f"{'='*60}\n")

    return metadata


if __name__ == "__main__":
    train_and_save_pipeline()
