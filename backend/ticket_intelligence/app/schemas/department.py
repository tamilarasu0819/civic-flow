from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class DepartmentBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    head_email: Optional[str] = None
    contact_number: Optional[str] = None
    sla_hours_p0: Optional[int] = 4
    sla_hours_p1: Optional[int] = 24
    sla_hours_p2: Optional[int] = 72
    sla_hours_p3: Optional[int] = 168

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    active_complaints_count: Optional[int] = 0

    class Config:
        from_attributes = True
