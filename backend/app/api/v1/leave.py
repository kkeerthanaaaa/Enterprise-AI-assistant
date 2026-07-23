import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.deps import get_current_user, require_role, CurrentUser
from app.models.enums import RoleEnum, LeaveStatus
from app.models.user import User
from app.models.leave import LeaveBalance, LeaveRequest
from app.schemas.employee import LeaveBalanceOut, LeaveRequestCreate, LeaveRequestOut, LeaveDecision
from app.ai.rules.leave_rules import evaluate_leave_request

router = APIRouter(prefix="/leave", tags=["leave"])


@router.get("/balance", response_model=list[LeaveBalanceOut])
def my_balance(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    year = datetime.utcnow().year
    balances = (
        db.query(LeaveBalance)
        .filter(LeaveBalance.user_id == current_user.id, LeaveBalance.company_id == current_user.company_id, LeaveBalance.year == year)
        .all()
    )
    return [
        LeaveBalanceOut(
            leave_type=b.leave_type,
            year=b.year,
            entitled_days=float(b.entitled_days),
            used_days=float(b.used_days),
            remaining_days=b.remaining_days,
        )
        for b in balances
    ]


@router.post("/request", response_model=LeaveRequestOut)
def request_leave(payload: LeaveRequestCreate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    evaluation = evaluate_leave_request(
        db, current_user.company_id, current_user.id, payload.leave_type, payload.start_date, payload.end_date
    )
    if evaluation.recommendation == "reject":
        raise HTTPException(status_code=400, detail="Insufficient leave balance for this request")

    leave_request = LeaveRequest(
        id=uuid.uuid4(),
        company_id=current_user.company_id,
        user_id=current_user.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days_requested=evaluation.days_requested,
        reason=payload.reason,
        status=LeaveStatus.PENDING,
    )
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)
    return leave_request


@router.get("/history", response_model=list[LeaveRequestOut])
def my_history(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    return (
        db.query(LeaveRequest)
        .filter(LeaveRequest.user_id == current_user.id, LeaveRequest.company_id == current_user.company_id)
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )


@router.get("/team-history/{employee_id}", response_model=list[LeaveRequestOut], dependencies=[Depends(require_role(RoleEnum.MANAGER))])
def team_member_history(employee_id: uuid.UUID, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    employee = db.query(User).filter(User.id == employee_id, User.company_id == current_user.company_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if employee.manager_id != current_user.id and current_user.role not in (RoleEnum.HR, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail="Not this employee's manager")
    return (
        db.query(LeaveRequest)
        .filter(LeaveRequest.user_id == employee_id, LeaveRequest.company_id == current_user.company_id)
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )


@router.post("/{request_id}/decide", response_model=LeaveRequestOut, dependencies=[Depends(require_role(RoleEnum.MANAGER))])
def decide_leave(request_id: uuid.UUID, payload: LeaveDecision, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    leave_request = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.id == request_id, LeaveRequest.company_id == current_user.company_id)
        .first()
    )
    if not leave_request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    employee = db.query(User).filter(User.id == leave_request.user_id).first()
    if employee.manager_id != current_user.id and current_user.role not in (RoleEnum.HR, RoleEnum.ADMIN):
        raise HTTPException(status_code=403, detail="Only the employee's manager (or HR/Admin) can decide this request")

    leave_request.status = LeaveStatus.APPROVED if payload.approve else LeaveStatus.REJECTED
    leave_request.decided_by = current_user.id
    leave_request.decision_note = payload.note
    leave_request.decided_at = datetime.utcnow()

    if payload.approve:
        year = leave_request.start_date.year
        balance = (
            db.query(LeaveBalance)
            .filter(
                LeaveBalance.user_id == employee.id,
                LeaveBalance.company_id == current_user.company_id,
                LeaveBalance.leave_type == leave_request.leave_type,
                LeaveBalance.year == year,
            )
            .first()
        )
        if balance:
            balance.used_days = float(balance.used_days) + float(leave_request.days_requested)

    db.commit()
    db.refresh(leave_request)
    return leave_request
