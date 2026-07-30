import asyncio
import json
import uuid
import sys
import pathlib
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sse_starlette.sse import EventSourceResponse

from app.schemas.ticket import (
    TicketGenerationRequest, 
    TicketResponsePayload, 
    DepartmentListResponse,
    DepartmentInfo,
    DepartmentName,
    VisionInputPayload,
    SeverityLevel,
    vision_response_to_input_payload
)
from app.services.department_mapper import DepartmentMapper
from app.services.ticket_service import TicketService
from app.services.document_customizer import DocumentCustomizer
from pydantic import BaseModel

# Schema for chat-based document customization
class TicketCustomizationRequest(BaseModel):
    ticket: Dict[str, Any]
    user_prompt: str

# Dynamically link vision_intelligence service
current_file = pathlib.Path(__file__).resolve()
backend_dir = None
for p in current_file.parents:
    if (p / "vision_intelligence").exists():
        backend_dir = p
        break

if backend_dir:
    vision_dir = backend_dir / "vision_intelligence"
    if str(vision_dir) not in sys.path:
        sys.path.insert(0, str(vision_dir))

try:
    from services.vision_service import analyze_image_bytes
except ImportError as e:
    logger.error(f"Failed to import analyze_image_bytes: {e}")
    analyze_image_bytes = None

logger = logging.getLogger("civicflow.routes.ticket")
router = APIRouter()

# Dependency Instantiations (Singletons)
department_mapper_instance = DepartmentMapper()
ticket_service_instance = TicketService(department_mapper=department_mapper_instance)
customizer_instance = DocumentCustomizer()

# In-memory and disk backup storage for upload session image assets
SESSION_STORE: Dict[str, bytes] = {}
TEMP_UPLOAD_DIR = pathlib.Path(__file__).parent.parent.parent.parent.parent / "temp_uploads"
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/upload-session",
    status_code=status.HTTP_200_OK,
    summary="Initialize Image Analysis Session"
)
async def upload_session_endpoint(image: UploadFile = File(...)):
    """
    Consumes uploaded infrastructure imagery asset and creates a session ID
    for real-time SSE visual intelligence analysis.
    """
    try:
        image_bytes = await image.read()
        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )
        
        session_id = str(uuid.uuid4())
        SESSION_STORE[session_id] = image_bytes
        
        # Also backup to disk
        try:
            (TEMP_UPLOAD_DIR / f"{session_id}.jpg").write_bytes(image_bytes)
        except Exception:
            pass

        logger.info(f"Successfully initialized session {session_id} with {len(image_bytes)} bytes.")
        return {"sessionId": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing upload session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload session initialization failed: {str(e)}"
        )


@router.post(
    "/generate-ticket", 
    response_model=TicketResponsePayload, 
    status_code=status.HTTP_200_OK,
    summary="Generate Formal Municipal Complaint Ticket"
)
async def generate_ticket_endpoint(request: TicketGenerationRequest):
    """
    Consumes Vision JSON input and generates a complete, formal government complaint ticket.
    """
    try:
        ticket = await ticket_service_instance.generate_ticket(request)
        return ticket
    except Exception as e:
        logger.error(f"Error generating ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ticket generation failed: {str(e)}"
        )


@router.post(
    "/customize-ticket",
    status_code=status.HTTP_200_OK,
    summary="Customize Municipal Complaint Ticket via Groq AI Chat"
)
async def customize_ticket_endpoint(request: TicketCustomizationRequest):
    """
    Consumes current ticket JSON and user modification instruction prompt.
    Uses Groq API to update document telemetry and return change summary.
    """
    try:
        res = await customizer_instance.customize_ticket(
            current_ticket=request.ticket,
            user_instruction=request.user_prompt
        )
        return res
    except Exception as e:
        logger.error(f"Ticket customization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ticket customization failed: {str(e)}"
        )


