from fastapi import APIRouter
from app.api.v1.endpoints import auth, complaints, work_orders, departments, analytics, ticket

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints Lifecycle"])
api_router.include_router(work_orders.router, prefix="/work-orders", tags=["Work Orders"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Command Center"])
api_router.include_router(ticket.router, prefix="", tags=["Ticket Intelligence & SSE Gateway"])
