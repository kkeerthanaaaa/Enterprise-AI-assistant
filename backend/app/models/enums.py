import enum


class RoleEnum(str, enum.Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr"
    ADMIN = "admin"


# Role hierarchy used for "X can do everything Y can do" checks
ROLE_LEVEL = {
    RoleEnum.EMPLOYEE: 1,
    RoleEnum.MANAGER: 2,
    RoleEnum.HR: 3,
    RoleEnum.ADMIN: 4,
}


class LeaveType(str, enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    UNPAID = "unpaid"
    WFH = "wfh"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DocumentType(str, enum.Enum):
    HANDBOOK = "handbook"
    HR_POLICY = "hr_policy"
    IT_POLICY = "it_policy"
    TRAVEL_POLICY = "travel_policy"
    LEAVE_POLICY = "leave_policy"
    PAYROLL_POLICY = "payroll_policy"
    INSURANCE = "insurance"
    BENEFITS = "benefits"
    SECURITY_POLICY = "security_policy"
    SOP = "sop"
    TRAINING_MANUAL = "training_manual"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    ARCHIVED = "archived"
