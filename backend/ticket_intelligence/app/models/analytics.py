from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.db.base import Base

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True, nullable=False)
    metric_value = Column(Float, nullable=False)
    category = Column(String, index=True, nullable=True)
    date_recorded = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    extra_metadata = Column(JSON, nullable=True)
