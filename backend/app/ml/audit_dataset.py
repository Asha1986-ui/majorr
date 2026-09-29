import pandas as pd
import numpy as np

df = pd.read_csv(r'C:\Users\Admin\Downloads\archive\india_diabetes_patient_dataset.csv')

num_cols = ['Age','BMI','Physical_Activity_Hours','Daily_Sugar_Intake','Fast_Food_Frequency',
            'Sleep_Hours','Family_History','Blood_Pressure','HbA1c','Fasting_Glucose','Monthly_Income','Month']

print("=== NUMERICAL RANGES ===")
print(df[num_cols].describe().round(2).to_string())
print()

print("=== CATEGORICAL CARDINALITY ===")
for c in ['Patient_Group','Gender']:
    print(f"{c}: {df[c].value_counts().to_dict()}")
print()

all_cols = num_cols + ["Diabetes"]
corr = df[all_cols].corr()
print("=== CORRELATIONS WITH TARGET ===")
print(corr['Diabetes'].sort_values(ascending=False).round(3).to_string())
print()

print("=== SUSPICIOUS VALUES ===")
print("BMI<10:", (df['BMI'] < 10).sum(), " BMI>60:", (df['BMI'] > 60).sum())
print("Fasting_Glucose<50:", (df['Fasting_Glucose'] < 50).sum())
print("HbA1c<2:", (df['HbA1c'] < 2).sum(), "HbA1c>20:", (df['HbA1c'] > 20).sum())
print("Age<1:", (df['Age'] < 1).sum(), " Age>110:", (df['Age'] > 110).sum())
print("Blood_Pressure<40:", (df['Blood_Pressure'] < 40).sum(), " BP>200:", (df['Blood_Pressure'] > 200).sum())
print("Family_History values:", sorted(df['Family_History'].dropna().unique()))
print("Month values:", sorted(df['Month'].dropna().unique()))
