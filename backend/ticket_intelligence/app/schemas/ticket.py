"""
backend/app/schemas/ticket.py
Pydantic Schemas for Ticket Intelligence Engine and API Gateway.
"""

from enum import Enum
from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class SeverityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class PriorityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class DepartmentName(str, Enum):
    PWD = "Public Works Department (PWD)"
    SANITATION = "Department of Sanitation & Solid Waste Management"
    ELECTRICITY = "Electricity Board / Power Discom"
    WATER_SEWAGE = "Water Supply & Sewage Board"
    TRAFFIC_POLICE = "Traffic Police / RTO"
    GENERAL_MUNICIPAL = "General Municipal Administration"


# --- Input Payloads ---

class VisionInputPayload(BaseModel):
    """Payload produced by Stage 1 Vision Intelligence Engine."""
    type: str = Field(..., example="Drainage Overflow")
    severity: SeverityLevel = Field(..., example=SeverityLevel.HIGH)
    confidence: float = Field(..., ge=0.0, le=100.0, example=94.5)
    description: str = Field(..., example="Drain water overflowing onto public road")
    affected_area: str = Field(..., example="Main Road")
    possible_risks: List[str] = Field(
        default_factory=list, 
        example=["Traffic Hazard", "Disease Spread"]
    )
    image_url: Optional[str] = None


def vision_response_to_input_payload(data: Any) -> VisionInputPayload:
    """
    Converts a Vision Intelligence output (VisionAnalysisResponse or raw JSON dict)
    into a standardized VisionInputPayload for Ticket Intelligence.
    """
    if isinstance(data, VisionInputPayload):
        return data

    if hasattr(data, "model_dump"):
        data_dict = data.model_dump()
    elif hasattr(data, "dict"):
        data_dict = data.dict()
    elif isinstance(data, dict):
        data_dict = data
    else:
        raise ValueError(f"Unsupported vision data type: {type(data)}")

    # Check if already in VisionInputPayload format
    if "type" in data_dict and "affected_area" in data_dict:
        severity_val = data_dict.get("severity", SeverityLevel.HIGH)
        if isinstance(severity_val, str):
            cap_sev = severity_val.capitalize()
            severity_val = SeverityLevel(cap_sev) if cap_sev in [s.value for s in SeverityLevel] else SeverityLevel.HIGH
        return VisionInputPayload(
            type=data_dict["type"],
            severity=severity_val,
            confidence=float(data_dict.get("confidence", 90.0)),
            description=data_dict.get("description", ""),
            affected_area=data_dict.get("affected_area", "Public Carriageway"),
            possible_risks=data_dict.get("possible_risks", []),
            image_url=data_dict.get("image_url")
        )

    # Convert from VisionAnalysisResponse format (issue_type, affected_infrastructure, visible_risks, etc.)
    issue_type = data_dict.get("issue_type", data_dict.get("type", "Civic Infrastructure Hazard"))
    severity_raw = data_dict.get("severity", "High")
    if isinstance(severity_raw, str):
        cap_sev = severity_raw.capitalize()
        severity = SeverityLevel(cap_sev) if cap_sev in [s.value for s in SeverityLevel] else SeverityLevel.HIGH
    else:
        severity = SeverityLevel.HIGH

    confidence = float(data_dict.get("confidence", 90))
    description = data_dict.get("description", "")
    affected_area = data_dict.get("affected_infrastructure", data_dict.get("affected_area", "Public Infrastructure Zone"))
    possible_risks = data_dict.get("visible_risks", data_dict.get("possible_risks", []))

    return VisionInputPayload(
        type=issue_type,
        severity=severity,
        confidence=confidence,
        description=description,
        affected_area=affected_area,
        possible_risks=possible_risks,
        image_url=data_dict.get("image_url")
    )


class TicketGenerationRequest(BaseModel):
    """Request payload for manual/direct ticket generation endpoint."""
    vision_data: VisionInputPayload
    user_location_hint: Optional[str] = Field(
        None, example="Corner of 5th Main and 12th Cross Road"
    )
    override_department: Optional[DepartmentName] = None



# --- Internal Resolution Schemas ---

class DepartmentMappingResult(BaseModel):
    department: DepartmentName
    priority: PriorityLevel
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    matched_rule: str
    resolution_method: str = Field(..., example="RULE_MATRIX")  # RULE_MATRIX or LLM_FALLBACK


# --- Response Payloads ---

class TicketResponsePayload(BaseModel):
    """Final ready-to-submit municipal complaint ticket payload."""
    ticket_id: str = Field(..., example="TCK-20260730-9421")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    department: DepartmentName
    priority: PriorityLevel
    complaint_title: str
    executive_summary: str
    formal_complaint_body: str
    evidence_summary: List[str]
    actionable_recommendations: List[str]
    statutory_references: List[str]
    vision_summary: VisionInputPayload


class DepartmentInfo(BaseModel):
    id: str
    name: DepartmentName
    description: str
    typical_sla_hours: int


class DepartmentListResponse(BaseModel):
    departments: List[DepartmentInfo]


# --- SSE Stream Event Schemas ---

class SSEStageUpdateData(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stage: str
    progress_percentage: int
    description: str


class SSEThoughtData(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent: str
    thought: str


class SSEErrorData(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_code: str
    message: str
    recoverable: bool = False
