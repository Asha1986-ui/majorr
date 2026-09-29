"""
Database Migration: Pima v1 → India Diabetes Dataset v2
Run once from: backend/ directory

Usage:
    python app/ml/migrate_db_v2.py

This script safely adds new columns to the existing `assessments` table
using IF NOT EXISTS so it is safe to re-run.
"""
import sys
import os

# Allow running from backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config.database import engine
from sqlalchemy import text

MIGRATIONS = [
    # New v2 columns
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS patient_group VARCHAR(50)",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS gender VARCHAR(20)",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS blood_pressure FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS physical_activity_hours FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS daily_sugar_intake FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS fast_food_frequency FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS sleep_hours FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS hba1c FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS fasting_glucose FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS family_history FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS monthly_income FLOAT",
    "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS month FLOAT",
    # Keep legacy columns nullable (for rollback compatibility)
    "ALTER TABLE assessments ALTER COLUMN glucose DROP NOT NULL",
    "ALTER TABLE assessments ALTER COLUMN blood_pressure DROP NOT NULL",
    "ALTER TABLE assessments ALTER COLUMN bmi DROP NOT NULL",
]


def run_migration():
    print("=" * 55)
    print("DiaSense AI — DB Migration v2 (India Diabetes Schema)")
    print("=" * 55)
    with engine.begin() as conn:
        for sql in MIGRATIONS:
            try:
                conn.execute(text(sql))
                print(f"  OK: {sql[:70]}...")
            except Exception as e:
                print(f"  SKIP (may already exist): {e}")
    print("\nMigration complete. Old data preserved. New columns are nullable.")
    print("=" * 55)


if __name__ == "__main__":
    run_migration()
