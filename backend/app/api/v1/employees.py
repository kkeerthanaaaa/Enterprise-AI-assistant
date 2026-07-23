import uuid
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.deps import get_current_user, require_role, assert_same_company, CurrentUser
from app.models.enums import RoleEnum
from app.models.user import User
from app.models.training import Training
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.core.security import hash_password

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/me", response_model=EmployeeOut)
def get_my_profile(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user


@router.get("/team", response_model=list[EmployeeOut], dependencies=[Depends(require_role(RoleEnum.MANAGER))])
def get_my_team(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    """Manager+ only. Returns direct reports within the same company."""
    return (
        db.query(User)
        .filter(User.manager_id == current_user.id, User.company_id == current_user.company_id)
        .all()
    )


@router.get("", response_model=list[EmployeeOut], dependencies=[Depends(require_role(RoleEnum.HR))])
def list_employees(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    """HR+ only. Full roster for the tenant."""
    return db.query(User).filter(User.company_id == current_user.company_id).all()


@router.post("", response_model=EmployeeOut, dependencies=[Depends(require_role(RoleEnum.ADMIN))])
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    existing = db.query(User).filter(User.company_id == current_user.company_id, User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use for this company")

    count = db.query(User).filter(User.company_id == current_user.company_id).count()
    employee_code = f"EMP-{count + 1:04d}"

    probation_end = None
    if payload.date_joined:
        probation_end = payload.date_joined + timedelta(days=90)

    user = User(
        id=uuid.uuid4(),
        company_id=current_user.company_id,
        employee_code=employee_code,
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        department_id=payload.department_id,
        manager_id=payload.manager_id,
        designation=payload.designation,
        date_joined=payload.date_joined,
        probation_end_date=probation_end,
        notice_period_days=payload.notice_period_days,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/probation-ending-this-month", response_model=list[EmployeeOut], dependencies=[Depends(require_role(RoleEnum.HR))])
def probation_ending_this_month(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    today = date.today()
    start = today.replace(day=1)
    if today.month == 12:
        end = date(today.year + 1, 1, 1)
    else:
        end = date(today.year, today.month + 1, 1)
    return (
        db.query(User)
        .filter(User.company_id == current_user.company_id, User.probation_end_date >= start, User.probation_end_date < end)
        .all()
    )


@router.get("/training-incomplete", dependencies=[Depends(require_role(RoleEnum.HR))])
def training_incomplete(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    rows = (
        db.query(Training, User)
        .join(User, User.id == Training.user_id)
        .filter(Training.company_id == current_user.company_id, Training.is_mandatory.is_(True), Training.completed.is_(False))
        .all()
    )
    return [
        {"employee": t_user.full_name, "training": t.training_name, "due_date": t.due_date}
        for t, t_user in rows
    ]
