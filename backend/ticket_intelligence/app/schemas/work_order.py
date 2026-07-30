from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.complaint import PriorityLevel
from app.models.work_order import WorkOrderStatus

class WorkOrderBase(BaseModel):
    complaint_id: int
    assigned_officer_id: Optional[int] = None
    priority: Optional[PriorityLevel] = PriorityLevel.P2
    estimated_completion_days: Optional[int] = 3
    notes: Optional[str] = None

class WorkOrderCreate(WorkOrderBase):
    pass

class WorkOrderUpdate(BaseModel):
    assigned_officer_id: Optional[int] = None
    priority: Optional[PriorityLevel] = None
    estimated_completion_days: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[WorkOrderStatus] = None

class WorkOrderResponse(WorkOrderBase):
    id: int
    work_order_code: str
    status: WorkOrderStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
