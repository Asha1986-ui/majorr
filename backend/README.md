# DiaSense AI - Enterprise Production Backend & Integration

A production-ready, scalable backend built with **Python FastAPI**, **MySQL / SQLite**, **SQLAlchemy ORM**, **XGBoost ML model**, and **JWT Authentication** following strict **Clean Architecture** (Routes → Services → Repositories → Database).

Integrated seamlessly with the React frontend using **Axios** without changing any UI design, CSS styling, colors, fonts, layout, or component structures.

---

## Technical Stack & Architecture

- **Backend Framework:** Python FastAPI (v0.110+)
- **Database ORM:** SQLAlchemy (v2.0+) + Alembic migrations
- **Machine Learning:** XGBoost (`diabetes_model.pkl`) + Scikit-Learn
- **Security:** JWT Tokens (Access & Refresh), bcrypt password hashing
- **Validation:** Pydantic (v2.6+)
- **Testing:** Pytest + TestClient
- **Documentation:** Interactive OpenAPI Swagger UI (`/docs`) & ReDoc (`/redoc`)

---

## Directory Structure

```
DiaSenseAI/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config/
│   │   │   ├── database.py
│   │   │   ├── settings.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── assessment.py
│   │   │   ├── prediction.py
│   │   │   ├── diet_plan.py
│   │   │   └── contact.py
│   │   ├── schemas/
│   │   │   ├── user_schema.py
│   │   │   ├── assessment_schema.py
│   │   │   ├── prediction_schema.py
│   │   │   ├── auth_schema.py
│   │   │   └── contact_schema.py
│   │   ├── routes/
│   │   │   ├── auth_routes.py
│   │   │   ├── user_routes.py
│   │   │   ├── assessment_routes.py
│   │   │   ├── prediction_routes.py
│   │   │   ├── dashboard_routes.py
│   │   │   ├── diet_routes.py
│   │   │   └── contact_routes.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── assessment_service.py
│   │   │   ├── prediction_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── diet_service.py
│   │   │   └── email_service.py
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   ├── assessment_repository.py
│   │   │   ├── prediction_repository.py
│   │   │   └── diet_repository.py
│   │   ├── ml/
│   │   │   ├── diabetes_model.pkl
│   │   │   ├── prediction.py
│   │   │   ├── preprocessing.py
│   │   │   ├── features.py
│   │   │   └── train_model.py
│   │   └── utils/
│   │       ├── logger.py
│   │       ├── response.py
│   │       ├── validators.py
│   │       └── helper.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_prediction.py
│   │   └── test_dashboard.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   └── run.py
└── frontend/ (React application - UI design 100% preserved)
```

---

## Setup & Local Execution Guide

### 1. Environment Configuration
Create a `.env` file inside `backend/`:
```env
APP_NAME="DiaSense AI Backend"
APP_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database Configuration
# Primary MySQL connection string:
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/diasense_db
# Zero-setup local SQLite fallback:
DATABASE_URL=sqlite:///./diasense.db

# JWT Security
SECRET_KEY=diasense_super_secret_jwt_key_2026_x99!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 2. Install Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

### 3. Train ML Model (Automatic on First Run)
```bash
python -m app.ml.train_model
```

### 4. Run Development / Production Server
```bash
python run.py
```
The server will start at `http://localhost:8000`.
- Interactive Swagger UI: `http://localhost:8000/docs`
- Interactive ReDoc: `http://localhost:8000/redoc`

### 5. Execute Automated Pytest Suite
```bash
pytest tests/ -v
```

---

## API Endpoints Summary

| Module | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/auth/register` | User account registration |
| **Auth** | `POST` | `/api/auth/login` | Authenticate user & issue JWT |
| **Auth** | `GET` | `/api/auth/profile` | Retrieve logged-in profile |
| **Auth** | `PUT` | `/api/auth/profile` | Update profile information |
| **Assessment** | `POST` | `/api/assessment` | Store health assessment |
| **Assessment** | `GET` | `/api/assessment/history` | User assessment history |
| **Assessment** | `GET` | `/api/assessment/{id}` | Get specific assessment |
| **Prediction** | `POST` | `/api/prediction` | Run XGBoost ML prediction |
| **Prediction** | `GET` | `/api/prediction/latest` | Retrieve latest ML analysis |
| **Dashboard** | `GET` | `/api/dashboard` | Aggregated dashboard data |
| **Diet** | `GET` | `/api/diet/latest` | Retrieve active diet plan |
| **Contact** | `POST` | `/api/contact` | Submit contact message |
| **System** | `GET` | `/health` | Server status health check |
