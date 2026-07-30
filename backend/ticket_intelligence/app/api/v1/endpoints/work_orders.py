import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_db, get_current_user, get_current_active_officer
from app.models.user import User
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.complaint import Complaint, ComplaintStatus
from app.models.status_history import StatusHistory
from app.schemas.work_order import WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse

router = APIRouter()

@router.post("", response_model=WorkOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    wo_in: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_officer: User = Depends(get_current_active_officer)
):
    stmt = select(Complaint).where(Complaint.id == wo_in.complaint_id)
    res = await db.execute(stmt)
    complaint = res.scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    work_order_code = f"WO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    work_order = WorkOrder(
        work_order_code=work_order_code,
        complaint_id=wo_in.complaint_id,
        assigned_officer_id=wo_in.assigned_officer_id or current_officer.id,
        priority=wo_in.priority or complaint.priority_level,
        estimated_completion_days=wo_in.estimated_completion_days or 3,
        notes=wo_in.notes,
        status=WorkOrderStatus.PENDING
    )
    db.add(work_order)
    
    complaint.status = ComplaintStatus.IN_PROGRESS
    db.add(StatusHistory(
        complaint_id=complaint.id,
        previous_status=ComplaintStatus.ASSIGNED.value,
        new_status=ComplaintStatus.IN_PROGRESS.value,
        changed_by_user_id=current_officer.id,
        agent_name=current_officer.full_name,
        comment=f"Work Order {work_order_code} issued."
    ))

    await db.commit()
    await db.refresh(work_order)
    return work_order

@router.get("", response_model=List[WorkOrderResponse])
async def list_work_orders(
    status_filter: Optional[WorkOrderStatus] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(WorkOrder)
    if status_filter:
        query = query.where(WorkOrder.status == status_filter)
    query = query.order_by(WorkOrder.created_at.desc()).offset(skip).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()

@router.put("/{id}", response_model=WorkOrderResponse)
async def update_work_order(
    id: int,
    wo_in: WorkOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_officer: User = Depends(get_current_active_officer)
):
    stmt = select(WorkOrder).where(WorkOrder.id == id)
    res = await db.execute(stmt)
    wo = res.scalar_one_or_none()
    if not wo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work Order not found")

    if wo_in.assigned_officer_id is not None:
        wo.assigned_officer_id = wo_in.assigned_officer_id
    if wo_in.priority is not None:
        wo.priority = wo_in.priority
    if wo_in.estimated_completion_days is not None:
        wo.estimated_completion_days = wo_in.estimated_completion_days
    if wo_in.notes is not None:
        wo.notes = wo_in.notes
    if wo_in.status is not None:
        wo.status = wo_in.status
        if wo_in.status == WorkOrderStatus.COMPLETED:
            wo.completed_at = datetime.now(timezone.utc)
            # Update complaint status to RESOLVED
            stmt_c = select(Complaint).where(Complaint.id == wo.complaint_id)
            res_c = await db.execute(stmt_c)
            complaint = res_c.scalar_one_or_none()
            if complaint:
                complaint.status = ComplaintStatus.RESOLVED
                db.add(StatusHistory(
                    complaint_id=complaint.id,
                    previous_status=ComplaintStatus.IN_PROGRESS.value,
                    new_status=ComplaintStatus.RESOLVED.value,
                    changed_by_user_id=current_officer.id,
                    agent_name=current_officer.full_name,
                    comment=f"Work order {wo.work_order_code} completed."
                ))

    await db.commit()
    await db.refresh(wo)
    return wo
