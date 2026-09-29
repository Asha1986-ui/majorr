from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config.settings import settings
from app.config.database import init_db
from app.utils.logger import logger
from app.utils.response import error_response, success_response

from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.assessment_routes import router as assessment_router
from app.routes.prediction_routes import router as prediction_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.diet_routes import router as diet_router
from app.routes.contact_routes import router as contact_router
from app.routes.report_routes import router as report_router
from app.routes.chatbot_routes import router as chatbot_router
from app.routes.food_routes import router as food_router
from app.routes.nearby_care_routes import router as nearby_care_router
from app.routes.smart_assessment_routes import router as smart_assessment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Tables
    logger.info("Initializing database tables...")
    init_db()
    
    # Initialize & Pre-load ML Prediction Model & log Accuracy Score
    from app.ml.prediction import get_model_metrics
    metrics = get_model_metrics()
    acc_pct = metrics.get("accuracy_percentage", "N/A")
    acc = metrics.get("accuracy", "N/A")
    logger.info("==================================================")
    logger.info(" DiaSense AI ML Prediction Model Ready")
    logger.info(f" Model Accuracy Score: {acc_pct} ({acc})")
    logger.info("==================================================")
    yield
    logger.info("Shutting down DiaSense AI Backend...")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Clean Architecture FastAPI Backend for DiaSense AI Diabetes Prediction System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All Module Routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(assessment_router)
app.include_router(prediction_router)
app.include_router(dashboard_router)
app.include_router(diet_router)
app.include_router(contact_router)
app.include_router(report_router)
app.include_router(chatbot_router)
app.include_router(food_router)
app.include_router(nearby_care_router)
app.include_router(smart_assessment_router)


# Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP Exception {exc.status_code} at {request.url.path}: {exc.detail}")
    return error_response(
        message=str(exc.detail),
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation Error at {request.url.path}: {exc.errors()}")
    return error_response(
        message="Invalid request parameters",
        errors=exc.errors(),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception at {request.url.path}: {str(exc)}", exc_info=True)
    return error_response(
        message="Internal server error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# Core System Endpoints
@app.get("/health", tags=["Health"])
def health_check():
    """
    System Health Status Check Endpoint.
    """
    return success_response(
        data={
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "environment": settings.APP_ENV,
        },
        message="DiaSense AI Backend is running smoothly.",
    )


@app.get("/", tags=["Root"])
def root_endpoint():
    """
    API Welcome Endpoint.
    """
    return success_response(
        data={
            "service": settings.APP_NAME,
            "version": "1.0.0",
            "documentation": "/docs",
        },
        message="Welcome to DiaSense AI Backend API",
    )
