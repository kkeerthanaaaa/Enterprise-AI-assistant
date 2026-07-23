import uuid
from datetime import date, datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Date, Enum as SAEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RoleEnum


class User(Base):
    """A single table serves Employee / Manager / HR / Admin.
    Role is data (RoleEnum), not a separate table, because permissions are
    strictly hierarchical (Manager includes Employee, HR includes Manager, etc.)
    per the spec. This keeps org-chart queries (manager -> reports) simple.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"), nullable=True)

    employee_code: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[RoleEnum] = mapped_column(SAEnum(RoleEnum), default=RoleEnum.EMPLOYEE, nullable=False)
    designation: Mapped[str | None] = mapped_column(String(150), nullable=True)

    manager_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    date_joined: Mapped[date | None] = mapped_column(Date, nullable=True)
    probation_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notice_period_days: Mapped[int] = mapped_column(default=30)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="users")
    department: Mapped["Department"] = relationship(back_populates="users")
    manager: Mapped["User"] = relationship(remote_side=[id], backref="direct_reports")

    leave_balances: Mapped[list["LeaveBalance"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    leave_history: Mapped[list["LeaveRequest"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", foreign_keys="LeaveRequest.user_id"
    )

    __table_args__ = (
        UniqueConstraint("company_id", "email", name="uq_user_company_email"),
        UniqueConstraint("company_id", "employee_code", name="uq_user_company_code"),
    )
