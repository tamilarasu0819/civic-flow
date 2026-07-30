from typing import Dict, Any, List
from pydantic import BaseModel

class PriorityBreakdown(BaseModel):
    P0_Critical: int = 0
    P1_High: int = 0
    P2_Medium: int = 0
    P3_Low: int = 0

class StatusBreakdown(BaseModel):
    SUBMITTED: int = 0
    TRIAGED: int = 0
    ASSIGNED: int = 0
    IN_PROGRESS: int = 0
    RESOLVED: int = 0
    REJECTED: int = 0
    CLOSED: int = 0

class DepartmentMetric(BaseModel):
    department_name: str
    code: str
    total_complaints: int
    pending_complaints: int
    resolved_complaints: int
    avg_resolution_hours: float
    sla_compliance_rate: float

class AnalyticsOverview(BaseModel):
    total_complaints: int
    open_complaints: int
    resolved_complaints: int
    resolution_rate_percent: float
    avg_resolution_hours: float
    total_duplicates_detected: int
    priority_breakdown: PriorityBreakdown
    status_breakdown: StatusBreakdown
    category_distribution: Dict[str, int]
    department_metrics: List[DepartmentMetric]