@router.get(
    "/ticket-departments", 
    response_model=DepartmentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Supported Civic Departments for Ticket Intelligence"
)
async def list_ticket_departments_endpoint():
    """Returns directory of supported civic departments and typical response SLAs."""
    dept_list = [
        DepartmentInfo(id="PWD", name=DepartmentName.PWD, description="Roads, bridges, and public infrastructure", typical_sla_hours=48),
        DepartmentInfo(id="SANITATION", name=DepartmentName.SANITATION, description="Solid waste, illegal dumping, and public hygiene", typical_sla_hours=24),
        DepartmentInfo(id="ELECTRICITY", name=DepartmentName.ELECTRICITY, description="Power lines, transformers, and street lighting", typical_sla_hours=12),
        DepartmentInfo(id="WATER_SEWAGE", name=DepartmentName.WATER_SEWAGE, description="Water mains, drainage systems, and manholes", typical_sla_hours=12),
        DepartmentInfo(id="TRAFFIC", name=DepartmentName.TRAFFIC_POLICE, description="Traffic signals, road obstructions, and hazards", typical_sla_hours=6),
    ]
    return DepartmentListResponse(departments=dept_list)


@router.get(
    "/analyze-live", 
    summary="Live AI Thought Stream & Pipeline Execution (SSE)"
)
async def analyze_live_sse(
    sessionId: Optional[str] = Query(None),
    issue_type: Optional[str] = Query(None),
    severity: Optional[SeverityLevel] = Query(None),
    description: Optional[str] = Query(None)
):
    """
    Server-Sent Events endpoint streaming real-time pipeline execution, AI thought frames,
    intermediate vision results, and the final complaint ticket.
    """
    
    async def sse_generator() -> AsyncGenerator[dict, None]:
        try:
            # Stage 1: Vision Analysis
            yield {
                "event": "stage_start",
                "data": json.dumps({
                    "stage": "ANALYZING_VISION",
                    "stageLabel": "Vision Analysis",
                    "estimatedDurationMs": 3000
                })
            }
            yield {
                "event": "stage_update",
                "data": json.dumps({
                    "stage": "STAGING_VISION_ANALYSIS",
                    "progress_percentage": 20,
                    "description": "Executing Gemma Multimodal Vision Engine"
                })
            }
            await asyncio.sleep(0.3)

            # Determine vision data source
            vision_obj = None
            img_bytes = None
            if sessionId:
                if sessionId in SESSION_STORE:
                    img_bytes = SESSION_STORE[sessionId]
                else:
                    disk_file = TEMP_UPLOAD_DIR / f"{sessionId}.jpg"
                    if disk_file.exists():
                        try:
                            img_bytes = disk_file.read_bytes()
                        except Exception:
                            img_bytes = None

            if img_bytes and analyze_image_bytes:
                yield {
                    "event": "token",
                    "data": json.dumps({"token": "Ingested image asset. Pre-processing visual grid telemetry...\n"})
                }
                yield {
                    "event": "thought",
                    "data": json.dumps({
                        "agent": "VisionIntelligenceEngine",
                        "thought": "Ingested image asset. Executing multimodal LLM visual inspection..."
                    })
                }
                await asyncio.sleep(0.4)
                
                try:
                    vision_obj = await analyze_image_bytes(img_bytes)
                except Exception as ve:
                    logger.warning(f"Live vision call failed: {ve}")

            if not vision_obj:
                desc_text = description or "No valid civic image provided."
                vision_data_dict = {
                    "is_civic_issue": False,
                    "type": "Unrecognized Image",
                    "severity": "Low",
                    "confidenceScore": 0,
                    "description": desc_text,
                    "affectedArea": "None",
                    "possibleRisks": []
                }
            else:
                vision_dict = vision_obj.model_dump() if hasattr(vision_obj, "model_dump") else vision_obj.dict()
                is_civic = vision_dict.get("is_civic_issue", True)
                if isinstance(is_civic, str):
                    is_civic = is_civic.strip().lower() in ("true", "1", "yes")

                issue_type_str = str(vision_dict.get("issue_type", "")).lower()
                if "non-civic" in issue_type_str or "unrecognized" in issue_type_str:
                    is_civic = False

                vision_data_dict = {
                    "is_civic_issue": bool(is_civic),
                    "type": vision_dict.get("issue_type", "Civic Infrastructure Hazard"),
                    "severity": vision_dict.get("severity", severity or SeverityLevel.LOW),
                    "confidenceScore": vision_dict.get("confidence", 85),
                    "description": vision_dict.get("description", "Image analyzed."),
                    "affectedArea": vision_dict.get("affected_infrastructure", "Public Infrastructure Zone"),
                    "possibleRisks": vision_dict.get("visible_risks", [])
                }

            # Yield Vision Complete
            yield {
                "event": "vision_complete",
                "data": json.dumps({"visionResult": vision_data_dict})
            }
            yield {
                "event": "vision_result",
                "data": json.dumps({"vision_data": vision_data_dict})
            }
            await asyncio.sleep(0.4)

            # Halt pipeline if this is NOT a civic issue
            if not vision_data_dict.get("is_civic_issue", True):
                desc = vision_data_dict.get("description", "Non-civic subject detected.")
                yield {
                    "event": "token",
                    "data": json.dumps({"token": f"\nSorry, I couldn't find exactly what your problem is. All I see is: {desc}\nNo government complaint ticket will be generated.\n"})
                }
                yield {
                    "event": "thought",
                    "data": json.dumps({
                        "agent": "VisionIntelligenceEngine",
                        "thought": f"Identified non-civic input: {desc}. Halting ticket generation."
                    })
                }
                yield {
                    "event": "non_civic",
                    "data": json.dumps({
                        "message": desc,
                        "issue_type": vision_data_dict.get("type", "Non-Civic Image"),
                        "description": desc
                    })
                }
                return  # Stop execution, do not proceed to department mapping or ticket generation!

            # Stage 2: Department Mapping
            yield {
                "event": "stage_start",
                "data": json.dumps({
                    "stage": "MAPPING_DEPARTMENT",
                    "stageLabel": "Department Mapping",
                    "estimatedDurationMs": 2000
                })
            }
            yield {
                "event": "stage_update",
                "data": json.dumps({
                    "stage": "STAGING_DEPARTMENT_MAPPING",
                    "progress_percentage": 60,
                    "description": "Resolving civic department and priority score"
                })
            }
            yield {
                "event": "token",
                "data": json.dumps({"token": f"Resolving municipal authority for issue '{vision_data_dict['type']}'...\n"})
            }
            yield {
                "event": "thought",
                "data": json.dumps({
                    "agent": "DepartmentMapper",
                    "thought": f"Matched pattern for '{vision_data_dict['type']}'. Calculating risk factors and priority."
                })
            }
            await asyncio.sleep(0.5)

            # Stage 3: Synthesizing Ticket
            yield {
                "event": "stage_start",
                "data": json.dumps({
                    "stage": "SYNTHESIZING_TICKET",
                    "stageLabel": "Synthesizing Ticket",
                    "estimatedDurationMs": 2000
                })
            }
            yield {
                "event": "stage_update",
                "data": json.dumps({
                    "stage": "STAGING_COMPLAINT_GENERATION",
                    "progress_percentage": 85,
                    "description": "Drafting formal municipal complaint using Ticket Intelligence Agent"
                })
            }
            yield {
                "event": "token",
                "data": json.dumps({"token": "Drafting formal bureaucratic memo & statutory legal references...\n"})
            }
            await asyncio.sleep(0.6)

            vision_input_payload = vision_response_to_input_payload(vision_data_dict)
            req = TicketGenerationRequest(vision_data=vision_input_payload)
            ticket_obj = await ticket_service_instance.generate_ticket(req)

            ticket_dump = ticket_obj.model_dump() if hasattr(ticket_obj, "model_dump") else ticket_obj.dict()

            # Adapt ticket payload to match frontend GeneratedTicket interface
            frontend_ticket_result = {
                "id": ticket_dump.get("ticket_id"),
                "ticketId": ticket_dump.get("ticket_id"),
                "title": ticket_dump.get("complaint_title"),
                "description": ticket_dump.get("executive_summary"),
                "category": vision_data_dict["type"],
                "department": ticket_dump.get("department"),
                "severity": ticket_dump.get("priority"),
                "location": vision_data_dict["affectedArea"],
                "evidence": ticket_dump.get("evidence_summary", []),
                "dateGenerated": ticket_dump.get("created_at"),
                "formal_complaint_body": ticket_dump.get("formal_complaint_body"),
                "executive_summary": ticket_dump.get("executive_summary"),
                "actionable_recommendations": ticket_dump.get("actionable_recommendations", []),
                "statutory_references": ticket_dump.get("statutory_references", [])
            }

            yield {
                "event": "ticket_complete",
                "data": json.dumps({"ticketResult": frontend_ticket_result}, default=str)
            }
            yield {
                "event": "ticket_result",
                "data": json.dumps({"ticket_data": ticket_dump}, default=str)
            }
            
        except Exception as e:
            logger.error(f"SSE Pipeline Error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "error_code": "SSE_PIPELINE_FAILURE",
                    "message": str(e),
                    "recoverable": False
                })
            }

    return EventSourceResponse(sse_generator())

