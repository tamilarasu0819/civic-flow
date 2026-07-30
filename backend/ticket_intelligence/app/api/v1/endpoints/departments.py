from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api.deps import get_db, get_current_user, get_current_active_officer
from app.models.department import Department
from app.models.complaint import Complaint, ComplaintStatus
from app.schemas.department import DepartmentCreate, DepartmentResponse

router = APIRouter()

@router.get("", response_model=List[DepartmentResponse])
async def list_departments(db: AsyncSession = Depends(get_db)):
    stmt = select(Department)
    res = await db.execute(stmt)
    departments = res.scalars().all()

    response_list = []
    for dept in departments:
        # Count active open complaints
        stmt_count = select(func.count(Complaint.id)).where(
            Complaint.department_id == dept.id,
            Complaint.status.in_([ComplaintStatus.SUBMITTED, ComplaintStatus.TRIAGED, ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS])
        )
        res_count = await db.execute(stmt_count)
        active_count = res_count.scalar() or 0

        dept_resp = DepartmentResponse(
            id=dept.id,
            name=dept.name,
            code=dept.code,
            description=dept.description,
            head_email=dept.head_email,
            contact_number=dept.contact_number,
            sla_hours_p0=dept.sla_hours_p0,
            sla_hours_p1=dept.sla_hours_p1,
            sla_hours_p2=dept.sla_hours_p2,
            sla_hours_p3=dept.sla_hours_p3,
            created_at=dept.created_at,
            active_complaints_count=active_count
        )
        response_list.append(dept_resp)

    return response_list

@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_in: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_officer = Depends(get_current_active_officer)
):
    dept = Department(
        name=dept_in.name,
        code=dept_in.code.upper(),
        description=dept_in.description,
        head_email=dept_in.head_email,
        contact_number=dept_in.contact_number,
        sla_hours_p0=dept_in.sla_hours_p0 or 4,
        sla_hours_p1=dept_in.sla_hours_p1 or 24,
        sla_hours_p2=dept_in.sla_hours_p2 or 72,
        sla_hours_p3=dept_in.sla_hours_p3 or 168
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept
