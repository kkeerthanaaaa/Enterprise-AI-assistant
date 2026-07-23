from fastapi import APIRouter

from app.api.v1 import auth, employees, departments, leave, documents, chat, analytics

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(employees.router)
api_router.include_router(departments.router)
api_router.include_router(leave.router)
api_router.include_router(documents.router)
api_router.include_router(chat.router)
api_router.include_router(analytics.router)
