import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class PriorityLevel(str, enum.Enum):
    P0 = "P0"  # Critical
    P1 = "P1"  # High
    P2 = "P2"  # Medium
    P3 = "P3"  # Low

class ComplaintStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    TRIAGED = "TRIAGED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    
    # Priority & Reasoning Engine Fields
    priority_level = Column(Enum(PriorityLevel), default=PriorityLevel.P2, index=True)
    priority_score = Column(Float, default=50.0)
    priority_factors = Column(JSON, nullable=True)
    
    # OCR / Vision / AI Integration Outputs
    ocr_extracted_text = Column(Text, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    
    # Workflow & Status
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.SUBMITTED, index=True)
    
    # Location
    location_address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    media_urls = Column(JSON, default=list)
    
    # Relationships & Foreign Keys
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    
    # Duplicate Detection
    is_duplicate = Column(Boolean, default=False, index=True)
    parent_complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=True)
    duplicate_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    citizen = relationship("User", back_populates="complaints", foreign_keys=[citizen_id])
    department = relationship("Department", back_populates="complaints")
    work_orders = relationship("WorkOrder", back_populates="complaint")
    status_history = relationship("StatusHistory", back_populates="complaint", cascade="all, delete-orphan")
    parent_complaint = relationship("Complaint", remote_side=[id], backref="duplicates")
