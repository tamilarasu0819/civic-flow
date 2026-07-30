from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.models.complaint import PriorityLevel, ComplaintStatus
from app.schemas.department import DepartmentResponse
from app.schemas.status_history import StatusHistoryResponse
from app.schemas.work_order import WorkOrderResponse

class PriorityFactors(BaseModel):
    human_safety: float = 0.0          # 0 to 25
    affected_citizens: float = 0.0     # 0 to 15
    vulnerable_groups: float = 0.0     # 0 to 15
    traffic_disruption: float = 0.0    # 0 to 15
    environmental_impact: float = 0.0  # 0 to 10
    infrastructure_damage: float = 0.0 # 0 to 10
    complaint_age: float = 0.0         # 0 to 5
    duplicate_count: float = 0.0       # 0 to 5

class ComplaintCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = "General"
    location_address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    media_urls: Optional[List[str]] = []
    
    human_safety_hazard: Optional[bool] = False
    vulnerable_area: Optional[bool] = False
    estimated_affected_count: Optional[int] = 1

class ComplaintUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority_level: Optional[PriorityLevel] = None
    status: Optional[ComplaintStatus] = None
    department_id: Optional[int] = None
    location_address: Optional[str] = None
    comment: Optional[str] = None

class AIAnalysisPayload(BaseModel):
    ocr_extracted_text: Optional[str] = None
    detected_objects: Optional[List[str]] = None
    gemma_summary: Optional[str] = None
    suggested_category: Optional[str] = None
    suggested_priority: Optional[PriorityLevel] = None
    confidence_score: Optional[float] = None

class ComplaintResponse(BaseModel):
    id: int
    ticket_number: str
    title: str
    description: str
    category: str
    priority_level: PriorityLevel
    priority_score: float
    priority_factors: Optional[Dict[str, Any]] = None
    ocr_extracted_text: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    status: ComplaintStatus
    location_address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    media_urls: List[str] = []
    citizen_id: int
    department_id: Optional[int] = None
    is_duplicate: bool = False
    parent_complaint_id: Optional[int] = None
    duplicate_count: int = 0
    created_at: datetime
    updated_at: datetime

    department: Optional[DepartmentResponse] = None
    work_orders: Optional[List[WorkOrderResponse]] = []
    status_history: Optional[List[StatusHistoryResponse]] = []

    class Config:
        from_attributes = True
