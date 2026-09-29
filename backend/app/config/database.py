from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config.settings import settings
from app.utils.logger import logger

# Create SQLAlchemy Engine
# Handles both MySQL and SQLite database connections seamlessly
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI Dependency that provides a database session per request,
    ensuring proper closing upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Automatically creates all database tables defined in SQLAlchemy ORM models.
    """
    try:
        from app.models import Base  # Import after models are defined
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}", exc_info=True)
        raise e
