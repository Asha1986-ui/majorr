from app.config.database import Base
from app.models.user import User
from app.models.assessment import Assessment
from app.models.prediction import Prediction
from app.models.diet_plan import DietPlan
from app.models.contact import ContactMessage

__all__ = ["Base", "User", "Assessment", "Prediction", "DietPlan", "ContactMessage"]
