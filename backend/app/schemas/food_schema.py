from typing import List, Optional
from pydantic import BaseModel, Field


class FoodAnalysisRequest(BaseModel):
    query: str = Field(..., min_length=2, example="2 Masala Dosa with sambar")


class FoodItemNutritionalDetail(BaseModel):
    food_name: str
    calories_kcal: float
    carbohydrates_g: float
    net_carbs_g: float
    protein_g: float
    fiber_g: float
    fats_g: float
    glycemic_index: int
    glycemic_load: float
    portion_size: str
    diabetic_suitability: str  # "Diabetic Friendly", "Moderate / Control Portion", "High Risk / Limit"
    suitability_color: str    # "emerald", "amber", "red"


class FoodAnalysisResponse(BaseModel):
    dish_name: str
    identified_items: List[str]
    total_calories_kcal: float
    total_carbohydrates_g: float
    total_net_carbs_g: float
    total_protein_g: float
    total_fiber_g: float
    total_fats_g: float
    average_glycemic_index: int
    overall_suitability: str  # "Diabetic Friendly", "Moderate / Control Portion", "High Risk / Avoid"
    suitability_color: str
    suggested_portion: str
    nutritional_details: List[FoodItemNutritionalDetail]
    clinical_recommendation: str
