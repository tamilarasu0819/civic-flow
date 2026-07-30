from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class StatusHistoryResponse(BaseModel):
    id: int
    complaint_id: int
    previous_status: Optional[str] = None
    new_status: str
    changed_by_user_id: Optional[int] = None
    agent_name: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
