from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.complaint import Complaint, PriorityLevel, ComplaintStatus
from app.models.status_history import StatusHistory
from app.models.notification import Notification
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintResponse, AIAnalysisPayload
from app.services.agent_workflow import AgentWorkflowEngine

router = APIRouter()

@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    complaint_in: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submits a new civic complaint and triggers the Intake & Agent Triage pipeline.
    """
    complaint = await AgentWorkflowEngine.process_new_complaint(db, complaint_in, current_user.id)
    
    # Reload with relationships
    stmt = select(Complaint).where(Complaint.id == complaint.id).options(
        selectinload(Complaint.department),
        selectinload(Complaint.work_orders),
        selectinload(Complaint.status_history)
    )
    res = await db.execute(stmt)
    return res.scalar_one()

@router.get("", response_model=List[ComplaintResponse])
async def list_complaints(
    priority: Optional[PriorityLevel] = Query(None),
    status_filter: Optional[ComplaintStatus] = Query(None),
    department_id: Optional[int] = Query(None),
    is_duplicate: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complaints list with filtering & pagination.
    Citizens see their complaints; Officers see department complaints; Admins see all.
    """
    query = select(Complaint).options(
        selectinload(Complaint.department),
        selectinload(Complaint.work_orders),
        selectinload(Complaint.status_history)
    )

    if current_user.role == UserRole.CITIZEN:
        query = query.where(Complaint.citizen_id == current_user.id)
    elif current_user.role == UserRole.OFFICER and current_user.department_id:
        query = query.where(Complaint.department_id == current_user.department_id)

    if priority:
        query = query.where(Complaint.priority_level == priority)
    if status_filter:
        query = query.where(Complaint.status == status_filter)
    if department_id:
        query = query.where(Complaint.department_id == department_id)
    if is_duplicate is not None:
        query = query.where(Complaint.is_duplicate == is_duplicate)
    if search:
        query = query.where(
            (Complaint.title.ilike(f"%{search}%")) | 
            (Complaint.description.ilike(f"%{search}%")) |
            (Complaint.ticket_number.ilike(f"%{search}%"))
        )

    query = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()

@router.get("/{id}", response_model=ComplaintResponse)
async def get_complaint(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed complaint profile including priority factors, status history, and work orders.
    """
    stmt = select(Complaint).where(Complaint.id == id).options(
        selectinload(Complaint.department),
        selectinload(Complaint.work_orders),
        selectinload(Complaint.status_history)
    )
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()
    
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
        
    return complaint

@router.put("/{id}", response_model=ComplaintResponse)
async def update_complaint(
    id: int,
    complaint_in: ComplaintUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update complaint status, reassign department, or override priority.
    Appends to status history and sends citizen notifications.
    """
    stmt = select(Complaint).where(Complaint.id == id).options(
        selectinload(Complaint.department),
        selectinload(Complaint.work_orders),
        selectinload(Complaint.status_history)
    )
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()

    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    old_status = complaint.status.value

    if complaint_in.title is not None:
        complaint.title = complaint_in.title
    if complaint_in.description is not None:
        complaint.description = complaint_in.description
    if complaint_in.category is not None:
        complaint.category = complaint_in.category
    if complaint_in.priority_level is not None:
        complaint.priority_level = complaint_in.priority_level
    if complaint_in.department_id is not None:
        complaint.department_id = complaint_in.department_id
    if complaint_in.location_address is not None:
        complaint.location_address = complaint_in.location_address

    if complaint_in.status is not None and complaint_in.status != complaint.status:
        complaint.status = complaint_in.status
        
        # Log audit step in status history
        history_entry = StatusHistory(
            complaint_id=complaint.id,
            previous_status=old_status,
            new_status=complaint.status.value,
            changed_by_user_id=current_user.id,
            agent_name=current_user.full_name,
            comment=complaint_in.comment or f"Status updated to {complaint.status.value}"
        )
        db.add(history_entry)

        # Notify citizen
        notif = Notification(
            user_id=complaint.citizen_id,
            title=f"Complaint Status Update: #{complaint.ticket_number}",
            message=f"Your complaint '{complaint.title}' status changed to {complaint.status.value}.",
            type="STATUS_CHANGE"
        )
        db.add(notif)

    await db.commit()
    await db.refresh(complaint)
    return complaint

@router.post("/{id}/ai-analyze", response_model=ComplaintResponse)
async def attach_ai_analysis(
    id: int,
    payload: AIAnalysisPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Hook for AI Agents / Computer Vision sub-agents to attach OCR text and Gemma multimodal outputs.
    """
    stmt = select(Complaint).where(Complaint.id == id).options(
        selectinload(Complaint.department),
        selectinload(Complaint.work_orders),
        selectinload(Complaint.status_history)
    )
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()

    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    if payload.ocr_extracted_text:
        complaint.ocr_extracted_text = payload.ocr_extracted_text

    analysis_dict = complaint.ai_analysis or {}
    analysis_dict.update({
        "detected_objects": payload.detected_objects or [],
        "gemma_summary": payload.gemma_summary or "",
        "confidence_score": payload.confidence_score or 0.95
    })
    complaint.ai_analysis = analysis_dict

    if payload.suggested_priority:
        complaint.priority_level = payload.suggested_priority

    history_entry = StatusHistory(
        complaint_id=complaint.id,
        previous_status=complaint.status.value,
        new_status=complaint.status.value,
        agent_name="GemmaVisionSubAgent",
        comment=f"Attached AI Multimodal Vision Analysis. Detected: {', '.join(payload.detected_objects or [])}"
    )
    db.add(history_entry)

    await db.commit()
    await db.refresh(complaint)
    return complaint
