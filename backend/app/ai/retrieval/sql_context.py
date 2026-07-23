import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.leave import LeaveBalance, LeaveRequest
from app.models.training import Training
from app.core.deps import CurrentUser


def get_employee_sql_context(db: Session, current_user: CurrentUser) -> dict:
    """Structured facts about the asking user: their own record, manager,
    leave balances, recent leave history. Always scoped to company_id +
    the user's own id -- an Employee can never pull another employee's row
    through this path (that's what elevated role-specific queries below are
    for, gated by RBAC at the API layer)."""

    user = (
        db.query(User)
        .filter(User.id == current_user.id, User.company_id == current_user.company_id)
        .first()
    )
    if not user:
        return {}

    year = datetime.utcnow().year
    balances = (
        db.query(LeaveBalance)
        .filter(
            LeaveBalance.user_id == user.id,
            LeaveBalance.company_id == current_user.company_id,
            LeaveBalance.year == year,
        )
        .all()
    )
    recent_requests = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.user_id == user.id, LeaveRequest.company_id == current_user.company_id)
        .order_by(LeaveRequest.created_at.desc())
        .limit(5)
        .all()
    )
    manager = db.query(User).filter(User.id == user.manager_id).first() if user.manager_id else None

    return {
        "employee": {
            "full_name": user.full_name,
            "employee_code": user.employee_code,
            "designation": user.designation,
            "department_id": str(user.department_id) if user.department_id else None,
            "date_joined": str(user.date_joined) if user.date_joined else None,
            "notice_period_days": user.notice_period_days,
            "manager_name": manager.full_name if manager else None,
        },
        "leave_balances": [
            {
                "leave_type": b.leave_type.value,
                "entitled": float(b.entitled_days),
                "used": float(b.used_days),
                "remaining": b.remaining_days,
            }
            for b in balances
        ],
        "recent_leave_requests": [
            {
                "leave_type": r.leave_type.value,
                "start_date": str(r.start_date),
                "end_date": str(r.end_date),
                "days": float(r.days_requested),
                "status": r.status.value,
            }
            for r in recent_requests
        ],
    }


def get_direct_reports_context(db: Session, current_user: CurrentUser) -> dict:
    """Manager-scoped context: only direct reports within the same company."""
    reports = (
        db.query(User)
        .filter(User.manager_id == current_user.id, User.company_id == current_user.company_id)
        .all()
    )
    return {
        "direct_reports": [
            {"id": str(r.id), "full_name": r.full_name, "designation": r.designation}
            for r in reports
        ]
    }


def get_employee_by_name_scoped(db: Session, current_user: CurrentUser, name: str) -> User | None:
    """Look up a named employee (e.g. 'John') strictly inside the caller's
    company, and only usable by Manager+ roles at the API layer."""
    return (
        db.query(User)
        .filter(User.company_id == current_user.company_id, User.full_name.ilike(f"%{name}%"))
        .first()
    )
