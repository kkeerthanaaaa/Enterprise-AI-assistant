import uuid
from datetime import date
from pydantic import BaseModel, EmailStr

from app.models.enums import RoleEnum, LeaveType, LeaveStatus


class DepartmentCreate(BaseModel):
    name: str
    code: str | None = None


class DepartmentOut(BaseModel):
    id: uuid.UUID
    name: str
    code: str | None
    class Config:
        from_attributes = True


class EmployeeCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.EMPLOYEE
    department_id: uuid.UUID | None = None
    manager_id: uuid.UUID | None = None
    designation: str | None = None
    date_joined: date | None = None
    notice_period_days: int = 30


class EmployeeOut(BaseModel):
    id: uuid.UUID
    employee_code: str
    full_name: str
    email: EmailStr
    role: RoleEnum
    designation: str | None
    department_id: uuid.UUID | None
    manager_id: uuid.UUID | None
    date_joined: date | None
    probation_end_date: date | None
    notice_period_days: int
    is_active: bool

    class Config:
        from_attributes = True


class LeaveBalanceOut(BaseModel):
    leave_type: LeaveType
    year: int
    entitled_days: float
    used_days: float
    remaining_days: float

    class Config:
        from_attributes = True


class LeaveRequestCreate(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str | None = None


class LeaveRequestOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    leave_type: LeaveType
    start_date: date
    end_date: date
    days_requested: float
    status: LeaveStatus
    reason: str | None

    class Config:
        from_attributes = True


class LeaveDecision(BaseModel):
    approve: bool
    note: str | None = None
