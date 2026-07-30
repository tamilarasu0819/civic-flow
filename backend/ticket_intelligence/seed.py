import asyncio
from datetime import datetime, timezone
from sqlalchemy.future import select

from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.complaint import Complaint, PriorityLevel, ComplaintStatus
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.status_history import StatusHistory
from app.models.notification import Notification

async def seed_database():
    print("[+] Recreating database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("[+] Seeding departments...")
        departments_data = [
            {"name": "Roads & Bridges Department", "code": "ROADS", "description": "Maintenance of carriageways, footpaths, bridges, asphalt, and potholes", "head_email": "pwd.head@civicflow.gov", "contact_number": "+1-800-ROADS-01"},
            {"name": "Drainage & Stormwater Department", "code": "DRAINAGE", "description": "Storm drains, sewer lines, effluent overflow, and flood control", "head_email": "drainage.head@civicflow.gov", "contact_number": "+1-800-DRAIN-02"},
            {"name": "Waste Management & Sanitation", "code": "WASTE", "description": "Garbage disposal, illegal dumping, toxic waste, and street sweeping", "head_email": "waste.head@civicflow.gov", "contact_number": "+1-800-WASTE-03"},
            {"name": "Electricity & Street Lighting", "code": "ELECTRICITY", "description": "Transformers, power lines, live wire hazards, and streetlights", "head_email": "power.head@civicflow.gov", "contact_number": "+1-800-POWER-04"},
            {"name": "Public Health & Sanitation", "code": "PUBLIC_HEALTH", "description": "Vector control, epidemic prevention, biological hazards, food safety", "head_email": "health.head@civicflow.gov", "contact_number": "+1-800-HEALTH-05"},
            {"name": "Water Supply & Sewerage Board", "code": "WATER", "description": "Water mains, burst pipes, drinking water quality, sewage connections", "head_email": "water.head@civicflow.gov", "contact_number": "+1-800-WATER-06"},
            {"name": "Parks & Urban Environment", "code": "PARKS", "description": "Fallen trees, urban forestry, parks maintenance, and green spaces", "head_email": "parks.head@civicflow.gov", "contact_number": "+1-800-PARKS-07"},
        ]

        depts = {}
        for d_info in departments_data:
            dept = Department(**d_info)
            db.add(dept)
            await db.flush()
            depts[dept.code] = dept

        print("[+] Seeding users (Admins, Officers, Citizens)...")
        admin = User(
            email="admin@civicflow.gov",
            hashed_password=get_password_hash("admin123"),
            full_name="Chief Administrator",
            role=UserRole.ADMIN,
            phone="+1-555-0100"
        )
        db.add(admin)

        officer1 = User(
            email="officer.pwd@civicflow.gov",
            hashed_password=get_password_hash("officer123"),
            full_name="Senior Engineer - PWD",
            role=UserRole.OFFICER,
            department_id=depts["ROADS"].id,
            phone="+1-555-0101"
        )
        officer2 = User(
            email="officer.power@civicflow.gov",
            hashed_password=get_password_hash("officer123"),
            full_name="Chief Lineman - Power Discom",
            role=UserRole.OFFICER,
            department_id=depts["ELECTRICITY"].id,
            phone="+1-555-0102"
        )
        db.add_all([officer1, officer2])

        citizen1 = User(
            email="citizen.john@gmail.com",
            hashed_password=get_password_hash("citizen123"),
            full_name="John Doe",
            role=UserRole.CITIZEN,
            phone="+1-555-0201"
        )
        citizen2 = User(
            email="citizen.sarah@gmail.com",
            hashed_password=get_password_hash("citizen123"),
            full_name="Sarah Connor",
            role=UserRole.CITIZEN,
            phone="+1-555-0202"
        )
        db.add_all([citizen1, citizen2])
        await db.flush()

        print("[+] Seeding sample complaints (P0, P1, P2, P3)...")
        # 1. P0 Critical Hazard
        c_p0 = Complaint(
            ticket_number="CF-20260730-P001",
            title="EMERGENCY: Fallen Electric Pole with Live Line Exposure on Main Road",
            description="A concrete utility pole has snapped at its base, suspending high-voltage cables less than 2 meters above active traffic lanes.",
            category="Electricity",
            priority_level=PriorityLevel.P0,
            priority_score=92.5,
            priority_factors={"human_safety": 25.0, "affected_citizens": 15.0, "vulnerable_groups": 15.0, "traffic_disruption": 15.0, "environmental_impact": 2.0, "infrastructure_damage": 10.0, "complaint_age": 0.0, "duplicate_count": 3.0},
            status=ComplaintStatus.IN_PROGRESS,
            location_address="Intersection of 5th Main & 12th Cross, Downtown",
            latitude=37.7749,
            longitude=-122.4194,
            media_urls=["http://storage.civicflow.gov/media/pole_snapped_01.jpg"],
            citizen_id=citizen1.id,
            department_id=depts["ELECTRICITY"].id,
            ai_analysis={"detected_objects": ["fallen pole", "high voltage line", "snapped concrete"], "gemma_summary": "P0 Critical electrical hazard requiring immediate SCADA grid isolation.", "confidence_score": 0.98}
        )
        db.add(c_p0)

        # 2. P1 High Urgent
        c_p1 = Complaint(
            ticket_number="CF-20260730-P101",
            title="Major Sewer Line Burst Inundating Primary Carriageway",
            description="Untreated wastewater overflowing from main sewer line, covering 50% of traffic lane and creating severe odor.",
            category="Drainage",
            priority_level=PriorityLevel.P1,
            priority_score=74.0,
            priority_factors={"human_safety": 15.0, "affected_citizens": 12.0, "vulnerable_groups": 15.0, "traffic_disruption": 15.0, "environmental_impact": 10.0, "infrastructure_damage": 7.0, "complaint_age": 0.0, "duplicate_count": 0.0},
            status=ComplaintStatus.ASSIGNED,
            location_address="78 Hospital Road, Medical District",
            latitude=37.7833,
            longitude=-122.4167,
            media_urls=["http://storage.civicflow.gov/media/sewer_burst.jpg"],
            citizen_id=citizen2.id,
            department_id=depts["DRAINAGE"].id
        )
        db.add(c_p1)

        # 3. P2 Medium Standard Maintenance
        c_p2 = Complaint(
            ticket_number="CF-20260730-P201",
            title="Deep Pothole on Residential Footpath Lane",
            description="Asphalt depression approximately 15cm deep posing tripping hazard to pedestrians.",
            category="Roads",
            priority_level=PriorityLevel.P2,
            priority_score=45.0,
            priority_factors={"human_safety": 5.0, "affected_citizens": 8.0, "vulnerable_groups": 3.0, "traffic_disruption": 8.0, "environmental_impact": 2.0, "infrastructure_damage": 4.0, "complaint_age": 0.0, "duplicate_count": 0.0},
            status=ComplaintStatus.SUBMITTED,
            location_address="142 Oak Lane, Suburbia",
            latitude=37.7600,
            longitude=-122.4400,
            citizen_id=citizen1.id,
            department_id=depts["ROADS"].id
        )
        db.add(c_p2)

        # 4. P3 Low Routine
        c_p3 = Complaint(
            ticket_number="CF-20260730-P301",
            title="Minor Garbage Littering Near Public Park Bench",
            description="Uncollected paper wrappings and plastic cups scattered near park entrance.",
            category="Waste Management",
            priority_level=PriorityLevel.P3,
            priority_score=22.0,
            priority_factors={"human_safety": 5.0, "affected_citizens": 4.0, "vulnerable_groups": 3.0, "traffic_disruption": 3.0, "environmental_impact": 3.0, "infrastructure_damage": 0.0, "complaint_age": 0.0, "duplicate_count": 0.0},
            status=ComplaintStatus.RESOLVED,
            location_address="Central Community Park",
            latitude=37.7500,
            longitude=-122.4300,
            citizen_id=citizen2.id,
            department_id=depts["WASTE"].id
        )
        db.add(c_p3)

        await db.flush()

        print("[+] Seeding work orders & notifications...")
        wo_p0 = WorkOrder(
            work_order_code="WO-20260730-ELEC01",
            complaint_id=c_p0.id,
            assigned_officer_id=officer2.id,
            priority=PriorityLevel.P0,
            estimated_completion_days=1,
            notes="Emergency dispatch: SCADA Feeder line 4B de-energized. Crane squad en route.",
            status=WorkOrderStatus.IN_PROGRESS
        )
        db.add(wo_p0)

        history_p0 = StatusHistory(
            complaint_id=c_p0.id,
            previous_status="SUBMITTED",
            new_status="IN_PROGRESS",
            changed_by_user_id=officer2.id,
            agent_name="PriorityScoringAgent & Officer",
            comment="Elevated to P0 Emergency. Work order WO-20260730-ELEC01 dispatched."
        )
        db.add(history_p0)

        notif_p0 = Notification(
            user_id=citizen1.id,
            title="Emergency Priority P0 Escalation",
            message="Your report regarding the fallen electric pole was rated P0 Critical. Emergency crew dispatched.",
            type="PRIORITY_ALERT"
        )
        db.add(notif_p0)

        await db.commit()
        print("[+] Database seeding complete! Run main server or test suite now.")

if __name__ == "__main__":
    asyncio.run(seed_database())
