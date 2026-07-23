import uuid
from datetime import date, datetime
from sqlalchemy import String, DateTime, ForeignKey, Date, Integer, Numeric, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import LeaveType, LeaveStatus


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    leave_type: Mapped[LeaveType] = mapped_column(SAEnum(LeaveType), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    entitled_days: Mapped[float] = mapped_column(Numeric(5, 1), default=0)
    used_days: Mapped[float] = mapped_column(Numeric(5, 1), default=0)

    user: Mapped["User"] = relationship(back_populates="leave_balances")

    @property
    def remaining_days(self) -> float:
        return float(self.entitled_days) - float(self.used_days)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    leave_type: Mapped[LeaveType] = mapped_column(SAEnum(LeaveType), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_requested: Mapped[float] = mapped_column(Numeric(5, 1), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[LeaveStatus] = mapped_column(SAEnum(LeaveStatus), default=LeaveStatus.PENDING)
    decided_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="leave_history", foreign_keys=[user_id])
