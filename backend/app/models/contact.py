from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.config.database import Base


class ContactMessage(Base):
    """
    SQLAlchemy Contact Message Model.
    Table: contact_messages
    """
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
