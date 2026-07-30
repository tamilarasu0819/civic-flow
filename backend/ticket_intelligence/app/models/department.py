from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    head_email = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    sla_hours_p0 = Column(Integer, default=4)
    sla_hours_p1 = Column(Integer, default=24)
    sla_hours_p2 = Column(Integer, default=72)
    sla_hours_p3 = Column(Integer, default=168)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="department")
    complaints = relationship("Complaint", back_populates="department")
