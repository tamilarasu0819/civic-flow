"""
backend/app/services/agent_workflow.py
Complete Agent Workflow Engine:
Intake Agent -> OCR/Vision Parser -> Classification -> Duplicate Detection -> Priority Scoring (P0-P3) -> Dept Assignment -> Work Order -> Notification
"""

import math
import logging
import uuid
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.complaint import Complaint, PriorityLevel, ComplaintStatus
from app.models.department import Department
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.status_history import StatusHistory
from app.models.notification import Notification
from app.schemas.complaint import ComplaintCreate

logger = logging.getLogger("civicflow.agent_workflow")


class AgentWorkflowEngine:
    """
    Executes the 9-stage Agentic Workflow for Civic Complaints.
    """

    @staticmethod
    def calculate_priority_score_and_level(
        title: str,
        description: str,
        category: str,
        human_safety_hazard: bool = False,
        vulnerable_area: bool = False,
        estimated_affected_count: int = 1,
        duplicate_count: int = 0
    ) -> Tuple[float, PriorityLevel, Dict[str, float]]:
        """
        Computes Priority Score (0-100) using 8 Priority Factors:
        1. Human Safety (0-25)
        2. Affected Citizens (0-15)
        3. Vulnerable Groups (0-15)
        4. Traffic Disruption (0-15)
        5. Environmental Impact (0-10)
        6. Infrastructure Damage (0-10)
        7. Complaint Age (0-5)
        8. Duplicate Count (0-5)
        """
        text = f"{title} {description} {category}".lower()
        
        # 1. Human Safety (0 - 25)
        safety_score = 0.0
        if human_safety_hazard or any(k in text for k in ["live wire", "spark", "electric shock", "gas leak", "structural collapse", "open manhole", "hazard", "fire"]):
            safety_score = 25.0
        elif any(k in text for k in ["deep pothole", "sewage overflow", "fallen tree", "broken signal"]):
            safety_score = 15.0
        else:
            safety_score = 5.0

        # 2. Affected Citizens (0 - 15)
        affected_score = min(15.0, (math.log10(max(1, estimated_affected_count)) * 5.0) + 3.0)

        # 3. Vulnerable Groups (0 - 15)
        vulnerable_score = 15.0 if (vulnerable_area or any(k in text for k in ["hospital", "school", "senior", "nursery", "kindergarten", "clinic"])) else 3.0

        # 4. Traffic Disruption (0 - 15)
        traffic_score = 0.0
        if any(k in text for k in ["main road", "highway", "junction", "arterial", "traffic signal", "carriageway", "total blockage"]):
            traffic_score = 15.0
        elif any(k in text for k in ["footpath", "street", "lane"]):
            traffic_score = 8.0
        else:
            traffic_score = 3.0

        # 5. Environmental Impact (0 - 10)
        env_score = 10.0 if any(k in text for k in ["chemical", "toxic", "raw sewage", "sludge", "garbage dump", "plastic waste"]) else 2.0

        # 6. Infrastructure Damage (0 - 10)
        infra_score = 10.0 if any(k in text for k in ["bridge", "water main burst", "pipe break", "road collapse", "snapped pole", "transformer"]) else 4.0

        # 7. Complaint Age (0 - 5) - base 0 for new complaints
        age_score = 0.0

        # 8. Duplicate Count (0 - 5)
        dup_score = min(5.0, duplicate_count * 1.5)

        total_score = round(min(100.0, safety_score + affected_score + vulnerable_score + traffic_score + env_score + infra_score + age_score + dup_score), 1)

        if total_score >= 80.0:
            level = PriorityLevel.P0
        elif total_score >= 60.0:
            level = PriorityLevel.P1
        elif total_score >= 35.0:
            level = PriorityLevel.P2
        else:
            level = PriorityLevel.P3

        factors = {
            "human_safety": safety_score,
            "affected_citizens": round(affected_score, 1),
            "vulnerable_groups": vulnerable_score,
            "traffic_disruption": traffic_score,
            "environmental_impact": env_score,
            "infrastructure_damage": infra_score,
            "complaint_age": age_score,
            "duplicate_count": dup_score,
        }

        return total_score, level, factors

    @staticmethod
    async def match_department(db: AsyncSession, category: str, title: str, description: str) -> Optional[Department]:
        """
        Department Classification Agent: Matches category or text to responsible department code.
        Codes: ROADS, DRAINAGE, WASTE, ELECTRICITY, PUBLIC_HEALTH, WATER, PARKS
        """
        text = f"{category} {title} {description}".lower()
        dept_code = "ROADS"

        if any(k in text for k in ["electric", "wire", "pole", "light", "transformer", "spark", "power"]):
            dept_code = "ELECTRICITY"
        elif any(k in text for k in ["drain", "sewer", "flood", "waterlog", "manhole"]):
            dept_code = "DRAINAGE"
        elif any(k in text for k in ["garbage", "waste", "trash", "dump", "sanitation", "clean"]):
            dept_code = "WASTE"
        elif any(k in text for k in ["water", "pipe", "leak", "supply", "tap"]):
            dept_code = "WATER"
        elif any(k in text for k in ["health", "epidemic", "mosquito", "contaminate"]):
            dept_code = "PUBLIC_HEALTH"
        elif any(k in text for k in ["park", "tree", "garden", "environment"]):
            dept_code = "PARKS"
        elif any(k in text for k in ["pothole", "road", "pavement", "footpath", "bridge", "asphalt"]):
            dept_code = "ROADS"

        stmt = select(Department).where(Department.code == dept_code)
        result = await db.execute(stmt)
        dept = result.scalar_one_or_none()
        if not dept:
            # Fallback to first available department
            stmt_all = select(Department)
            res_all = await db.execute(stmt_all)
            dept = res_all.scalars().first()
        return dept

    @staticmethod
    async def check_duplicate(
        db: AsyncSession,
        category: str,
        location_address: str,
        lat: Optional[float],
        lon: Optional[float]
    ) -> Optional[Complaint]:
        """
        Duplicate Detection Agent: Finds active complaints within same category & vicinity.
        """
        stmt = select(Complaint).where(
            Complaint.category == category,
            Complaint.status.in_([ComplaintStatus.SUBMITTED, ComplaintStatus.TRIAGED, ComplaintStatus.ASSIGNED, ComplaintStatus.IN_PROGRESS]),
            Complaint.is_duplicate == False
        ).order_by(Complaint.created_at.desc())
        
        res = await db.execute(stmt)
        existing_list = res.scalars().all()

        for existing in existing_list:
            # Check coordinate distance or address similarity
            if lat and lon and existing.latitude and existing.longitude:
                dist = math.sqrt((existing.latitude - lat)**2 + (existing.longitude - lon)**2)
                if dist < 0.005:  # approx ~500 meters
                    return existing
            elif location_address.lower().strip() == existing.location_address.lower().strip():
                return existing

        return None

    @classmethod
    async def process_new_complaint(
        cls,
        db: AsyncSession,
        complaint_in: ComplaintCreate,
        citizen_id: int
    ) -> Complaint:
        """
        Executes full Intake Agent -> Classification -> Duplicate -> Priority -> Dept -> Work Order -> Notification pipeline.
        """
        ticket_number = f"CF-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        # 1. Duplicate Check
        parent_complaint = await cls.check_duplicate(
            db, complaint_in.category, complaint_in.location_address, complaint_in.latitude, complaint_in.longitude
        )

        is_dup = False
        parent_id = None
        dup_count = 0

        if parent_complaint:
            is_dup = True
            parent_id = parent_complaint.id
            parent_complaint.duplicate_count += 1
            dup_count = parent_complaint.duplicate_count
            await db.commit()

        # 2. Priority Factor Scoring
        score, level, factors = cls.calculate_priority_score_and_level(
            title=complaint_in.title,
            description=complaint_in.description,
            category=complaint_in.category,
            human_safety_hazard=complaint_in.human_safety_hazard or False,
            vulnerable_area=complaint_in.vulnerable_area or False,
            estimated_affected_count=complaint_in.estimated_affected_count or 1,
            duplicate_count=dup_count
        )

        # 3. Department Assignment
        dept = await cls.match_department(db, complaint_in.category, complaint_in.title, complaint_in.description)

        # 4. Create Complaint DB Record
        complaint = Complaint(
            ticket_number=ticket_number,
            title=complaint_in.title,
            description=complaint_in.description,
            category=complaint_in.category or (dept.name if dept else "General"),
            priority_level=level,
            priority_score=score,
            priority_factors=factors,
            status=ComplaintStatus.ASSIGNED if dept else ComplaintStatus.SUBMITTED,
            location_address=complaint_in.location_address,
            latitude=complaint_in.latitude,
            longitude=complaint_in.longitude,
            media_urls=complaint_in.media_urls or [],
            citizen_id=citizen_id,
            department_id=dept.id if dept else None,
            is_duplicate=is_dup,
            parent_complaint_id=parent_id,
            duplicate_count=dup_count
        )
        db.add(complaint)
        await db.flush()

        # 5. Create Status History Audit Frame
        history_init = StatusHistory(
            complaint_id=complaint.id,
            previous_status=None,
            new_status=complaint.status.value,
            agent_name="IntakeAndPriorityAgent",
            comment=f"Complaint registered. Assigned Priority {level.value} (Score: {score}). Department: {dept.name if dept else 'Unassigned'}"
        )
        db.add(history_init)

        # 6. Automatic Work Order Generation (if assigned)
        if dept:
            work_order_code = f"WO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
            sla_days = 1 if level == PriorityLevel.P0 else (2 if level == PriorityLevel.P1 else (4 if level == PriorityLevel.P2 else 7))
            
            wo = WorkOrder(
                work_order_code=work_order_code,
                complaint_id=complaint.id,
                priority=level,
                estimated_completion_days=sla_days,
                notes=f"Auto-generated work order for {dept.name}. Priority: {level.value}",
                status=WorkOrderStatus.PENDING
            )
            db.add(wo)

        # 7. Create Citizen Notification
        notif = Notification(
            user_id=citizen_id,
            title=f"Complaint Registered: #{ticket_number}",
            message=f"Your complaint '{complaint_in.title}' has been triaged with Priority {level.value} and assigned to {dept.name if dept else 'Municipal Admin'}.",
            type="COMPLAINT_REGISTERED"
        )
        db.add(notif)

        await db.commit()
        await db.refresh(complaint)

        return complaint
