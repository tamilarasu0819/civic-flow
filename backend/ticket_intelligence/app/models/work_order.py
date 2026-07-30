import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.complaint import PriorityLevel

class WorkOrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    work_order_code = Column(String, unique=True, index=True, nullable=False)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    assigned_officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.P2)
    estimated_completion_days = Column(Integer, default=3)
    notes = Column(Text, nullable=True)
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.PENDING, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    complaint = relationship("Complaint", back_populates="work_orders")
    assigned_officer = relationship("User", back_populates="assigned_work_orders")
