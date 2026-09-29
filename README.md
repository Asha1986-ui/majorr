# DiaSense AI — AI-Assisted Diabetes Risk Screening & Health Guidance Platform

[![Python Version](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-cyan.svg)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-orange.svg)](https://xgboost.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**DiaSense AI** is an enterprise-grade full-stack AI healthcare web platform designed for early **diabetes risk prediction**, **clinical feature explainability**, and **personalized lifestyle guidance**. It combines an **XGBoost machine learning classifier** trained on the authentic Pima Indians Diabetes Dataset with a modern **React 19** frontend, **FastAPI** backend, and automated **ReportLab PDF report generation**.

---

## 🌟 Executive Key Features

- 🧠 **Authentic XGBoost Machine Learning Model**: Trained on the 768-sample Pima Indians Diabetes Dataset (NIDDK) with 75.97% accuracy, 82.83% ROC-AUC, and full evaluation metrics.
- 📊 **Clinical Feature Explainability**: Evaluates physiological feature impacts (Glucose, BMI, Diastolic BP, Age, Insulin) to explain risk classifications.
- 📐 **Real-Time Auto BMI Calculation**: Automatically computes Body Mass Index as height (cm) and weight (kg) are entered.
- 📄 **On-Demand PDF Report Engine**: Generates downloadable clinical PDF health summary reports using ReportLab.
- 🔒 **Enterprise Security & Authorization**: OAuth2 JWT token authentication, Bcrypt password hashing, Pydantic input range validation, and strict IDOR authorization protection.
- 🥗 **Personalized Nutrition & Exercise Prescriptions**: Day-by-day filterable meal plans and risk-aware physical activity guidance.
- 📱 **Modern Healthcare SaaS UI**: Fully responsive glassmorphism interface across desktop, tablet, and mobile breakpoints.

---

## 📐 System Architecture

```text
               ┌────────────────────────────────────────────────────────┐
               │              React 19 + Vite Frontend                  │
               │  (Home, Dashboard, Stepper Assessment, Result, PDF)    │
               └───────────────────────────┬────────────────────────────┘
                                           │  REST API Calls (JWT Bearer)
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │                 FastAPI Backend Service                │
               │  (/api/auth, /api/assessments, /api/reports, /health)  │
               └───────────┬──────────────────────────────┬─────────────┘
                           │                              │
                           ▼                              ▼
             ┌──────────────────────────┐    ┌──────────────────────────┐
             │ SQLite / SQLAlchemy ORM  │    │  XGBoost Classifier Model│
             │ (User, Assessment, Pred) │    │   (Pima Dataset Trained) │
             └──────────────────────────┘    └──────────────────────────┘
```

---

## 🔬 Machine Learning Pipeline & Metrics

The ML classification pipeline utilizes **XGBoost** trained on the authentic **Pima Indians Diabetes Dataset** (768 patient samples).

### Model Performance Metrics (Evaluated on 20% Stratified Test Holdout)
| Metric | Value | Clinical Significance |
|---|---|---|
| **Accuracy Score** | **75.97%** | Overall correct classification rate on holdout test set |
| **Precision** | **68.09%** | Positive predictive value for diabetic classification |
| **Recall (Sensitivity)** | **59.26%** | Ability to detect true high-risk cases |
| **F1 Score** | **0.6337** | Harmonic mean of precision and recall |
| **ROC-AUC Index** | **0.8283** | Discrimination capacity between diabetic and non-diabetic profiles |

*Note: Data preprocessing cleans zero values in physiological columns (Glucose, BP, SkinThickness, Insulin, BMI) with column medians before training.*

---

## 🛠️ Technology Stack

- **Frontend**: React 19, Vite 8, Tailwind CSS v4, Framer Motion, Recharts, React Icons, Axios
- **Backend**: FastAPI 0.110, Python 3.14, SQLAlchemy ORM, Pydantic v2, Passlib (Bcrypt), Python-Jose (JWT)
- **PDF Engine**: ReportLab PDF Generation Library
- **Machine Learning**: XGBoost, Scikit-Learn, Pandas, NumPy
- **Testing**: Pytest automated backend suite (Auth, IDOR, ML inference, Report tests)

---

## 🚀 Installation & Running Guide

### 1. Prerequisites
- **Python 3.10+** (Python 3.14 supported)
- **Node.js 18+** & **npm**

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Train XGBoost Model on Pima Dataset
$env:PYTHONPATH="."
python app/ml/train_model.py

# Run FastAPI Server
python run.py
```
*Backend API will run on `http://localhost:8000`. Swagger API docs available at `http://localhost:8000/docs`.*

### 3. Frontend Setup
```bash
cd frontend

# Install Node modules
npm install

# Start Vite Development Server
npm run dev
```
*Frontend web application will run on `http://localhost:5173`.*

---

## 🧪 Automated Testing

Execute the backend test suite covering authentication, IDOR security checks, prediction pipeline, and report generation:

```bash
cd backend
$env:PYTHONPATH="."
pytest
```

To run frontend build verification:
```bash
cd frontend
npm run build
```

---

## ⚖️ Academic & Medical Disclaimer

DiaSense AI provides **AI-assisted risk screening estimations** and **lifestyle guidance** based on machine learning classification models. It is **NOT** a substitute for professional medical diagnosis, laboratory blood testing (HbA1c / FBG), or doctor consultation.
