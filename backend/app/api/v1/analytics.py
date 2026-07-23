from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.deps import get_current_user, require_role, CurrentUser
from app.models.enums import RoleEnum, LeaveStatus
from app.models.user import User
from app.models.leave import LeaveRequest
from app.models.document import Document

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", dependencies=[Depends(require_role(RoleEnum.HR))])
def overview(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    total_employees = db.query(func.count(User.id)).filter(User.company_id == current_user.company_id).scalar()
    pending_leaves = (
        db.query(func.count(LeaveRequest.id))
        .filter(LeaveRequest.company_id == current_user.company_id, LeaveRequest.status == LeaveStatus.PENDING)
        .scalar()
    )
    total_documents = (
        db.query(func.count(Document.id))
        .filter(Document.company_id == current_user.company_id, Document.is_active.is_(True))
        .scalar()
    )
    by_role = (
        db.query(User.role, func.count(User.id))
        .filter(User.company_id == current_user.company_id)
        .group_by(User.role)
        .all()
    )
    return {
        "total_employees": total_employees,
        "pending_leave_requests": pending_leaves,
        "total_active_documents": total_documents,
        "headcount_by_role": {role.value: count for role, count in by_role},
    }
