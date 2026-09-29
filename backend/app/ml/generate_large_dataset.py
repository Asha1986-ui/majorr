import os
import pandas as pd
import numpy as np


def generate_large_diabetes_dataset(output_path: str, num_samples: int = 2500, random_seed: int = 42):
    """
    Generates an expanded 2,500-sample clinical diabetes dataset based on realistic
    physiological correlations (Glucose, Blood Pressure, Insulin, BMI, Age, Pedigree, Pregnancies).
    """
    np.random.seed(random_seed)

    # Base authentic distributions: 35% Positive (Diabetic), 65% Negative (Non-Diabetic)
    num_diabetic = int(num_samples * 0.35)
    num_healthy = num_samples - num_diabetic

    # Healthy Population Parameters
    healthy_glucose = np.random.normal(loc=98, scale=14, size=num_healthy)
    healthy_bp = np.random.normal(loc=70, scale=8, size=num_healthy)
    healthy_skin = np.random.normal(loc=20, scale=6, size=num_healthy)
    healthy_insulin = np.random.normal(loc=80, scale=25, size=num_healthy)
    healthy_bmi = np.random.normal(loc=24.5, scale=3.5, size=num_healthy)
    healthy_dpf = np.random.exponential(scale=0.25, size=num_healthy) + 0.08
    healthy_age = np.random.randint(low=21, high=60, size=num_healthy)
    healthy_pregnancies = np.random.poisson(lam=1.5, size=num_healthy)

    # Diabetic Population Parameters
    diabetic_glucose = np.random.normal(loc=155, scale=22, size=num_diabetic)
    diabetic_bp = np.random.normal(loc=82, scale=10, size=num_diabetic)
    diabetic_skin = np.random.normal(loc=32, scale=8, size=num_diabetic)
    diabetic_insulin = np.random.normal(loc=180, scale=45, size=num_diabetic)
    diabetic_bmi = np.random.normal(loc=33.5, scale=4.8, size=num_diabetic)
    diabetic_dpf = np.random.exponential(scale=0.45, size=num_diabetic) + 0.20
    diabetic_age = np.random.randint(low=28, high=70, size=num_diabetic)
    diabetic_pregnancies = np.random.poisson(lam=3.8, size=num_diabetic)

    # Combine arrays
    pregnancies = np.concatenate([healthy_pregnancies, diabetic_pregnancies])
    glucose = np.clip(np.concatenate([healthy_glucose, diabetic_glucose]), 55, 200)
    bp = np.clip(np.concatenate([healthy_bp, diabetic_bp]), 40, 122)
    skin = np.clip(np.concatenate([healthy_skin, diabetic_skin]), 7, 60)
    insulin = np.clip(np.concatenate([healthy_insulin, diabetic_insulin]), 15, 600)
    bmi = np.clip(np.concatenate([healthy_bmi, diabetic_bmi]), 16.0, 50.0)
    dpf = np.clip(np.concatenate([healthy_dpf, diabetic_dpf]), 0.08, 2.40)
    age = np.clip(np.concatenate([healthy_age, diabetic_age]), 21, 80)
    outcome = np.concatenate([np.zeros(num_healthy, dtype=int), np.ones(num_diabetic, dtype=int)])

    df = pd.DataFrame({
        "Pregnancies": pregnancies,
        "Glucose": np.round(glucose, 1),
        "BloodPressure": np.round(bp, 1),
        "SkinThickness": np.round(skin, 1),
        "Insulin": np.round(insulin, 1),
        "BMI": np.round(bmi, 1),
        "DiabetesPedigreeFunction": np.round(dpf, 3),
        "Age": age,
        "Outcome": outcome
    })

    # Shuffle dataset rows
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated expanded dataset with {len(df)} records at {output_path}")
    return df


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_csv = os.path.join(current_dir, "pima-indians-diabetes-large.csv")
    generate_large_diabetes_dataset(target_csv, num_samples=2500)
